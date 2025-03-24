package main

import (
	"fmt"
	"os"
	get "siftrequests/crawling"
	"siftrequests/ipc"
)

var ENVRELPATH = "./.env"

func main() {
	setup_success := load_env()
	if !setup_success {
		return
	}

	// TODO: this aggregates requests from multiple files, but then saves them all under a single filename
	beginScraping(&requests_encoding_collection, outfile)

}

func beginScraping(collection_to_use *ipc.RCollection, outfile string) {
	options := get.DefineCrawlerBehavior(collection_to_use, "", "", "")
	// todo: nil will have to change to different callable response handlers as we expand the number of ways to communicate back to the caller.
	consumer.ListenRCollectionsFromRabbitMQ(options, outfile, collection_to_use, nil)
}

func load_env() bool {
	cwd, err := os.Getwd()
	if err != nil {
		fmt.Println("Error getting current working directory:", err)
		return false
	}
	fmt.Println("Current working directory:", cwd)
	defineEnvironment(ENVRELPATH)
	return true
}
