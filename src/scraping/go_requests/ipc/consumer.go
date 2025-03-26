package ipc

import (
	"encoding/json"
	"fmt"
	"log"
	"os"
	get "siftrequests/crawling"
	"siftrequests/ipc_structs"

	"github.com/wagslane/go-rabbitmq"
)

func ListenForTargets(connStr, queueName string) error {
	// Establish a connection to RabbitMQ.
	conn, err := rabbitmq.NewConn(connStr, rabbitmq.WithConnectionOptionsLogging)
	if err != nil {
		return err
	}
	// Note: We intentionally do not defer conn.Close() here because we want to keep it open.

	// Create a new consumer for the specified queue.
	consumer, err := rabbitmq.NewConsumer(
		conn,
		queueName,
		rabbitmq.WithConsumerOptionsQueueDurable,
		rabbitmq.WithConsumerOptionsConcurrency(5),
	)
	fmt.Printf("\nNew consumer: %s", queueName)
	if err != nil {
		fmt.Printf("\nError when making connection: %s\n", err.Error())
		conn.Close()
		return err
	}
	debug_flag := os.Getenv("REQUESTER_DEBUG")
	var is_debug = false
	if debug_flag == "1" {
		is_debug = true
	}

	parsedResultChan := make(chan get.ReceivedContent)
	go func() {
		if is_debug {
			for result := range parsedResultChan {
				fmt.Printf("\n[Writer] Received result for %s", result.Alias)
				file := "bin/request_collections/" + result.Alias + ".json"
				wd, _ := os.Getwd()
				fmt.Printf("\n%s\n", wd)
				err := WriteParsedResponseToFile(result.Response, file)
				if err != nil {
					fmt.Printf("Error writing result: %v\n", err)
				}

			}
		}
	}()

	// Call consumer.Run directly. This call will block and continuously wait for new messages.
	err = consumer.Run(func(d rabbitmq.Delivery) rabbitmq.Action {
		fmt.Println("[Handler] New message received")
		targets, err := ipc_structs.UnmarshalTargets(d.Body)
		if err != nil {
			fmt.Println("Unmarshal error:", err)
			return rabbitmq.NackDiscard
		}

		crawlerOpts := get.DefineCrawlerBehavior(targets, "", "")
		results := get.GetContent(crawlerOpts, targets)

		// Forward each result to the outer channel
		go func() {
			for result := range results {
				parsedResultChan <- result
			}
		}()

		return rabbitmq.Ack
	})

	if err != nil {
		log.Printf("consumer run error: %v", err)
	}

	// If consumer.Run exits, close the connection.
	conn.Close()
	return err
}

func WriteParsedResponseToFile(response get.ParsedResponse, path string) error {
	// Marshal the struct to pretty JSON
	jsonBytes, err := json.MarshalIndent(response, "", "  ")
	if err != nil {
		return fmt.Errorf("failed to marshal response: %w", err)
	}

	// Write to file
	err = os.WriteFile(path, jsonBytes, 0644)
	if err != nil {
		return fmt.Errorf("failed to write file: %w", err)
	}

	return nil
}
