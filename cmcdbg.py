#!/usr/bin/env python3
import paramiko
import os
import sys
import re
import time
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


def get_challenge(challengeString):
    C1C2 = []
    if len(challengeString) == 2 or (len(challengeString) == 3 and challengeString[-1] == 'DONE.'):
        if len(challengeString[0]) == 64 and len(challengeString[1]) in (14,16):
            C1C2.append(challengeString[0])
            C1C2.append(challengeString[1])
    else:
        for line in challengeString:
            if re.search(r"^\*", line):
                continue
            elif re.search(r"^DONE\.", line):
                break
            else:
                C1C2.append(line)
    return C1C2


def ssh_recv_ready(channel):
    n = 0
    while not channel.recv_ready() or n < 3:
        time.sleep(.1)
        n = n+1
    output = channel.recv(9999)
    return output


def init_channel(server, user, passwd):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    while True:
        try:
            print(f"Connecting to {server} as {user}")
            ssh.connect(hostname=server, username=user, password=passwd)
            break
        except paramiko.ssh_exception.AuthenticationException:
            print("Check your password or try a different server.")
            passwd = getpass("Password: ")
        except:
            error = sys.exc_info()[0]
            print(error)
            exit()
    print(f"Successfully logged into {server}")
    channel = ssh.invoke_shell()
    return channel


def send_command(server, user, passwd, C1, C2):
    channel = init_channel(server, user, passwd)
    output = ssh_recv_ready(channel)
    n = 0
    ready = False
    while not ready or n < 3:
        for line in output.decode().split('\n'):
            if re.search(r' ~]\$ ', line):
                ready = True
                break
        if ready:
            break
        else:
            output = ssh_recv_ready(channel)
            n = n+1
    print(f'Sending challenge: /router/bin/ct_sign_client-1.0.1 -C1 {C1} -C2 {C2} -cec')
    channel.send(f"/router/bin/ct_sign_client-1.0.1 -C1 {C1} -C2 {C2} -cec\n")
    output = ssh_recv_ready(channel)
    ready = False
    n = 0
    while not ready or n < 3:
        for line in output.decode().split('\n'):
            if re.search(rf'{user} password:', line):
                ready = True
                break
        if ready:
            break
        else:
            output = ssh_recv_ready(channel)
            n = n+1
    print('Sending password')
    channel.send(passwd + "\n\n")
    output = ssh_recv_ready(channel)
    print('Awaiting challenge response...')
    result = False
    n = 0
    while not result or n < 3:
        for line in output.decode().split('\n'):
            if re.search(r'^Response String', line):
                result = True
                break
        if result:
            break
        else:
            output = ssh_recv_ready(channel)
            n = n+1
    print('\n')
    os.system('cls' if sys.platform in ('win32', 'nt') else 'clear')
    for line in output.decode().split('\n'):
        if ' ~]$' not in line:
            print(line)
    print('\n')


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
            exit()
    challengeString = []

    if os.getenv('ts'):
        ts = os.getenv('ts').split(':')
        print(f"\nLoaded servers {len(ts)} from env: {ts}")
    else:
        ts = input("Server: ")
    server = ts[randint(0,len(ts)-1)]
    print(f'Selected server: {server}')
    user = os.getlogin()
    print("ctrl+c to end input. Including 'DONE.' also ends input (not required).\nInput challenge: ")
    while True:
        try:
            line = input()
        except KeyboardInterrupt:
            break
        else:
            if line == "DONE.":
                challengeString.append(line)
                break
            elif line.strip() == "" or len(line) < 14:
                continue
            else:
                challengeString.append(line)
    C1, C2 = get_challenge(challengeString)

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
