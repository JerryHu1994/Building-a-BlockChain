#!/usr/bin/env python
##################################
# University of Wisconsin-Madison
# Author: Jieru Hu
##################################

import numpy as np
import json
import hashlib
from urllib.parse import urlparse
from utils import *
import time
import requests

# object represents a blockchain, keeping track of the entire chain
# and all current transactions.
class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []

        # create a root block
        self.create_new_block(100)
        # store all nodes
        self.node_list = set()

    # create a new block
    def create_new_block(self, key, previous_hash=None):
        local_time = time.localtime()
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time.strftime("%a, %d-%b-%Y-%H:%M:%S GMT", local_time),
            'transactions':self.current_transactions,
            'key':key,
            'previous_hash': previous_hash,
        }
        self.current_transactions = []
        self.chain.append(block)
        return block

    # creates a new transaction
    def create_new_transaction(self, sender, recipient, amount):
        self.current_transactions.append({
            'sender': sender,
            'recipient':recipient,
            'amount':amount,
        })
        return self.get_last_block()['index'] + 1

    # fetch the last block in the chain
    def get_last_block(self):
        return self.chain[-1]

    # find a hash h such as hash(h, h') constains 4 leading zeros, where h'
    # is the prevous hash and hash() is the hash function.
    def mining(self, last_hash):
        new_key = 0
        while not validate_key(last_hash, new_key):
            new_key += 1
        return new_key

    # register a new node address
    def register_node(self, addr):
        #parsed_url = urlparse(addr)
        self.node_list.add(addr)

    def resolve_conflicts(self):
        neighbor_nodes, new_chain = self.node_list, None
        max_chain_length = len(self.chain)

        for n in neighbor_nodes:
            # get request from neighbor nodes
            url = '{}/chain'.format(n)
            print (url)
            response = requests.get(url)

            if response.status_code == 200:
                response_json = response.json()
                length = response_json['length']
                chain = response_json['chain']
                # check the chain length is shorter and also the chain is valid
                if length > max_chain_length and validate_chain(chain):
                    max_chain_length = length
                    new_chain = chain
            else:
                print ("Get response failed")
        # update the chain in the blockchain if there is a candidate
        if new_chain:
            self.chain = new_chain
            return True
        return False

