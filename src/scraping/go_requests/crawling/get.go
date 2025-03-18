package get

import (
	"fmt"
	"math"
	"math/rand"
	"os"
	"siftrequests/ipc"
	"strconv"

	"github.com/projectdiscovery/gologger"
	"github.com/projectdiscovery/katana/pkg/engine/standard"
	"github.com/projectdiscovery/katana/pkg/types"
)

func GetProxies(num int) []string {
	prox_prepend := "PROX"

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

func defineCrawlerBehavior(engine string, url_alias_container *ipc.RCollection) *types.Options {
	if engine == "" {
		engine = "rod"
	}
	env_par_limit := os.Getenv("PARALELL_LIMIT")
	if len(env_par_limit) == 0 {
		fmt.Printf("\nExpected PARALLEL_LIMIT to be defined in the environment, but it can't be found. Discontinuing.\n")
	}
	parallel_limit, atoierror := strconv.Atoi(env_par_limit)
	if atoierror != nil {
		fmt.Printf("\n The value for PARALLEL_LIMIT read in from the environment could not be understood as an integer (reason: %s). Discontinuing. ", atoierror.Error())
	}
	return &types.Options{
		MaxDepth:     3,
		BodyReadSize: math.MaxInt,
		Timeout:      10,
		Parallelism:  parallel_limit,
		RateLimit:    150,
	}

}
func getContent(options *types.Options, proxy string) {
	if proxy != "" {
		options.Proxy = proxy
	}
	crawlerOptions, crawlopterror := types.NewCrawlerOptions(options)
	if crawlopterror != nil {
		fmt.Printf("\nCannot instantiate crawler options for calling url %s, due to unexpected error: %s \n", url, crawlopterror.Error())
		return
	}
	defer crawlerOptions.Close()
	crawler, err := standard.New(crawlerOptions)
	if err != nil {
		gologger.Fatal().Msg(err.Error())
	}
	defer crawler.Close()

	err = crawler.Crawl(url)
	if err != nil {
		gologger.Warning().Msgf("Could not crawl %s: %s", input, err.Error())
	}
}
