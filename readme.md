
About
=====
cmcdbg is used for automatically extracting the CIMC debug challenge string from a user provided block of text and retrieving the challenge response. The tool utilizes paramiko to connect to a server and remotely execute a script to generate a challenge response string.

Keychain can be optionally used. Depending on the platform, passwords will be saved to either (macOS) Keychain Access or (Windows) Windows Credential Locker.

This tool is mostly useless to people outside of my place of employment.

Usage
=====
Requires [chromedriver[(https://chromedriver.chromium.org/) to be installed
A list of servers can be stored in '.env' as variable 'ts', multiple servers can be added by separating them with ':'.

> ts=server1:1.1.1.1:server3.example.org:1.1.1.2

Recommended to save password to Keychain with `cmcdbg.py -k`.
