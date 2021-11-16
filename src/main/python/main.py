import json
from typing import Callable
from rabbit import *
import sys

from query_processor import SimpleQueryProcessor
from es_query import run_query
from elasticsearch_dsl.connections import connections  # type: ignore

connection = None
inbox = None
po = None

stopwords_file_path = "stopwords.txt"
query_processor = SimpleQueryProcessor(stopwords_file_path)
# connections.create_connection(hosts=["es01:9200"], timeout=100, alias="default")
connections.create_connection(hosts=["localhost:9200"], timeout=100, alias="default")


# Callback to be called when a message arrives on the message queue named
# "task_queue"
def on_message(ack: Callable[[], None], m: str) -> None:
    if type(m) == str:
        print("[on_message] message is a string")
    else:
        print("Message is a {}".format(type(m)))

    ack()  # ALWAYS call ack() to acknowledge the message was received.

    message = Message(m)
    message.command = "search"
    print("[on_message] Message ID: {}".format(message.id))
    if message.command == "HALT":
        # Clean shutdown.  This will cause the `inbox.start()` below to exit.
        print("[on_message] Recevied HALT command")
        inbox.stop()
    elif len(message.route) > 0:
        status = "OK"
        status_line = None
        if message.command == "print":
            print("[on_message] BODY: {}".format(message.body))
            status = "printed"
        elif message.command == "upper":
            message.body = message.body.upper()
            status = "uppercased"
        elif message.command == "lower":
            message.body = message.body.lower()
            status = "lowercased"
        elif message.command == "transform":
            message.body = query_processor(message.body)
        elif message.command == "search":
            message.body = run_query(message.body, index="test_rabbitmq_idx")
        else:
            status = "ERROR"
            message.set("message", "Unknown command '{}'".format(message.command))

        message.set("status", status)
        print("[on_message] {} {}".format(status, status_line))
        # Reply to the message
        po.send(message)
    else:
        print("[on_message] Dropping message: no route")

    print("[on_message] Done")


def on_message_todo(ack: Callable[[], None], m: str) -> None:
    # TODO: implement it in the future to send and receive messages from ES
    raise NotImplementedError


def run():
    # Register our message handler and wait for messages.
    inbox.register(on_message)
    print("[*] Waiting for messages. To exit press CTRL+C")
    inbox.start()
    print("[*] Closed.")

    # Close the connection to prevent resource leaks on the server.
    po.close()


if __name__ == "__main__":
    host = "rabbitmq.lappsgrid.org"
    username = "askme"
    password = "askme"
    port = 5672
    virtual_host = "askme"
    if len(sys.argv) == 4:
        host = sys.argv[1]
        username = sys.argv[2]
        password = sys.argv[3]

    connection = Connection(host, username, password, virtual_host=virtual_host)
    # change the queue name to receive different messages
    inbox = InBox(queue_name="solr.mailbox", connection=connection, exchange="jingxuan")
    po = PostOffice(connection, exchange="jingxuan")

    run()
