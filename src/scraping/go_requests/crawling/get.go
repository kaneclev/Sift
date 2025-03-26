package get

import (
	"fmt"
	"math"
	"os"
	"siftrequests/ipc_structs"
	utils "siftrequests/utils"
	"strconv"
	"sync"

	"github.com/projectdiscovery/katana/pkg/engine/standard"
	"github.com/projectdiscovery/katana/pkg/output"
	"github.com/projectdiscovery/katana/pkg/types"
)

func getParalellLimit() int {
	env_par_limit := os.Getenv("PARALELL_LIMIT")
	if len(env_par_limit) == 0 {
		fmt.Printf("\nExpected PARALLEL_LIMIT to be defined in the environment, but it can't be found. Discontinuing.\n")
	}
	parallel_limit, atoierror := strconv.Atoi(env_par_limit)
	if atoierror != nil {
		fmt.Printf("\n The value for PARALLEL_LIMIT read in from the environment could not be understood as an integer (reason: %s). Discontinuing. ", atoierror.Error())
		return -1
	}
	return parallel_limit
}

func DefineCrawlerBehavior(url_alias_container *ipc_structs.Targets, response_dir, engine string) *types.Options {
	if url_alias_container == nil {
		fmt.Printf("\nCannot instantiate options for a crawler when the url_alias_container is nil (no urls to crawl)\n")
		return nil
	}
	if engine == "" {
		engine = "rod"
	}

	parallel_limit := getParalellLimit()
	if parallel_limit < 0 {
		return nil
	}
	defined_opts := &types.Options{
		URLs:                   url_alias_container.GetURLs(),
		Strategy:               "depth-first",
		Verbose:                true,
		BodyReadSize:           math.MaxInt,
		Timeout:                10,
		Parallelism:            parallel_limit,
		RateLimit:              150,
		Headless:               true,
		ShowBrowser:            true,
		TechDetect:             true,
		XhrExtraction:          true,
		AutomaticFormFill:      true,
		FormExtraction:         true,
		ScrapeJSResponses:      true,
		ScrapeJSLuiceResponses: true,
		Delay:                  2,
	}

	fmt.Printf("\nDefined options. \n")
	return defined_opts
}

type ReceivedContent struct {
	URL           string
	Alias         string
	CorrelationID string
	Response      ParsedResponse
}

func GetContent(options *types.Options, targets *ipc_structs.Targets) chan ReceivedContent {
	options.ConfigureOutput()

	// Create a queue of items to process
	request_queue := make([]ReceivedContent, 0, len(targets.Targets))
	for _, targ := range targets.Targets {
		request_queue = utils.Push(request_queue, ReceivedContent{
			URL:           targ.URL,
			Alias:         targ.Alias,
			CorrelationID: targets.CorrelationID,
			Response:      ParsedResponse{},
		})
	}

	numWorkers := options.Parallelism

	// Create channels for worker coordination
	jobs := make(chan ReceivedContent, len(request_queue))
	results := make(chan ReceivedContent, len(request_queue))

	// Create a wait group to wait for all workers to finish
	var wg sync.WaitGroup

	// Start workers
	for i := 0; i < numWorkers; i++ {
		wg.Add(1)
		go worker(i, options, jobs, results, &wg)
	}

	// Send jobs to workers
	go func() {
		for _, item := range request_queue {
			jobs <- item
		}
		close(jobs) // Close jobs channel when all jobs are sent
	}()

	// Collect results in a separate goroutine
	go func() {
		wg.Wait()      // Wait for all workers to finish
		close(results) // Close results channel when all workers are done
	}()

	// return the results channel. This channel returned is NOT expected to contain all of the results yet; the caller will get the channel, and will see it gradually fill.
	return results
}

func worker(id int, options *types.Options, jobs <-chan ReceivedContent, results chan<- ReceivedContent, wg *sync.WaitGroup) {
	defer wg.Done()

	for job := range jobs {
		fmt.Printf("\nWorker %d processing URL: %s\n", id, job.URL)

		// Create a copy of options for this specific job
		jobOptions := *options

		// Set the content receiver for this job
		jobOptions.OnResult = func(content output.Result) {
			if !content.HasResponse() {
				fmt.Printf("\nWorker %d: Couldn't resolve a response for %s\n", id, content.Request.URL)
				return
			}

			fmt.Printf("\nWorker %d: Result received at %s\n", id, content.Timestamp.String())
			if content.Error != "" {
				fmt.Printf("\nWorker %d: Error in result: %s\n", id, content.Error)
			}

			// Perform the parse
			parsedResp, err := ParseResponse(content.Response, job.Alias, job.CorrelationID)
			if err != nil {
				fmt.Printf("\nWorker %d: parseResponse error: %v\n", id, err)
				return
			}

			job.Response = parsedResp
			fmt.Printf("\nWorker %d: Found response with length %d bytes\n", id, len(parsedResp.BodyInfo.Text))

			// Send the completed job to results channel
			results <- job
		}

		// Get a proxy for this job
		proxy_list := utils.GetProxies(-1)
		if proxy_list != nil {
			proxy := utils.GetRandProxy(proxy_list)
			if len(proxy) == 0 {
				fmt.Printf("\nWorker %d: While there were proxies found, no random proxy was available... Continuing\n", id)
			}
			jobOptions.Proxy = proxy
		} else {
			fmt.Printf("\nWorker %d: No proxies available for some reason... Continuing\n", id)
			continue
		}

		// Create crawler options
		crawlerOptions, crawlopterror := types.NewCrawlerOptions(&jobOptions)
		if crawlopterror != nil {
			fmt.Printf("\nWorker %d: Cannot instantiate crawler options due to unexpected error: %s\n", id, crawlopterror.Error())
			continue
		}

		// Create crawler
		crawler, err := standard.New(crawlerOptions)
		if err != nil {
			fmt.Printf("\nWorker %d: Error creating crawler: %s\n", id, err.Error())
			continue
		}

		// Crawl the URL
		crawl_err := crawler.Crawl(job.URL)
		if crawl_err != nil {
			fmt.Printf("\nWorker %d: Error crawling %s: %v\n", id, job.URL, crawl_err)
		}

		crawlerOptions.Close()
	}
}
