#!/usr/bin/env python3
import paramiko
import os
import re
import time
import sys
import getopt
import keychainz
from getpass import getpass
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
        "2$^CSSH gwong2 to x.x.x.x\n")
    print('-k | --keychain:\tStores your password (Keychain on macOS or Windows Credential Locker on Windows)')
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
    while True:
        try:
            ssh.connect(hostname=server, username=user, password=passwd)
            break
        except paramiko.ssh.exception.AuthenticationException:
            print("Check your password or try a different server.")
            passwd = getpass("Password: ")
        except:
            error = sys.exc_info()[0]
            print(error)
    print(f"Logged into {server}")
    channel = ssh.invoke_shell()
    ssh_recv_ready(channel)
    print("Sending challenge.")
    channel.send(f"/router/bin/ct_sign_client-1.0.1 -C1 {C1} -C2 {C2} -cec\n")
    ssh_recv_ready(channel)
    channel.send(passwd + "\n")
    print("Waiting for challenge response.")
    output = ssh_recv_ready(channel)
    while True:
        try:
            if not re.search(r"Response String", output.decode()):
                output = ssh_recv_ready(channel)
            else:
                break
        except TypeError:
            pass
    ssh.close()
    for line in output.decode().split('\n'):
        if ' ~]$' not in line:
            print(line)


def main(argv):
    load_dotenv()
    try:
        opts,args = getopt.getopt(sys.argv[1:], 'hk', ['keychain', 'help'])
    except Exception as err_msg:
        print(err_msg)
        exit()
    for opt,arg in opts:
        if opt in ('-k', '--keychain'):
            keychainz.set_creds(__file__)
        elif opt in ('-h', '--help'):
            print_help()
    challengeString = []

    if os.getenv('ts'):
        ts = os.getenv('ts').split(':')
        print(f"Loaded servers {len(ts)} from env: {ts}")
    else:
        ts = input("Server: ")
    server = ts[randint(0,len(ts)-1)]
    print(f'Selected server: {server}')
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
            elif line == "DONE.":
                break
            else:
                challengeString.append(line)
    C1, C2 = get_challenge(challengeString)
    print(f"\nssh {user}@{server}")

    if keychainz.get_creds(__file__):
        passwd = keychainz.get_creds(__file__)
    else:
        try:
            passwd = getpass(prompt="ctrl+c to exit\nPassword: ")
        except KeyboardInterrupt:
            exit()
    send_command(server, user, passwd, C1, C2)
    exit()

if __name__=="__main__":
    main(sys.argv[1:])
