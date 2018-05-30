#!/usr/bin/env python
##################################
# University of Wisconsin-Madison
# Author: Jieru Hu
##################################

import numpy as np
import json
import hashlib
from time import time
from urllib.parse import urlparse


# method to verify the new key correctness
def validate_key(last_key, new_key):
    new_key = ('{}{}'.format(last_key, new_key)).encode()
    guess_hash = hashlib.sha256(new_key).hexdigest()
    return guess_hash[:4] == "0000"

# Validate if a given blockchain is valid
def validate_chain(chain):
    last_block = chain[0]
    curr = 1

    while curr < len(chain):
        curr_block = chain[curr]
        # check the consistency of the previous hash
        if curr_block['previous_hash'] != hash(last_block):
            return False
        # check the key of the adjacent block is valid
        if not validate_key(last_block['key'], curr_block['key']):
            return False
        last_block = curr_block
        curr += 1
    return True

# creates a hash code for a block
def hash(block):
    block_str = json.dumps(block, sort_keys=True).encode()
    return hashlib.sha256(block_str).hexdigest()

