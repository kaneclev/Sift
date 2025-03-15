package main

import (
	"fmt"
	"os"
)

var ENVRELPATH = "./.env"

func main() {
	// get program arguments
	args := os.Args[1:]
	success := argHandler(args)
	if !success {
		fmt.Println("Couldn't register args. Discontinuing run. ")
		return
	}
	cwd, err := os.Getwd()
	if err != nil {
		fmt.Println("Error getting current working directory:", err)
		return
	}
	fmt.Println("Current working directory:", cwd)
	defineEnvironment(ENVRELPATH)
}
