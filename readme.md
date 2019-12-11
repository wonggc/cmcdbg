## Setup

* Install python3 and python3-pip

* (Optional) Setup virtualenv

* Install python modules with `pip install -r requirements.txt`

* (Optional) Store servers list in .env


## About
cmcdbg is used for automatically extracting the CIMC debug challenge string from a user provided block of text and retrieving the challenge response. The tool utilizes paramiko to connect to a server and remotely execute a script to generate a challenge response string.

Keychain can be optionally used. Depending on the platform, passwords will be saved to either (macOS) Keychain Access or (Windows) Windows Credential Locker.

This tool is mostly useless to people outside of my place of employment.

## Usage
A list of servers can be stored in '.env' as variable 'ts', multiple servers can be added by separating them with ':'. Server can also be specified if the .env variable is not found.

> ts=server1:1.1.1.1:server3.example.org:1.1.1.2

Recommended to save password to Keychain with `cmcdbg.py -k`.
