#!/usr/bin/env python
##################################
# University of Wisconsin-Madison
# Author: Jieru Hu
##################################
import blockchain
import json
from uuid import uuid4
from flask import Flask, jsonify, request

# main method
app = Flask("blockchain_server")
node_id = str(uuid4()).replace('-', '')

bc = blockchain.Blockchain()

@app.route('/mine', methods=['GET'])
def mining():
    last_block = bc.get_last_block()
    last_key = last_block['key']
    proof = bc.mining(last_key)

    #reward the user a new coin
    bc.create_new_transaction(
        sender="0",
        recipient=node_id,
        amount=1,
    )

    #append the block to the chain
    previous_hash = bc.hash(last_block)
    new_block = bc.create_new_block(proof, previous_hash)

    response = {
        "msg": "New Block Added",
        'index': new_block['index'],
        'transactions': new_block['transactions'],
        'key': new_block['key'],
        'previous_hash': new_block['previous_hash'],
    }
    return jsonify(response), 200


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    inputs = request.get_json()

    required_keys = ['sender', 'recipient', 'amount']
    if not all(v in inputs for v in required_keys):
        return "{} missing".format(v), 400

    # create new transaction
    idx = bc.create_new_transaction(inputs['sender'], inputs['recipient'], inputs['amount'])
    response = {'msg': 'New transaction added with index {}'.format(idx)}
    return jsonify(response), 201


@app.route('/chain', methods=['GET'])
def get_full_chain():
    response = {
        'chain': bc.chain,
        'length': len(bc.chain),
    }
    return jsonify(response), 200

if __name__ == "__main__":
  app.run(host='0.0.0.0', port=5000)

