#!/usr/bin/env python3
import keyring
import os
import re
import sys
from getpass import getpass
from keyring.errors import PasswordSetError


def clean_path(file):
    if re.search(r'^\./', file) and re.search(r'\.py$', file):
        file = file[2:len(file)-3]
    elif re.search(r'^\./', file):
        file = file[2:]
    elif re.search(r'\.py', file):
        file = file[-3:]
    else:
        file = file
    return file


def set_creds(file):
    file = clean_path(file)
    try:
        keyring.set_password(file, os.getlogin(), getpass(prompt="Password: "))
    except PasswordSetError as err_msg:
        print(f"Unable to set password: {err_msg}")
        exit()
    except KeyboardInterrupt:
        exit()
    except Exception as err_msg:
        print(f'Error: {err_msg}')
    if sys.platform == 'darwin':
        print("Saved to keychain.")
    elif sys.platform == 'win32':
        print("Saved to Windows Credential Locker.")
    else:
        # Catch all if some unknown OS is compatible with keyring
        print("Saved to KWallet/Secret Service/etc.")
    get_creds(file)


def get_creds(file):
    file = clean_path(file)
    passwd = keyring.get_password(file, os.getlogin())
    return passwd
