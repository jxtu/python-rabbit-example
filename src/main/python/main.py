from typing import Callable
from rabbit import *
from flask import Flask, escape, request, abort
from tqdm import tqdm
import sys
import json
import numpy as np

EMBEDDINGS_PATH = 'cord_19_embeddings_2020-06-16.csv'
MAX_NUM_SIMILAR = 100
DEFAULT_NUM_SIMILAR = 10

'''
load_embeddings: loads SPECTER document embeddings and converts them into {id:vector} 
@params 
    embeddings_path --> path to CORD-19 SPECTER document embeddings
@returns embedding dictionary {id:vector}, where id is document id string and vector is numpy array of vector
'''
def load_embeddings(embeddings_path):
    embeddings = {}
    with open(embeddings_path, 'r') as f:
        for line in tqdm(f, desc='reading embeddings from file...'):
            split_line = line.rstrip('\n').split(",")
            embeddings[split_line[0]] =  np.array(split_line[1:]).astype(np.float)
    return embeddings

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
@returns array of most similar documents, by document id
'''
def n_most_similar(embeddings, document_id, topn):
    nms = [{'id': '', 'similarity':-1}] * (topn + 1)
    for document in embeddings.keys():
        similarity = cos_sim(embeddings[document],embeddings[document_id])
        if similarity > nms[0]['similarity']:
            nms[0] = {'id': document, 'similarity': similarity}
            nms.sort(key=lambda tup: tup['similarity'])
    nms.sort(key=lambda tup: tup['similarity'], reverse=True)
    return nms[1:]


embeddings = load_embeddings(EMBEDDINGS_PATH)


'''
Endpoint for Flask web service
'''
app = Flask(__name__)
@app.route('/similar/<id>')
def find_similar_documents(id):
    if request.args.get('n'):
        # if user-provided number of similar documents (n) is not a number
        try:
            num_similar = int(request.args.get('n'))
        except:
            abort(400)
    else:
        num_similar = default_num_similar
    
    # document id does not exist
    if id not in embeddings.keys():
        abort(404)

    # number of requested similar documents is too large
    elif num_similar > max_num_similar:
        abort(400)

    # returns JSON array of similar document IDs and cosine similarity
    else:
        return str(n_most_similar(embeddings,id,num_similar))





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
        #if message.command == 'print':
        #    print("[on_message] BODY: {}".format(message.body))
        #    status = "printed"
        #elif message.command == 'upper':
        #    message.body = message.body.upper()
        #    status = "uppercased"
        #elif message.command == 'lower':
        #    message.body = message.body.lower()
        #    status = "lowercased"
        if message.command == "similar":
            default_similar = 10
            split_body = message.body.split(" ")
            # TODO check for error in case of invalid message
            document_id = split_body[0]
            if len(split_body) == 1:
                num_similar = default_similar
            else:
                num_similar = int(split_body[1])
            message.body = "Processing " + document_id + " for " + str(num_similar) + " similar documents."

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



