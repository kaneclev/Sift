package ipc

import (
	"encoding/json"
	"log"

	"github.com/wagslane/go-rabbitmq"
)

type RequestEncoding struct {
	URL   string `json:"url"`
	Alias string `json:"alias"`
}
type RCollection struct {
	Requests []RequestEncoding
}
type TargetsWrapper struct {
	Targets []RequestEncoding `json:"targets"`
}

func (col *RCollection) GetURLs() []string {
	urls := make([]string, 0, len(col.Requests))
	for _, req := range col.Requests {
		urls = append(urls, req.URL)
	}
	return urls
}
func (col *RCollection) MapURLsToAliases(urls []string) map[string]string {
	aliasMap := make(map[string]string)

	// Build a lookup table for URL -> Alias from the collection.
	lookup := make(map[string]string)
	for _, req := range col.Requests {
		lookup[req.URL] = req.Alias
	}

	// For each URL in the provided slice, check if an alias exists.
	for _, url := range urls {
		if alias, ok := lookup[url]; ok {
			aliasMap[url] = alias
		}
	}

	return aliasMap
}
func (col *RCollection) GetAliasByURL(url string) string {
	for _, req := range col.Requests {
		if req.URL == url {
			return req.Alias
		}
	}
	return ""
}

// ListenRCollectionsFromRabbitMQ establishes a persistent connection to RabbitMQ and
// continuously listens for new messages. Each time a message is received, it is unmarshaled
// into an RCollection and passed to the provided handler function for further processing.
// This function will return an error if the initial connection or consumer setup fails.
func ListenRCollectionsFromRabbitMQ(
	connStr, queueName, routingKey, exchange string,
	handler func(*RCollection),
) error {
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
		rabbitmq.WithConsumerOptionsRoutingKey(routingKey),
		rabbitmq.WithConsumerOptionsExchangeName(exchange),
		rabbitmq.WithConsumerOptionsExchangeDeclare,
	)
	if err != nil {
		conn.Close()
		return err
	}
	// Similarly, we do not defer consumer.Close() here because we want this consumer running continuously.

	// Run the consumer in a separate goroutine.
	go func() {
		err := consumer.Run(func(d rabbitmq.Delivery) rabbitmq.Action {
			var col RCollection
			// Unmarshal the message body into an RCollection.
			if err := json.Unmarshal(d.Body, &col); err != nil {
				log.Printf("failed to unmarshal JSON: %v", err)
				// Optionally, you could invoke a handler for errors or log them.
				return rabbitmq.NackDiscard
			}
			// Call the provided handler function with the new collection.
			handler(&col)
			return rabbitmq.Ack
		})
		if err != nil {
			log.Printf("consumer run error: %v", err)
		}
		// If consumer.Run ever exits, close the connection.
		conn.Close()
	}()

	return nil
}
