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
hosts = [] # keeps a list of port numbers
users = {} # dictionary keeping username -> # of coins
exit_flag = True # flag to exit the program

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

def check_int(str):
    """
    Check if a string can be converted to an integer
    """
    try:
        int(str)
    except ValueError:
        return False
    return True

def add_node(args):
    """
    Launcher a blockchain server given a port number
    Args:
        args: user argument
    Returns:
        0 if succeeds otherwise 1
    """
    if not len(args):
        print ("Please enter a port number\nUSAGE: addnode 5000")
        return 1
    if not len(args):
        print ("ERROR: Please provide port numbers")
    for node in args:
        if check_int(node):
            val = int(node)
        else:
            print ("{} is not a valid port number".format(node))
            continue
        print ("Launching a blockchain server on port {}".format(node))
        proc = Popen(['python', 'blockchain_server.py', "--port", node], stdout=PIPE, stderr=PIPE)

        time.sleep(1) # sleep 1 seconds to wait for server to fire up

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
    return 0

def mine(args):
    """
    Mine a coin on a certain node given the node name and user name
    Args:
        args: user argument
    Returns:
        0 if succeeds otherwise 1
    """
    if len(args) != 2:
        print ("Mine expects two arguments: user and node port\nUSAGE: mine Jerry 5000")
        return 1
    name, host = args
    if not check_int(host):
        print ("Port number must be an integer")
        return 1
    if not int(host) in hosts:
        print ("Cannot find a node server on port {}".format(int(host)))
        return 1
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
    if len(args) != 4:
        print ("trans operation expects four arguments: sender, recipient, amount, port")
        return 1
    sender, recipient, amount, port = args
    if not check_int(amount) or not check_int(port):
        print ("amount and port must all be integers")
        return 1
    if not sender in users and users[sender] < amount:
        print ("{} does not have enough balance")
        return 1
    url = "http://localhost:{}/transactions/new".format(port)
    payload = {
        "sender": sender,
        "recipient": recipient,
        "amount":int(amount)
    }
    ret = requests.post(url, json=payload)
    # increment and decrement the value for sender and recipient
    users[sender] -= 1
    if recipient in users:
        users[recipient] -= 1
    else:
        users[recipient] = 1
    print (ret.text)
    return 0

def delete_node(args):
    """
    Kill the server node given its port number
    Args:
        args: user argument
    Returns:
        0 if succeeds otherwise 1
    """
    port = int(args[0])
    ret = shutdown_node(port)
    if ret == 0:
        print ("Killing server node with portnumber {}".format(port))
    else:
        print ("Failed to kill the server node on port {}".format(port))
        return 1
    return 0

def print_users(args):
    """
    Print a list of users and their coins
    Returns:
        0 if succeeds otherwise 1
    """
    if not len(users):
        print ("No users found.")
    for user, val in users.items():
        print ("{}: {} coins".format(user, val))
    return 0

def print_node(args):
    """
    Print a node in a graph format
    Args:
        args: node port number
    Returns:
        0 if succeeds otherwise 1
    """
    port = args[0]
    if not check_int(port):
        print ("The port number must be an integer")
        return 1
    url = "http://localhost:{}/chain".format(port)
    ret = requests.get(url)
    data = json.loads(ret.text)
    # print the chain
    for i in range(int(data["length"])-1):
        print ("========================================")
        print (data["chain"][i])
        print ("========================================")
        print ("         ||         ")
        print ("         ||         ")
        print ("         ||         ")
        print ("         \/         ")

    print ("========================================")
    print (data["chain"][-1])
    print ("========================================")
    return 0

def resolve_node(args):
    """
    Resolves all given nodes, basically running consensus algorithm on its nodes
    Returns:
        0 if succeeds otherwise 1
    """
    for node in args:
        if not check_int(node):
            print ("The port number must be an integer")
            return 1
        val = int(node)
        url = "http://localhost:{}/nodes/resolve".format(val)
        ret = requests.get(url)
        print (ret)
    return 0

def get_help(args):
    """
    Print the help menu
    Return 0
    """
    help_string = "In the blockchain simulation, following commands are included:"
    str_list = ["addnode", "launch a blockchain node server.\n","Usage: addnode <portnumber>",
    "mine", "mine a bitcoin on a specific node for a specific user.\n", "Usage: mine <user> <portnumber>",
    "trans", "perform a bitcoin transaction between users.\n", "Usage: trans <sender> <recipient> <amount>\
    <portnumber>",
    "deletenode", "shutdown a blockchain node server.\n", "Usage: deletenode <portnumber>",
    "resolve", "run consensus algorithm among its neighbor nodes.\n", "Usage: resolve <portnumber>",
    "printusers","print all registered users and their bitcoin numbers.\n", "Usage: printusers",
    "printnode", "print the blockchain for a specific node.\n", "Usage: printnode <portnumber>",
    "help", "print the help information.\n", "Usage: help",
    "exit", "exit the console.\n", "Usage: exit"]
    print (help_string)
    ind = 0
    while ind < len(str_list):
        str_to_print = '{0: <13}'.format(str_list[ind]) + str_list[ind+1] + "             " + str_list[ind+2]
        print (str_to_print)
        ind += 3
    return 0

def exit(args):
    """
    Exit gracefully, shutting down all nodes/
    Returns 1
    """
    global exit_flag
    for node in hosts:
        ret = shutdown_node(node)
        if ret == 0:
            print ("Killing server node with portnumber {}".format(str(node)))
        else:
            print ("Failed to kill the server node on port {}".format(str(node)))
    exit_flag = False
    print ("Goodbye.")
    return 0

"""
dictionary mapping users command to the handler functions
"""
dict_functions = {
    "addnode" : add_node,
    "mine" : mine,
    "trans" : trans,
    "deletenode" : delete_node,
    "resolve" : resolve_node,
    "printusers" : print_users,
    "printnode" : print_node,
    "help" : get_help,
    "exit" : exit
}

# main method
def main():

    print ("Welcome to BlockChain simulation !")
    # main user loop
    while (exit_flag):
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

