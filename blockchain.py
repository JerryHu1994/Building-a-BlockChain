#!/usr/bin/env python
##################################
# University of Wisconsin-Madison
# Author: Jieru Hu
##################################

import numpy as np
import json
import hashlib
from time import time
# object represents a blockchain, keeping track of the entire chain
# and all current transactions.
class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []

        # create a root block
        self.create_new_block(100)

    # create a new block
    def create_new_block(self, key, previous_hash=None):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
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
        while not self.validate_new_key(last_hash, new_key):
            new_key += 1
        return new_key

    # static method to verify the new key correctness
    @staticmethod
    def validate_new_key(last_key, new_key):
        new_key = ('{}{}'.format(last_key, new_key)).encode()
        guess_hash = hashlib.sha256(new_key).hexdigest()
        return guess_hash[:4] == "0000"


    # creates a hash code for a block
    @staticmethod
    def hash(block):
        block_str = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_str).hexdigest()

