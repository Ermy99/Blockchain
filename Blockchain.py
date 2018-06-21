import hashlib
import json
import requests #??

from time import time
from uuid import uuid4
from textwrap import dedent #??
from flask import Flask, jsonify, request
from urllib.parse import urlparse #??

class Blockchain(object):
	
	def __init__(self):
		self.chain = []
		self.nodes = set()
		self.current_transactions = []
		self.new_block(previous_hash = 1, proof = 100)

	def register_node(self, address):
		parse_url = urlparse(address)
		self.nodes.add(parse_url.netloc)

	def valid_chain(self, chain):
		last_block = chain[0]
		current_index = 1

		while current_index < len(chain):
            block = chain[current_index]
            print("{}".format(last_block))
            print("{}".format(block))
            print("\n-----------\n")

            if block['previous_hash'] != self.hash(last_block):
                return False
            if not self.valid_proof(last_block['proof'], block['proof']):
                return False

            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self): 
    	neighbors = self.nodes
    	new_chain = None
    	max_length = len(self.chain)
    	for node in neighbors:
    		response = requests.get("http://{}/chain")

    		if response.status_code == 200;
    			length = response.json()["length"]
    			chain = response.json()["chain"]

    				if length > max_length and self.valid_chain(chain):
    					max_length = length
    					new_chain = chain

    	if new_chain:
    		self.chain = new_chain
    		return True

		return False    		


	def new_block(self, proof, previous_hash=None): 
		#creates new block, adds transactions and everything else to it, and then resets the transactions list
		block = {
			"index": len(self.chain) + 1, #sso does indexing start @ 1?
			"timestamp": time(),
			"transactions": self.current_transactions,
			"proof": proof,
			"previous_hash": previous_hash or self.hash(self.chain[-1]) # is self necessariy if hash() is static
		}

		self.current_transactions = []
		self.chain.append(block)
		return block


	def new_transaction(self, sender, recipient, amount):
		#adds the transaction to the list

	def last_block(self):
		#returns last block in the chain
		return self.chain[-1]

	def proof_of_work(self, last_proof):
		proof = 0
		while self.valid_proof(last_proof, proof) is False:
			proof += 1
		return proof 

	@staticmethod
	def valid_proof(last_proof, proof):
		#validates if the two proofs hashed together gives 4 leading 0s
		guess = ("{}{}".format(last_proof, proof)).encode()
		guess_hash = hashlib.sha256(guess).hexdigest()
		return guess_hash[:4] == "0000"

app = Flask(__name__)
node_identifier = str(uuid4()).replace('-', '')
blockchain = Blockchain()

@app.route("/", methods=["GET"]) #WORKS!
def index():
	return "Welcome to my Blockchain Web App!"

@app.route("/mine", methods=["GET"]) #these are called endpoints
def mine(): #WORKS!!

	#1. calculate the proof
	last_block = blockchain.last_block
	last_proof = last_block["proof"]
	proof = blockchain.proof_of_work(last_proof)

	#2. reward the miner by transacting a coin to them
	blockchain.new_transaction(
		sender="0",
		recipient=node_identifier,
		amount=1
		)

	#3. create the block and add it to the chain
	previous_hash = blockchain.hash(last_block)
	block = blockchain.new_block(proof, previous_hash)
	response = {
		"message": "New Block forged.",
		"index": block["index"],
		"transactions": block["transactions"],
		"proof": block["proof"],
		"previous_hash": block["previous_hash"]
	}
	return jsonify(response), 200

@app.route("/transactions/new", methods=["GET", "POST"])
def new_transaction(): # adding a new transaction
	values = request.get_json()
	required = ["sender", "recipient", "amount"]

	if not all (k in values for k in required):
		return "Missing values", 400

	index = blockchain.new_transaction("sender", "recipient", values["amount"]) #why is values needed here?
	response = {"message" : "Transaction will be added to Block %d".format(index)}
	return jsonify(response),201

@app.route("/chain", methods=["GET"]) #WORKS!!
def full_chain():
	response = {
	"chain": blockchain.chain,
	"length": len(blockchain.chain)
	}
	return jsonify(response), 200

@app.route("/nodes/register", methods=["POST"])
def register_nodes():
	values = request.get_json()
	nodes = values.get("nodes") # is the input a dict of nodes?

	if nodes is None:
		return "Error: Please supply a valid list of nodes", 400

	for node in nodes:
		blockchain.register_node(node)

	response = {
		"message": "New nodes have been added.",
		"total_nodes": list(blockchain.nodes)
	}

	return jsonify(response), 201 #why do we have to jsonify all the outputs?

@app.route("/nodes/resolve", methods=["GET"])
def consensus():
	replaced = blockchain.resolve_conflicts()

	if replaced:
		response = {
			"message": "Our chain was replaced.",
			"new_chain": blockchain.chain
		}
	else:
		response = {
			"message": "Our chain is authoritative.",
			"new_chain": blockchain.chain
		}
	return jsonify(response), 200

if __name__ == "__main__":
	
	"""
	missing a part
	"""
	
	app.run(debug=True)

"""
Hashlib: 
json.dumps(): dictionary to json
encode() = returns bytes
HTTP Client: makes requests using urls...
Unix time: will be used to timestamp a block
Block: each block in the chain has an index, a timestamp, a list of transactions, a proof, and the hash of the previous Block
"""