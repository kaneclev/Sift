package main

import (
	"fmt"
	"os"
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
	requests_encoding_collection := getRequests()
	if len(requests_encoding_collection.Requests) == 0 {
		fmt.Println("There were no requests found.")
		return
	}
	for i, req := range requests_encoding_collection.Requests {
		fmt.Printf("\nRequest %d: URL=%s, Alias=%s\n", i, req.URL, req.Alias)
	}
}

func getRequests() ipc.RCollection {
	location := os.Getenv("REQUEST_COM")
	file := os.Getenv("finput")
	match_type := os.Getenv("match-type")
	if len(match_type) == 0 {
		fmt.Println("\nA match type for the request collection must be specified using --match-type (options: loose, strict)")
		return ipc.RCollection{}
	}

	// & is creating a pointer to the new RCollection instance which the FindRequests method needs in order to modify the RCollection instance
	request_container := &ipc.RCollection{}

	request_container.FindRequests(file, location, match_type)
	return *request_container
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
