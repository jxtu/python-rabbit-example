import uuid
import pika
import json
import jsons

PERSIST = pika.BasicProperties(delivery_mode=2)


class Connection(object):
    """
    Manage a connection to the RabbitMQ server.
    """

    def __init__(
        self,
        host="localhost",
        username="guest",
        password="guest",
        port=5672,
        virtual_host="/",
    ):
        credentials = pika.PlainCredentials(username, password)
        self.parameters = pika.ConnectionParameters(
            host, port, virtual_host, credentials
        )
        # self.connection = pika.BlockingConnection(parameters)

    def connect(self):
        return pika.BlockingConnection(self.parameters)

    # def channel(self):
    #     return self.connection.channel()
    #
    # def close(self, code=200, text="Normal shutdown"):
    #     self.connection.close(code, text)


class InBox(object):
    """Receive incoming messages from the RabbitMQ server.

    Each InBox instance create its own connection and channel to the server
    and then declares a 'direct' exchange and binds it to a message queue.

    TODO: It should be possible to configure the durable and auto_delete
          properties of the queue and exchange.
    """

    def __init__(self, queue_name, connection, exchange, fair=False):
        self.queue_name = queue_name
        self.connection = connection.connect()
        self.channel = self.connection.channel()
        self.channel.exchange_declare(
            exchange=exchange, exchange_type="direct", auto_delete=False
        )
        self.queue = self.channel.queue_declare(
            queue=queue_name, durable=True, auto_delete=False
        )
        self.channel.queue_bind(queue=self.queue.method.queue, exchange=exchange)
        if fair:
            self.channel.basic_qos(prefetch_count=1)

    def register(self, callback):
        """Register a callback function that will be called when messages arrive
        on the message queue.

        An `ack()` method is provided to the callback so it can easily
        acknowledge the message. It is important that the callback method
        calls the `ack()` method after it has finished processing the message.
        Messages that are not acknowledged will be redelivered by the server
        until a receiver acknowledges the message.
        """

        def handler(channel, method, properties, body):
            def ack():
                self.ack(method)

            callback(ack, body.decode("utf-8"))

        self.channel.basic_consume(queue=self.queue_name, on_message_callback=handler)

    def ack(self, method):
        self.channel.basic_ack(delivery_tag=method.delivery_tag)

    def start(self):
        self.channel.start_consuming()

    def stop(self):
        self.channel.stop_consuming()
        self.connection.close()


class PostOffice(object):
    """ Send messages to message queues on the given exchange."""

    def __init__(self, connection, exchange):
        self.connection = connection.connect()
        self.channel = self.connection.channel()
        self.exchange = exchange

    def send(self, target, message=None):
        if message is None:
            self._dispatch(target)
        elif isinstance(message, str):
            self.channel.basic_publish(
                self.exchange, routing_key=target, body=message, properties=PERSIST
            )
        else:
            s = jsons.dumps(message)
            self.channel.basic_publish(
                self.exchange, routing_key=target, body=s, properties=PERSIST
            )

    def close(self):
        self.connection.close()

    def _dispatch(self, msg):
        """Send a Message object or dictionary.

        If the message does not contain a `route`, or the `route` is empty then
        the message is dropped.  Otherwise the first item is removed from the
        `route` and the message is sent to that target.

        Parameters
        ----------
            msg: dict or Message
                The message to be sent. If msg is a dictionary it is assumed to
                contain the same fields as the Message class
        """
        target = None
        payload = None
        if type(msg) == dict:
            if "route" in msg and len(msg["route"]) > 0:
                target = msg["route"].pop(0)
            payload = json.dumps(msg)
        elif type(msg) == Message:
            target = msg.route.pop(0)
            payload = jsons.dumps(msg)

        if target is not None:
            self.channel.basic_publish(
                self.exchange, routing_key=target, body=payload, properties=PERSIST
            )
        else:
            print("No target for message")


class Message(object):
    """Data model for the JSON exchanged by AskMe services.

    Each message consists of:
    id : str
        This can be any unique value but a UUID is used by default.
    command: str
        Indicates what should be done with the `body`. Also used to issue
        admin commands (PING, HALT, etc) to a service.
    body: object
        This can be anything.
    parameters: dict
        Application specific key/value pairs.
    route: list
        The list of message queues this message should be sent to.
    """

    def __init__(self, command=None, body=None, *route):
        if command is None:
            self.id = uuid.uuid4()
            self.command = ""
            self.body = ""
            self.route = list()
            self.parameters = dict()
        elif type(command) == dict:
            if "parameters" not in command:
                command["parameters"] = dict()
            if "route" not in command:
                command["route"] = list()
            self.__dict__ = command
        elif type(command) == Message:
            # TODO not sure if this is the best way to do a "copy constructor"
            # in Python.
            self.__dict__ = command.__dict__
        elif type(command) == str and body is None:
            d = json.loads(command)
            self.__dict__ = d  # jsons.load(command)
            if "parameters" not in self.__dict__:
                self.parameters = dict()
        else:
            self.id = uuid.uuid4()
            self.command = command
            self.body = body
            self.route = list(route)
            self.parameters = dict()

    def set(self, name, value):
        self.parameters[name] = value

    def deliverable(self):
        return len(self.route) > 0

    def route_to(self, target):
        self.route.append(target)

    def _copy_constructor(self, other):
        self.id = other.id
        self.command = other.command
        self.body = other.body
        self.parameters = other.parameters
        self.route = other.route

    def _init_from_dict(self, map):
        self.id = map["id"]
        self._set_property(map, "command")
        self._set_property(map, "body")
        self._set_property(map, "parameters")
        self._set_property(map, "route")

    def _set_property(self, map, key):
        if key in map:
            self.__dict__[key] = map[key]
