# AskMe with ES Example

## Building the AskMe Backbone
```shell
$> cd src/main
$> docker compose -f askme.yml up
```
This will fire up the remote rabbitmq and original askme components 
including web interface, query transformation and documents ranking.
The webpage can be accessed via http://localhost:8080/ask.

> NOTE: the AskMe modules are connected via the RabbitMQ instance that is running on a remote server, so you might not be able to
run it because of the firewall.

## Building the Elasticsearch Module
```shell
$> cd ES-test-rabbitmq
$> docker-compose -f docker-compose.yml up --build -d
```
This will fire up the ES and build the index `test_rabbitmq_idx` 
with some sample documents (loaded from `test_es_doc.json`).


## Connecting ES and AskMe via RabbitMQ
(TODO: dockerize this part)
```shell
cd python
pip install -r requirements.txt
python main.py
```
This will enable the rabbitmq post office and mailbox that 
receive processed queries and send retrieved documents from ES to askme. 

## Testing
I submit the query `"hand-hygiene, and personal protective equipment"` via the askme search box and 
two ranked documents will be retrieved and displayed on the page.
