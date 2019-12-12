## Setup

* Install python3 and python3-pip

* (Optional) Setup virtualenv

* Install python modules with `pip install -r requirements.txt`

* (Optional) Store servers list in .env

* (Optional) Store password in keychain with '-k' option

* (Optional) Enable automatic clipboard copy from/to with .env


## About
cmcdbg is used for automatically extracting the CIMC debug challenge string from a user provided block of text and retrieving the challenge response. The tool utilizes paramiko to connect to a server and remotely execute a script to generate a challenge response string. The tool handles most garbage input, with a few corner cases where it fails; but otherwise no care is needed to copy 'Exactly between the lines'.

Keychain can be optionally used. Depending on the platform, passwords will be saved to either (macOS) Keychain Access or (Windows) Windows Credential Locker.

Added automatic clipboard copy from and to.

This tool is mostly useless to people outside of my place of employment.

## Usage
A list of servers can be stored in '.env' as variable 'ts', multiple servers can be added by separating them with ':'. A single server can also be specified if the .env variable is not found.

> ts=server1:1.1.1.1:server3.example.org:1.1.1.2

Automatic clipboard copy from/to can be enabled with '.env' variable 'clipboard=True'. The challenge response string is still printed out even if this option is enabled. 

> clipboard=True

