#!/usr/bin/env python
##################################
# University of Wisconsin-Madison
# Author: Jieru Hu
##################################

import numpy as np
from subprocess import Popen, PIPE
import requests
import os
import json
import time

# global varriables
hosts = []
users = {}

###################
# Helper functions
###################
def shutdown_node(port):
    """
    Close a node server on a specific port
    """
    if not port in hosts:
        print ("Cannot find server node on port {}".format(port))
        return 1
    cmd = "kill -9 `ps -ef |grep python |grep {}|awk '{{print $2}}'`".format(port)
    os.system(cmd)
    hosts.remove(port)
    return 0

def add_node(args):
    """
    Launcher a blockchain server given a port number
    Args:
        args: user argument
    Returns:
        0 if succeeds otherwise 1
    """
    print ("Entering add_node")
    if not len(args):
        print ("ERROR: Please provide port numbers")
    for node in args:
        try:
            val = int(node)
        except ValueError:
            print ("{} is not a valid port number".format(node))
            continue
        print ("Launching server on port {}".format(node))
        proc = Popen(['python', 'blockchain_server.py', "--port", node], stdout=PIPE, stderr=PIPE)

        time.sleep(1)

        # register existing nodes on the new node
        if len(hosts) != 0:
            register_url = "http://localhost:{}/nodes/register".format(str(val))
            node_list = ["http://localhost:{}".format(str(node)) for node in hosts]
            payload = {
                "nodes": node_list
            }
            print (payload)
            ret = requests.post(register_url, json=payload)
            print (ret)
        # register new node on existing nodes
        for node in hosts:
            register_url = "http://localhost:{}/nodes/register".format(str(node))
            payload = {
                "nodes": ["http://localhost:{}".format(str(val))]
            }
            ret = requests.post(register_url, json=payload)
            print (ret)
        # append the new node to the hosts
        hosts.append(val)


def mine(args):
    """
    Mine a coin on a certain node given the node name and user name
    Args:
        args: user argument
    Returns:
        0 if succeeds otherwise 1
    """
    print ("Mining")
    # TODO
    name, host = args
    url = 'http://localhost:{}/{}'.format(host,"mine")
    ret = requests.get(url)
    print (ret)

    # save the award for the user
    if name in users:
        users[name] += 1
    else:
        users[name] = 1
    return 0

def trans(args):
    """
    Performs a transaction between users given the sender, recipient and amount on 
    a specific node. (Default node: first node in the host list)
    Args:
        args: user argument
    Returns:
        0 if succeeds otherwise 1
    """
    print ("trans")
    # TODO
    sender, recipient, amount, port = args
    url = "http://localhost:{}/transactions/new".format(port)
    payload = {
        "sender": sender,
        "recipient": recipient,
        "amount":int(amount)
    }
#    headers = {'Content-Type': 'application/json'}
    ret = requests.post(url, json=payload)
    # increment and decrement the value for sender and recipient
    users[sender] -= 1
    if recipient in users:
        users[recipient] -= 1
    else:
        users[recipient] = 1
    print (ret.text)

def delete_node(args):
    """
    Kill the server node given its port number
    Args:
        args: user argument
    Returns:
        0 if succeeds otherwise 1
    """
    print ("Delete_node")
    port = int(args[0])
    ret = shutdown_node(port)
    if ret == 0:
        print ("Killing server node with portnumber {}".format(port))
    else:
        print ("Failed to kill the server node on port {}".format(port))

def print_users(args):
    """
    Print a list of users and their coins
    Returns:
        0 if succeeds otherwise 1
    """
    print ("Print all users")
    for user, val in users.items():
        print ("{}: {} coins".format(user, val))

def print_node(args):
    """
    Print a node in a graph format
    Args:
        args: node port number
    Returns:
        0 if succeeds otherwise 1
    """
    port = args[0]
    url = "http://localhost:{}/chain".format(port)
    ret = requests.get(url)
    print (ret.text)
    return 0

def resolve_node(args):
    """
    Resolves all given nodes, basically running consensus algorithm on its nodes
    Returns:
        0 if succeeds otherwise 1
    """
    for node in args:
        val = int(node)
        url = "http://localhost:{}/nodes/resolve".format(val)
        ret = requests.get(url)
        print (ret)
    return 0

def exit(args):
    """
    Exit gracefully, shutting down all nodes/
    Returns 1
    """
    print ("exit")
    for node in hosts:
        ret = shutdown_node(node)
        if ret == 0:
            print ("Killing server node with portnumber {}".format(str(node)))
        else:
            print ("Failed to kill the server node on port {}".format(str(node)))
    exit(1)

dict_functions = {
    "addnode" : add_node,
    "mine" : mine,
    "trans" : trans,
    "deletenode" : delete_node,
    "resolve" : resolve_node,
    "printusers" : print_users,
    "printnode" : print_node,
    "exit" : exit
}

# main method
def main():

    print ("Welcome to BlockChain simulation !")
    # main user loop
    while (True):
        response = input(">> ")
        res_list = response.split()
        if len(res_list) == 0:
            continue
        cmd, args = res_list[0], res_list[1:]
        # find the corresponding function
        func = dict_functions.get(cmd, "Not Found")
        if func != "Not Found":
            ret = func(args)
        else:
            print ("Oops, command not found")

    return 0


if __name__ == "__main__":
  main()

