import hashlib
import json
import time

from uuid import uuid4
from textwrap import dedent
from flask import Flask

class Blockchain(object):
	
	def __init__(self):
		self.chain = []
		self.current_transactions = []
		self.new_block(previous_hash = 1, proof = 100)

	def new_block(self, proof, previous_hash=None): 
		#creates new block, adds transactions and everything else to it, and then resets the transactions list
		block = {
			"index":len(self.chain) + 1, #sso does indexing start @ 1?
			"timestamp": time.time(),
			"transactions": self.current_transactions,
			"proof": proof,
			"previous_hash": previous_hash or self.hash(self.chain[-1]) # is self necessariy if hash() is static
		}

		self.current_transactions = []
		self.chain.append(block)
		return block


	def new_transaction(self, sender, recepient, amount):
		#adds the transaction to the list
		self.transactions.append({
			"sender": sender,
			"recepient": recepient,
			"amount": amount
			})
		#returns the index of the Block which will hold this transactionn
		return self.last_block()['index'] + 1

	@staticmethod
	def hash(block):
		block_string = json.dumps(block, sort_keys=True).encode()
		return hashlib.sha256(block_string).hexdigest() 

	@property
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
		guess = f"{last_proof}{proof}".encode()
		guess_hash = hashlib.sha256(guess).hexdigest()
		return guess_hash[:4] == "0000"

"""
Hashlib: 
json.dumps(): dictionary to json
encode() = returns bytes
HTTP Client: makes requests using urls...
Unix time: will be used to timestamp a block
Block: each block in the chain has an index, a timestamp, a list of transactions, a proof, and the hash of the previous Block
"""