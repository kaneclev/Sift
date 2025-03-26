import json
import logging
import os
import uuid

from typing import Any, Callable, Dict, Optional

import pika

logger = logging.getLogger(__name__)
PORT = os.environ['PORT']
HOST = os.environ['HOST']
USER = os.environ['RABBITMQ_PARSING_USER']
PASS = os.environ['RABBITMQ_PARSING_PASS']
class MessageBroker:
    """Handles RabbitMQ connections and operations."""

    def __init__(self, host=HOST, port=PORT, username=USER, password=PASS):
        self.connection_params = pika.ConnectionParameters(
            host=host,
            port=port,
            credentials=pika.PlainCredentials(username, password),
            heartbeat=600,
            blocked_connection_timeout=300
        )
        self.connection = None
        self.channel = None
        self.connect()

    def connect(self):
        """Establish connection to RabbitMQ server."""
        try:
            self.connection = pika.BlockingConnection(self.connection_params)
            self.channel = self.connection.channel()
            logger.info("Connected to RabbitMQ")
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise

    def ensure_connection(self):
        """Ensure the connection to RabbitMQ is active."""
        if not self.connection or self.connection.is_closed:
            logger.info("Reconnecting to RabbitMQ")
            self.connect()
        if not self.channel or self.channel.is_closed:
            self.channel = self.connection.channel()

    def declare_queue(self, queue_name: str, durable=True):
        """Declare a queue, creating it if it doesn't exist."""
        self.ensure_connection()
        self.channel.queue_declare(queue=queue_name, durable=durable)

    def declare_exchange(self, exchange_name: str, exchange_type='direct', durable=True):
        """Declare an exchange."""
        self.ensure_connection()
        self.channel.exchange_declare(exchange=exchange_name, exchange_type=exchange_type, durable=durable)

    def publish(self, queue_name: str, message: Dict[str, Any], correlation_id: Optional[str] = None):
        """Publish a message to a specific queue."""
        self.ensure_connection()

        # Generate correlation ID if not provided
        if correlation_id is None:
            correlation_id = str(uuid.uuid4())

        properties = pika.BasicProperties(
            delivery_mode=2,  # make message persistent
            correlation_id=correlation_id,
            content_type='application/json'
        )
        print(message)
        message_body = json.dumps(message)

        try:
            self.channel.basic_publish(
                exchange='',
                routing_key=queue_name,
                body=message_body,
                properties=properties
            )
            logger.info(f"Published message to queue '{queue_name}', correlation_id: {correlation_id}")
            return correlation_id
        except Exception as e:
            logger.error(f"Failed to publish message to queue '{queue_name}': {e}")
            raise

    def publish_to_exchange(self, exchange_name: str, routing_key: str, message: Dict[str, Any],
                           correlation_id: Optional[str] = None):
        """Publish a message to an exchange with routing key."""
        self.ensure_connection()

        if correlation_id is None:
            correlation_id = str(uuid.uuid4())

        properties = pika.BasicProperties(
            delivery_mode=2,
            correlation_id=correlation_id,
            content_type='application/json'
        )

        message_body = json.dumps(message)

        try:
            self.channel.basic_publish(
                exchange=exchange_name,
                routing_key=routing_key,
                body=message_body,
                properties=properties
            )
            logger.info(f"Published message to exchange '{exchange_name}' with routing key '{routing_key}'")
            return correlation_id
        except Exception as e:
            logger.error(f"Failed to publish message to exchange '{exchange_name}': {e}")
            raise

    def consume(self, queue_name: str, callback: Callable, auto_ack=False):
        """Start consuming messages from a queue."""
        self.ensure_connection()

        # Define a wrapper to handle parsing JSON
        def process_message(ch, method, properties, body):
            try:
                message = json.loads(body)
                callback(message, properties.correlation_id, method.delivery_tag, ch)
            except json.JSONDecodeError:
                logger.error(f"Failed to parse message as JSON: {body}")
                if auto_ack:
                    ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                if auto_ack:
                    ch.basic_ack(delivery_tag=method.delivery_tag)

        self.channel.basic_consume(
            queue=queue_name,
            on_message_callback=process_message,
            auto_ack=auto_ack
        )

        logger.info(f"Started consuming from queue '{queue_name}'")

        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            self.channel.stop_consuming()
            logger.info("Stopped consuming due to keyboard interrupt")
        except Exception as e:
            self.channel.stop_consuming()
            logger.error(f"Stopped consuming due to error: {e}")
            raise

    def acknowledge(self, channel, delivery_tag):
        """Acknowledge that a message has been processed."""
        if channel.is_open:
            channel.basic_ack(delivery_tag=delivery_tag)

    def reject(self, channel, delivery_tag, requeue=False):
        """Reject a message."""
        if channel.is_open:
            channel.basic_reject(delivery_tag=delivery_tag, requeue=requeue)

    def setup_dead_letter_queue(self, queue_name: str, dead_letter_exchange: str, dead_letter_routing_key: str):
        """Set up a queue with a dead letter exchange."""
        self.ensure_connection()
        self.channel.queue_declare(
            queue=queue_name,
            durable=True,
            arguments={
                'x-dead-letter-exchange': dead_letter_exchange,
                'x-dead-letter-routing-key': dead_letter_routing_key
            }
        )

    def close(self):
        """Close the connection to RabbitMQ."""
        if self.connection and self.connection.is_open:
            self.connection.close()
            logger.info("Closed connection to RabbitMQ")
