# GoogleWorkspaceMailboxDownload

Convenience script to download Google Workspace user mailboxes through the official Email Audit API. Works with python3.

This script uses an old email audit API that allows exporting even suspended people's mailbox contents, as long as you are the admin of the workspace.

Based on Google's documentation at https://developers.google.com/admin-sdk/email-audit/download-mailbox

## Caveats

The authentication the script uses to access the Google Data API requires a browser-based consent approval. This means that to get the right temporary credentials, you will need to FIRST run this script on a local computer with a browser installed. When you run the mbox.py script for the first time, it will pop up a browser window, you will have to authenticate with your google workspace admin user, then it will save the credentials in credentials.json, and you can copy the whole shebang to another computer and run the rest of the operations there.

Errors: frequently Google returns a 500 Internal Error. There is no rhyme nor reason when and for what. The same request will complete a minute or a day later. Try again later.

## Installation

This is a python script, it works with the current version 3 of python.

### DInstall python dependencies

```
# the public version is old and is missing a str/bytes fix so you need to download the latest:
pip3 install -e git+https://github.com/dvska/gdata-python3#egg=gdata
pip3 install requests oauth2client tqdm
```

### setup GPG 1.4 and create encryption/decryption key.

You have to create a public/private key because the resulting mailbox archives are encrypted. Instructions are in Google's documentation, it has to be a PGP format ASCII-encoded RSA key. YOU HAVE TO USE GnuPG 1.4 - newer versions won't work according to Google. On a mac you could use "brew install gnupg@1.4" if you have homebrew installed.

Remember to save the passphrase you used to create the key - you will need it for the decryption.

Google allows you to override the existing encryption key in their system by uploading a key again, so you are not stuck if you don't know the passphrase of the existing key in Google. Just create a new keypair and upload the key.


### Setup access credentials in Google Cloud for the script:

1. You have to create your own google cloud app in https://console.cloud.google.com/ I call my cloud app "GoogleWorkspaceMailboxDownload"

1.1. Setup an Oauth 2 Client with a scope to access the email audit API, and download the client credentials:

Documentation is in the Google doc above. TL:DR under your google cloud project "GoogleWorkspaceMailboxDownload" create a Oauth 2.0 client ID (Desktop type). Add the scope "https://apps-apis.google.com/a/feeds/compliance/audit/". Download the client's secret as JSON (under APIs & Services -> Credentials) and save it as client_secrets.json.
ZZ
## Usage

1. Setup GPG, create your key, export the public key, upload the key using this script. For creation of key, please use the Google Documentation at the beginning of this readme.

NOTE: file content should be the original human readable format, the script base64 encodes it for you. The keyfile has to include the BEGIN and END lines as well.

`./mbox.py uploadkey [domainname] [keyfilename]`

2. Request a mailbox export for a user:

`./mbox.py request [domainname] [username]`

Username is without the @domainname!

You can request many users, although Google has a limit of 100 a day, so you can run into that. When you start getting ERROR and 500 Internal Error as a result codes, take a break.

3. Watch the status of your requests:

`./mbox.py status [domainname]`

This can take more than a day! you will see PENDING for a looong time.

Once you see COMPLETED, you can download the encrypted mailbox content.

4. Download the encrypted mailbox content:

`./mbox.py download [domainname] [username] [request ID]`

This will produce X number of multimegabyte binary files, which are PGP encrypted individually.

5. Decrypt the encrypted mailbox using GPG:

`gpg1 --passphrase KEYPASSPHRASE --output DECRYPTEDFILE --decrypt FILE1`

Or for multiple files, a quick shell script:

`for i in USERNAME.*; do gpg1 --passphrase KEYPASS --output $i.mbox --decrypt $i; done`

You will end up with human readable MBOX format files.


## License

Copyright (c) 2024 imre Fitos

Licensed under [MIT](https://choosealicense.com/licenses/mit/)
