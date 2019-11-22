#!/usr/bin/env python
import paramiko
import os
import re
import getpass
import time
import sys
import keyring
import getopt
from random import randint
from dotenv import load_dotenv

def print_help():
    print("Tool written to extract the CIMC debug string and automatically format for the CID tool.")
    print("The tool can accept newline/whitespace and will ignore any lines starting with '***'.")
    print("The tool assumes there is:\n" 
        "Only two lines for the challenge string\n"
        "Logged in username is the same as your Domain username")
    print("Pasting the follwing is allowed:")
    print("********************************************************************************\n"
        "Xuz//wIAAADJvite60KPumY/m3gHwkQNgC9L9SWCIj0cRsYGpNyXEAgh74s2GTI1\n"
        "VE5OVs8m+FwBFQ==\n"
        "DONE.\n"
        "********************************************************************************\n"
        "2$^CSSH gwong2 to x.x.x.x")
    print("\n\nctrl+c to end input.\nInput challenge: ")

def get_challenge(challengeString):
    C1C2 = []
    for line in challengeString:
        if re.search(r"^\*", line):
            continue
        elif re.search(r"^DONE\.", line):
            break
        else:
            C1C2.append(line)
    return C1C2


def ssh_recv_ready(channel):
    while not channel.recv_ready():
        time.sleep(5)    
    output = channel.recv(9999)
    return output


def send_command(server, user, passwd, C1, C2):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
         ssh.connect(hostname=server, username=user, password=passwd)
    except:
        error = sys.exc_info()[0]
        print(error)
    channel = ssh.invoke_shell()
    ssh_recv_ready(channel)
    channel.send("/router/bin/ct_sign_client-1.0.1 -C1 %s -C2 %s -cec\n" % (C1, C2))
    ssh_recv_ready(channel)
    channel.send(passwd + "\n")
    output = ssh_recv_ready(channel)
    if not re.search(r"Response String", output):
        output = ssh_recv_ready(channel)
    print(output)
    ssh.close()

def keychainz():
    keyring.set_password("cimcdebug", os.getlogin(), getpass.getpass(prompt="Password: "))
    print("Saved in keyring!\nRestart script.\n")
    exit()

def main(argv):
    load_dotenv()
    try:
        opts,args = getopt.getopt(sys.argv[1:], 'k')
    except Exception as err_msg:
        print(err_msg)
        exit()
    for opt,arg in opts:
        if opt in ('-k', '--keychain'):
            keychainz()
    challengeString = []

    if os.getenv('ts'):
        ts = os.getenv('ts').split(':')
        print("Loaded servers %s from env: %s" % (len(ts), ts))
    else:
        ts = input("Server: ")
    server = ts[randint(0,len(ts)-1)]
    print('Selected server: %s' % server)
    user = os.getlogin()
    print("ctrl+c to end input.\nInput challenge: ")
    while True:
        try:
            line = input()
        except KeyboardInterrupt:
            break
        else:
            if line == "":
                continue
            elif line.lower() == "help":
                print_help()
            else:
                challengeString.append(line)
    C1, C2 = get_challenge(challengeString)
    print("\nssh %s@%s" % (user, server))

    if keyring.get_password("cimcdebug", user):
        passwd = keyring.get_password("cimcdebug", user)
    else:
        try:
            passwd = getpass.getpass(prompt="ctrl+c to exit\nPassword: ")
        except KeyboardInterrupt:
            exit()
    send_command(server, user, passwd, C1, C2)
    exit()

if __name__=="__main__":
    main(sys.argv[1:])
