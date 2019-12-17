#!/usr/bin/env python3
import paramiko
import sys
import re
import time
import getopt
import keychainz
import pyperclip
from getpass import getpass
from random import randint


def print_help():
    print("Tool written to extract the CIMC debug string and automatically format for the CID tool.")
    print("The tool can accept newline/whitespace and will ignore any lines starting with '***'.")
    print("The tool assumes there is:\n" 
        "Only two lines for the challenge string\n"
        "Logged in username is the same as your Domain username")
    print("Pasting the follwing is allowed:")
    print("\
        ********************************************************************************\n\
        Xuz//wIAAADJvite60KPumY/m3gHwkQNgC9L9SWCIj0cRsYGpNyXEAgh74s2GTI1\n\
        VE5OVs8m+FwBFQ==\n\
        DONE.\n\
        ********************************************************************************\n\
        2$^CSSH gwong2 to x.x.x.x\n")
    print('-k | --keychain:\tStores your password (Keychain on macOS or Windows Credential Locker on Windows)\n')
    print('-n | --noclip:\tManually disable clipboard usage\n')

def get_challenge(challengeString):
    C1C2 = []
    if len(challengeString) == 2 or (len(challengeString) == 3 and challengeString[-1] == 'DONE.'):
        challengeString.sort(key=len, reverse=True)
        if len(challengeString[0]) == 64 and len(challengeString[1]) in range(14,17):
            C1C2.append(challengeString[0])
            if len(challengeString[1]) in range (14, 16):
                offset = 16-len(challengeString[1])
                pad = "=" * offset
                challengeString[1] = challengeString[1] + pad
            C1C2.append(challengeString[1])
            return C1C2
    else:
        for sindex, line in reversed(list(enumerate(challengeString))):
            if ' ' in line.strip():
                del challengeString[sindex]
         
        for line in challengeString:
            if len(C1C2) == 2:
                break
            elif re.search(r"^\*", line):
                pass
            elif len(line) == 64 or len(line) in range(14,17):
                if len(line) in range (14,16):
                    offset = 16-len(line)
                    pad = "=" * offset
                    line = line+pad
                C1C2.append(line)
        C1C2.sort(key=len, reverse=True)
        if len(C1C2) == 2 and (len(C1C2[0]) == 64 and len(C1C2[1]) in range(14,17)):
             return C1C2
    print(C1C2)
    print(f"\nNo valid challenge string found.\n\t{C1C2}\n")
    exit()


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
    print(f"Sending challenge: /router/bin/ct_sign_client-1.0.1 -C1 '{C1}' -C2 '{C2}' -cec")
    channel.send(f"/router/bin/ct_sign_client-1.0.1 -C1 '{C1}' -C2 '{C2}' -cec\n")
    output = ssh_recv_ready(channel)
    ready = False
    n = 0
    while not ready or n < 3:
        for line in output.decode().split('\n'):
            if re.search(rf'{user} password:', line):
                ready = True
                break
            if 'Invalid Challenge.' in line:
                print(f"Is this an old challenge string? Ensure this is a recent challenge string.\n\t{C1}\n\t{C2}")
                exit()
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
    response = []
    for line in output.decode().split('\n'):
        if ' ~]$' not in line:
            print(line)
            response.append(line)
    print('\n')
    if os.getenv('clipboard').lower() == 'true':
        copypasta = '\n'.join(response)
        copypasta = copypasta.split('*'*69)[1].strip()
        pyperclip.copy(copypasta)
        print(f'Copied {len(copypasta)} characters to clipboard.')


def main(argv):
    manual = False
    try:
        opts,args = getopt.getopt(sys.argv[1:], 'hkn', ['keychain', 'help', 'noclip'])
    except Exception as err_msg:
        print(err_msg)
        exit()
    for opt,arg in opts:
        if opt in ('-k', '--keychain'):
            keychainz.set_creds(__file__)
        elif opt in ('-h', '--help'):
            print_help()
            exit()
        elif opt in ('-n', '--noclip'):
            manual = True
    challengeString = []

    if os.getenv('ts'):
        ts = os.getenv('ts').split(':')
        print(f"\nLoaded {len(ts)} servers from env: {ts}")
    else:
        ts = input("Server: ")
    server = ts[randint(0,len(ts)-1)]
    print(f'Selected server: {server}')
    user = os.getlogin()

    if ImageGrab.grabclipboard():
        challenge_image = ImageGrab.grabclipboard()
        print(f'Found image {challenge_image}')
        text = pt.image_to_string(cv2.cvtColor(nm.array(challenge_image), cv2.COLOR_BGR2GRAY))
        #text = pt.image_to_string(challenge_image)
        text = text.split('\n')
        #for index, line in enumerate(text):
            #if 'DONE.' in line:
                 #start = index
                 #break
        for line in text:
            if line == 'DONE.':
                if len(challengeString) < 2:
                    pass
                else:
                    challengeString.append(line)
                    break
            elif ' ' in line:
                line = line.replace(' ', '')
                challengeString.append(line)
            elif line == "" or len(line) < 14 or line == 'e'*14:
                pass
            else:
                challengeString.append(line.strip())
        print(f'Using {challengeString}')
    elif manual == False and os.getenv('clipboard').lower() == 'true':
        clippy = pyperclip.paste()
        for line in clippy.split('\n'):
            line = line.strip(' "\'\t\r\n')
            if line == "DONE.":
                if len(challengeString) < 2:
                    pass
                else:
                    challengeString.append(line)
                    break
            elif line == "" or len(line) < 14:
                pass
            else:
                challengeString.append(line)
    else:
        print("ctrl+c to end input. Including 'DONE.' also ends input (not required).\nInput challenge: ")
        while True:
            try:
                line = input()
            except KeyboardInterrupt:
                break
            else:
                line = line.strip(' "\'\t\r\n')
                if line == "DONE.":
                    if len(challengeString) < 2:
                        pass
                    else:
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
    from dotenv import load_dotenv
    import os
    load_dotenv()
    if os.getenv('ocr'):
        try:
            import pytesseract as pt
            from PIL import Image, ImageGrab
            import numpy as nm
            import cv2
        except ImportError:
            print('OCR enabled, but pytesseract not found. Ensure it is installed with `pip list`. Proceeding without OCR')
            pass
    main(sys.argv[1:])
