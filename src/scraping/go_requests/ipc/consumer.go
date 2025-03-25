package ipc

import (
	"fmt"
	"log"
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
	)
	fmt.Printf("\nNew consumer: %s", queueName)
	if err != nil {
		fmt.Printf("\nError when making connection: %s\n", err.Error())
		conn.Close()
		return err
	}

	// Call consumer.Run directly. This call will block and continuously wait for new messages.
	err = consumer.Run(func(d rabbitmq.Delivery) rabbitmq.Action {
		// Unmarshal the message body into an RCollection.
		targets, err := ipc_structs.UnmarshalTargets(d.Body)
		if err != nil {
			// If unmarshalling fails, log the error and Nack the message.
			fmt.Printf("\nError unmarshalling data: %s\n", string(d.Body))
			return rabbitmq.NackDiscard
		}

		// Get options for the crawler behavior
		crawlerOpts := get.DefineCrawlerBehavior(targets, "", "")
		results := get.GetContent(crawlerOpts, targets)

		// Process results as they arrive.
		for result := range results {
			fmt.Printf("\nRetrieved content for %s", result.Alias)
		}

		// After processing, acknowledge the message.
		return rabbitmq.Ack
	})

	if err != nil {
		log.Printf("consumer run error: %v", err)
	}

	// If consumer.Run exits, close the connection.
	conn.Close()
	return err
}
