
About
=====
cmcdbg is used for automatically extracting the CIMC debug challenge string from a block of text and retrieving the challenge response.

Keychain can be optionally used. Depending on the platform, passwords will be saved to either (macOS) Keychain Access or (Windows) Windows Credential Locker.

Usage
=====
A list of servers can be stored in '.env' as variable 'ts', multiple servers can be added by separating them with ':'.

> ts=server1:1.1.1.1:server3.example.org

Recommended to save password to Keychain with `cmcdbg.py -k`.
