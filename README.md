# Kevin's Notes
This is a test



# RabbitMQ Python Example

## Requirements

1. Python 3.7.1<br/>Other versions of Python may work but only Python 3.7.1 has been tested.
1. Java 8<br/>Newer versions of Java can be used, but will result in an **Illegal reflective access** warnings from the Groovy code. These warnings are safe to ignore.
1. RabbitMQ<br/>For this example I suggest using the RabbitMQ Docker container so no installation is required.

## Building The Java Module

The Java module uses Maven as the build system and the `src/main/docker` directory contains a Bash script to generate the Docker container.  The `make.sh` script will build the project and copy the JAR file to the `src/main/docker` directory before building the container with `docker build -t rabbit-groovy .`

``` 
$> cd src/main/docker
$> ./make.sh
```
Or,
``` 
$> mvn clean package
$> cp target/rabbit-groovy.jar src/main/docker
$> cd src/main/docker
$> docker build -t rabbit-groovy .
```

## Building the Python Module

The only thing that needs to be built for the Python module is the Docker container. 

``` 
$> cd src/main/python
$> docker build -t rabbit-python .
```

To run the `main.py` program from the command line its requirements will have to be installed:
``` 
$> pip install -r requirements.txt
```

## Running 

Before running the Java/Groovy and Python modules a RabbitMQ server needs to be started.  For simplicity we will use the Docker container provided by RabbitMQ with the default user (*guest*) and password (*guest*) 

``` 
$> docker run -d --name rabbit --hostname localhost -p 5672:5672 -p 15672:15672 rabbitmq:3-management 
```

The RabbitMQ management console is available at http://localhost:15672 if you need to check if messages are reaching the RabbitMQ server.

Both programs can be run from the command line. Open a terminal/shell for each program and run:

Python:
``` 
$> python main.py
```

Java:
```
$> java -jar rabbit-groovy.jar
```

Or to run the Docker containers:

Python:
``` 
$> docker run -it rabbit-python
```

Java/Groovy:
``` 
$> docker run -it rabbit-groovy
```

## Usage

Text entered into the Java program will be sent to the Python program, which will perform some simple tasks (convert to upper/lower case or print), and then return the result to the Java program.

In the Java terminal:
``` 
$> lower HELLO WORLD
{
  "id" : "05e9e3e1-4f01-4222-860f-ca6ed8943c9e",
  "command" : "lower",
  "body" : "hello world",
  "route" : [ ],
  "parameters" : {
    "status" : "lowercased"
  }
}

$> upper hello world
{
  "id" : "42d0125c-19b0-4700-86a6-1a1950af795e",
  "command" : "upper",
  "body" : "HELLO WORLD",
  "route" : [ ],
  "parameters" : {
    "status" : "uppercased"
  }
}

$> tokenize hello world
{
  "id" : "a6955f78-5bf4-4634-ad5f-6e3e5ca5075c",
  "command" : "tokenize",
  "body" : "hello world",
  "route" : [ ],
  "parameters" : {
    "message" : "Unknown command 'tokenize'",
    "status" : "ERROR"
  }
}
```

Enter the command `halt` to shutdown the Python process and `exit` to terminate the Java program.

## Messages

All messages passed between **AskMe** modules use the JSON format used here.  Each message consists of:

- **id: str**<br/>this can be any string that uniquely identifies the message for the lifetime of the application. The ID is almost always a UUID.
- **command: str**<br/>used to send administration commands to a service, e.g. shutdown or health check messages.
- **body: object**<br/>what this is will depend on the service.
- **route: List<str>**<br/>a list of RabbitMQ message queues.  A service is expected to remove the first item from the *route* and send the message to that message queue when it has finished processing.
- **parameters: Dict<str,str>**<br/>a dictionary of values that can be used to send application specific parameters to a service.

All services should update and return the same message object that they received.  If a service does create a new message object it should be sure to copy all targets from the `route` as well as the `parameters` dictionary.
