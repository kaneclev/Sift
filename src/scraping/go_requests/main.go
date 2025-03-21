package main

import (
	"fmt"
	"os"
	get "siftrequests/crawling"
	"siftrequests/ipc"
)

var ENVRELPATH = "./.env"

func main() {
	// get program arguments
	args := os.Args[1:]
	setup_success := setup(args)
	if !setup_success {
		return
	}
	requests_encoding_collection, outfile := getRequests()
	if len(requests_encoding_collection.Requests) == 0 {
		fmt.Printf("\nThere were no requests found.\n")
		return
	}
	for i, req := range requests_encoding_collection.Requests {
		fmt.Printf("\nRequest %d: URL=%s, Alias=%s\n", i, req.URL, req.Alias)
	}
	// TODO: this aggregates requests from multiple files, but then saves them all under a single filename
	beginScraping(&requests_encoding_collection, outfile)

}

func beginScraping(collection_to_use *ipc.RCollection, outfile string) {
	options := get.DefineCrawlerBehavior(collection_to_use, "", "", "")
	// todo: nil will have to change to different callable response handlers as we expand the number of ways to communicate back to the caller.
	get.GetContent(options, outfile, collection_to_use, nil)
}

func getRequests() (ipc.RCollection, string) {
	location := os.Getenv("REQUEST_COM") + "/Sent"
	file := os.Getenv("finput")
	outfile := os.Getenv("fout")
	match_type := os.Getenv("match-type")
	if len(match_type) == 0 {
		fmt.Println("\nA match type for the request collection must be specified using --match-type (options: loose, strict)")
		return ipc.RCollection{}, ""
	}

	// & is creating a pointer to the new RCollection instance which the FindRequests method needs in order to modify the RCollection instance
	request_container := &ipc.RCollection{}

	request_container.FindRequests(file, location, match_type)
	return *request_container, outfile
}

func setup(args []string) bool {
	success := argHandler(args)
	if !success {
		fmt.Println("Couldn't register args. Discontinuing run. ")
		return false
	}
	cwd, err := os.Getwd()
	if err != nil {
		fmt.Println("Error getting current working directory:", err)
		return false
	}
	fmt.Println("Current working directory:", cwd)
	defineEnvironment(ENVRELPATH)
	return true
}
