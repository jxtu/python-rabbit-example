from typing import Callable
from rabbit import *
from flask import Flask, escape, request, abort, make_response, jsonify
from tqdm import tqdm
from cord_index import *
import sys
import json
import numpy as np

EMBEDDINGS_PATH = 'embeddings/cord_19_embeddings_2020-06-16.csv'
METADATA_PATH = 'embeddings/metadata.csv'
MAX_NUM_SIMILAR = 100
DEFAULT_NUM_SIMILAR = 10




'''
load_embeddings: loads SPECTER document embeddings and converts them into {id:vector} 
@params 
    embeddings_path --> path to CORD-19 SPECTER document embeddings
@returns embedding dictionary {id:vector}, where id is document id string and vector is numpy array of vector
'''
def load_embeddings(embeddings_path):
    index = CordIndex(METADATA_PATH)
    embeddings = {}
    no_pmc_count = 0
    with open(embeddings_path, 'r') as f:
        for line in tqdm(f, desc='reading embeddings from file...'):
            split_line = line.rstrip('\n').split(",")

            # Keep only documents with PMCID 
            pmcid = index.get_by_cord_uid(split_line[0])['pmcid']
            if pmcid != '':
                embeddings[pmcid] =  np.array(split_line[1:]).astype(np.float)
            else:
                no_pmc_count += 1
    print(no_pmc_count)
    print(len(embeddings))

    return embeddings

embeddings = load_embeddings(EMBEDDINGS_PATH)


'''
cos_sim: calculates the cosine similarity between two vectors 
@params 
    a --> first vector
    b --> second vector
@returns float cosine similarity
'''
def cos_sim(a,b):
    dot_prod = np.dot(a,b)
    mag_a = np.sqrt(a.dot(a))
    mag_b = np.sqrt(b.dot(b))
    return np.divide(dot_prod, np.multiply(mag_a, mag_b))


'''
n_most_similar: finds and returns the top n most similar documents 
@params 
    embeddings --> the loaded embedding file as {id:vector} dict
    document_id --> the PMC document id
    topn --> number of similar documents to be returned
@returns json object of most similar documents, by document id
'''
def n_most_similar(embeddings, document_id, topn):
    nms = [{'pmcid': '', 'similarity':-1}] * (topn + 1)

    for document in embeddings.keys():
        similarity = cos_sim(embeddings[document],embeddings[document_id])
        if similarity > nms[0]['similarity']:
            nms[0] = {'pmcid': document, 'similarity': similarity}
            nms.sort(key=lambda tup: tup['similarity'])
    nms.sort(key=lambda tup: tup['similarity'], reverse=True)
    documents = {'documents': nms[1:]} 
    return documents


def generate_error_response(errorType, requestType, params):
    if requestType == 'JSON':
        if errorType == "provided_number":
            response = make_response(
                    jsonify(
                        {"message": "Number of similar documents must be integer greater than 0 and less than '{}': Given '{}'".format(params[0],params[1]), "severity": "danger"}
                    ),
                    400,
                )
            response.headers["Content-Type"] = "application/json"
            return response
        elif errorType == "missing_document":
            response = make_response(
                    jsonify(
                        {"message": "Document ID not found (must be PMC id): Given '{}'".format(params[0]), "severity": "danger"}
                    ),
                    404,
            )
            response.headers["Content-Type"] = "application/json"
            return response
    if requestType == "HTML":
        if errorType == "provided_number":
            return "<h1>ERROR 400</h1><p>Number of similar documents must be integer greater than 0 and less than '{}': Given '{}'</p>".format(params[0],params[1]), 400
        
        if errorType == "missing_document":
            return "<h1>ERROR 404</h1><p>Document ID not found (must be PMC id): Given '{}'</p>".format(params[0]), 404


def html(results, id,num_similar):
    return_string = "<h3>Displaying the {} most similar documents to {}</h3>".format(num_similar,id)
    for document in results['documents']:
        return_string += "<p>ID: {}, Similarity: {}</p>".format(document['pmcid'], document['similarity'])
    return return_string





'''
Endpoint for Flask web service
'''
app = Flask(__name__)
@app.route('/similar/<id>')
def find_similar_documents(id):

    if 'application/json' in request.headers.getlist('accept')[0].split(","):
        requestType = "JSON"
    else:
        requestType = "HTML"


    if request.args.get('n'):
        # if user-provided number of similar documents (n) is not a number
        try:
            num_similar = int(request.args.get('n'))
        except:
            return generate_error_response("provided_number", requestType, [MAX_NUM_SIMILAR,request.args.get('n')])
             
    else:
        num_similar = DEFAULT_NUM_SIMILAR
    
    # document id does not exist
    if id not in embeddings.keys():
        return generate_error_response("missing_document", requestType, [id])

    # number of requested similar documents is too large
    elif num_similar > MAX_NUM_SIMILAR:
        return generate_error_response("provided_number", requestType, [MAX_NUM_SIMILAR,num_similar])


    else:
        if requestType == "JSON":
            return json.dumps(n_most_similar(embeddings,id,num_similar))
        if requestType == "HTML":
            return html(n_most_similar(embeddings,id,num_similar),id,num_similar)





connection = None
inbox = None
po = None

# Callback to be called when a message arrives on the message queue named
# "task_queue"
def on_message(ack: Callable[[],None], m: str) -> None:
    print(str(m))
    if type(m) == str:
        print("[on_message] message is a string")
    else:
        print("Message is a {}".format(type(m)))

    ack() # ALWAYS call ack() to acknowledge the message was received.
    message = Message(m)
    print("[on_message] Message ID: {}".format(message.id))
    if message.command == "HALT":
        # Clean shutdown.  This will cause the `inbox.start()` below to exit.
        print("[on_message] Recevied HALT command")
        inbox.stop()
    elif len(message.route) > 0:
        status = "OK"
        status_line = None
    
        if message.command == "similar":
            split_body = message.body.split(" ")

            document_id = split_body[0]

            if document_id not in embeddings.keys():
                status  = "ERROR"
                message.set("message", "Document ID not found (must be PMC id): Given '{}'".format(document_id))
            
            elif len(split_body) == 1:
                message.body = n_most_similar(embeddings, document_id, DEFAULT_NUM_SIMILAR)
                status = "similar"

            else:
                try:
                    num_similar = int(split_body[1])
                except:
                    status  = "ERROR"
                    message.set("message", "Number of similar documents must be integer greater than 0 and less than '{}': Given '{}'".format(MAX_NUM_SIMILAR,split_body[1]))
                else:
                    if num_similar < 1 or num_similar > MAX_NUM_SIMILAR:
                        status  = "ERROR"
                        message.set("message", "Number of similar documents must be integer greater than 0 and less than '{}': Given '{}'".format(MAX_NUM_SIMILAR,split_body[1]))
                    else:
                        message.body = n_most_similar(embeddings, document_id, num_similar)
                        status = "similar"
            
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

def run():
    # Register our message handler and wait for messages.
    inbox.register(on_message)
    print('[*] Waiting for messages. To exit press CTRL+C')
    inbox.start()
    print("[*] Closed.")

    # Close the connection to prevent resource leaks on the server.
    po.close()


if __name__ == "__main__":
    host = "localhost"
    username = "guest"
    password = "guest"
    if len(sys.argv) == 4:
        host = sys.argv[1]
        username = sys.argv[2]
        password = sys.argv[3]

    connection = Connection(host, username, password)
    inbox = InBox("python_queue", connection)
    po = PostOffice(connection)

    run()



