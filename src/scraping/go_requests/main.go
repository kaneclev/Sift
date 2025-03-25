package main

import (
	"fmt"
	"os"
	"siftrequests/ipc"
)

var ENVRELPATH = "./.env"

func main() {
	setup_success := load_env()
	if !setup_success {
		return
	}
	fmt.Printf("\n PRENIS")
	connStr := os.Getenv("RABBITMQ_GOREQUESTS_CONNSTRING")
	queueName := os.Getenv("RABBITMQ_PARSE_REQUEST_QUEUENAME")
	if len(connStr) == 0 {
		fmt.Printf("\nNo connection string was found in the environment for RabbitMQ.\n")
		return
	}
	ipc.ListenForTargets(connStr, queueName)

	// TODO: this aggregates requests from multiple files, but then saves them all under a single filename

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
