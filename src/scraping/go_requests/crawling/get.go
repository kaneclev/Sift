package get

import (
	"fmt"
	"math"
	"math/rand"
	"os"
	"siftrequests/ipc"
	"strconv"
	"sync"

	"github.com/projectdiscovery/gologger"
	"github.com/projectdiscovery/katana/pkg/engine/standard"
	"github.com/projectdiscovery/katana/pkg/output"
	"github.com/projectdiscovery/katana/pkg/types"
)

func GetMaxNumProxies() int {
	max_num := os.Getenv("MAX_PROXIES")
	if max_num == "" {
		fmt.Printf("\n(!) Can't find field 'MAX_PROXIES' in the environment.")
		return -1
	}
	max_num_int, err := strconv.Atoi(max_num)
	if err != nil {
		fmt.Printf("\nCannot convert 'MAX_PROXIES' to an integer; given str to convert: %s, error: %s\n", max_num, err.Error())
		return -1
	}
	return max_num_int
}

func GetProxies(num int) []string {
	prox_prepend := "PROX"
	if num < 0 {
		num = GetMaxNumProxies()
		if num < 0 {
			return nil
		}
	}
	proxlist := make([]string, num)
	for i := range num {
		if i == 0 {
			continue
		}
		currproxstring := prox_prepend + strconv.Itoa(i)
		prox := os.Getenv(currproxstring)
		if len(prox) == 0 {
			fmt.Printf("\n Warning: no proxy associated with key %s\n", currproxstring)
			continue
		}
		proxlist = append(proxlist, prox)
	}
	return proxlist
}

func GetRandProxy(plist []string) string {
	// Generate a random integer [0..99].
	randomInt := rand.Intn(len(plist))
	return plist[randomInt]
}

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

func DefineCrawlerBehavior(url_alias_container *ipc.RCollection, proxy, response_dir, engine string) *types.Options {
	if url_alias_container == nil {
		fmt.Printf("\nCannot instantiate options for a crawler when the url_alias_container is nil (no urls to crawl)\n")
		return nil
	}
	if engine == "" {
		engine = "rod"
	}

	if proxy == "" {

		proxy_options := GetProxies(-1)
		if proxy_options != nil {
			proxy = GetRandProxy(proxy_options)
		} else {
			return nil
		}
	}
	parallel_limit := getParalellLimit()
	if parallel_limit < 0 {
		return nil
	}
	defined_opts := &types.Options{
		URLs:                url_alias_container.GetURLs(),
		Proxy:               proxy,
		Strategy:            "depth-first",
		BodyReadSize:        math.MaxInt,
		Timeout:             10,
		Parallelism:         parallel_limit,
		RateLimit:           150,
		Headless:            true,
		Silent:              true,
		HeadlessNoIncognito: true,
		TechDetect:          true,
		XhrExtraction:       true,
	}

	fmt.Printf("\nDefined options. \n")
	return defined_opts
}

type ResponseMetaWrapper struct {
	RequesterFilename string
	Alias             string
}

func GetContent(options *types.Options, requester_filename string, collection *ipc.RCollection, on_results types.OnResultCallback) {
	wrapper := ResponseMetaWrapper{
		RequesterFilename: requester_filename,
		Alias:             "",
	}
	if on_results == nil {
		options.OnResult = wrapper.contentReceiver
	} else {
		options.OnResult = on_results
	}
	options.ConfigureOutput()
	crawlerOptions, crawlopterror := types.NewCrawlerOptions(options)
	if crawlopterror != nil {
		fmt.Printf("\nCannot instantiate crawler options  due to unexpected error: %s \n", crawlopterror.Error())
		return
	}
	defer crawlerOptions.Close()
	crawler, err := standard.New(crawlerOptions)
	if err != nil {
		gologger.Fatal().Msg(err.Error())
	}
	defer crawler.Close()
	var wg sync.WaitGroup
	// TODO: Implement the parallel limit here to avoid running an exceeding num of requests.
	for _, url := range options.URLs {
		wg.Add(1)
		go func(u string) {
			defer wg.Done()
			wrapper.Alias = collection.GetAliasByURL(u)

			err := crawler.Crawl(u)
			if err != nil {
				gologger.Warning().Msgf("Error crawling %s: %v", u, err)
			}
		}(url)
	}
	wg.Wait()
}

/*
TODO:
  - OFFER OTHER WAYS OF COMMUNICATING THE RESULT BEYOND JUST SAVING AS JSON.
  - This could be implemented as multiple functions for on_results, and they are called differently depending on the
  - args passed to this executable.
*/
func (meta_wrapper *ResponseMetaWrapper) contentReceiver(content output.Result) {
	if !content.HasResponse() {
		fmt.Printf("\nCouldn't resolve a response for %s\n", content.Request.URL)
		return
	}

	fmt.Printf("\nResult recieved at %s\n", content.Timestamp.String())
	if content.Error != "" {
		fmt.Printf("\nError in result: %s\n", content.Error)
	}

	// Perform the parse
	parsedResp, err := ParseResponse(content.Response, meta_wrapper.Alias)
	if err != nil {
		fmt.Printf("parseResponse error: %v\n", err)
		return
	}
	outFile := ipc.GetReturnJSONFilename(meta_wrapper.RequesterFilename)
	// (Optional) Save the structured result to disk
	if err := SaveParsedResponseToFile(parsedResp, outFile); err != nil {
		fmt.Printf("Error saving parsed response: %v\n", err)
	}
}
