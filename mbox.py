#!/usr/bin/env python3
# GoogleWorkspaceMailboxDownload Copyright (c) 2024 imre Fitos

import sys
import requests
import gdata.apps.audit.service
from oauth2client import file, client, tools
from tqdm.auto import tqdm

SCOPES = ['https://apps-apis.google.com/a/feeds/compliance/audit/',]

# file download with a progress counter
def download(url, fname):
    resp = requests.get(url, stream=True)
    total = int(resp.headers.get('content-length', 0))
    with open(fname, 'wb') as file, tqdm(
            desc=fname,
            total=total,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
    ) as bar:
        for data in resp.iter_content(chunk_size=1024):
            size = file.write(data)
            bar.update(size)

def usage():
    print("""
Usage:
    mbox.py uploadkey [domainname] [keyfilename] - uploads the public key Google will use to encrypt the mailbox archives
    mbox.py status [domainname] - shows all currently running requests
    mbox.py request [domainname] [username] - request a full mailbox export for username
    mbox.py download [domainname] [username] [request ID] - download completed export into username.X files
    mbox.py deleterequest [domainname] [username] [request ID] - delete the request from Google
    """)
    exit(1)


# main 

store = file.Storage('credentials.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('client_secrets.json', SCOPES)
    creds = tools.run_flow(flow, store)

access_token, expires_in = creds.get_access_token()

if len(sys.argv) < 3:
    usage()

google = gdata.apps.audit.service.AuditService(domain=sys.argv[2])
google.additional_headers[u'Authorization'] = u'Bearer {0}'.format(access_token)
 
if sys.argv[1] == 'status':
    allreqs = google.getAllMailboxExportRequestsStatus()
    for req in allreqs:
        if req[b'status'] == b'PENDING':
            print(req[b'userEmailAddress'].decode('utf-8') + "\tPENDING")
        elif req[b'status'] == b'DELETED':
            print(req[b'userEmailAddress'].decode('utf-8') + "\tDELETED\tRequest ID: " + req[b'requestId'].decode('utf-8'))
        elif req[b'status'] == b'COMPLETED':
            print(req[b'userEmailAddress'].decode('utf-8') + "\tCOMPLETED\tRequest ID: " + req[b'requestId'].decode('utf-8'))
        else:
            print(req)

elif sys.argv[1] == 'request':
    print(google.createMailboxExportRequest(sys.argv[3], include_deleted=True))

elif sys.argv[1] == 'download':
    if len(sys.argv) < 4:
        print("Usage: mbox.py download [domainname] [username] [requestID]")
        exit(1)
    req = google.getMailboxExportRequestStatus(sys.argv[3], sys.argv[4])
    print("Downloading " + req[b'numberOfFiles'].decode('utf-8') + " files as " + sys.argv[3] + ".X")
    for i in range(0, int(req[b'numberOfFiles'])):
        download(req[str.encode('fileUrl' + str(i))].decode('utf-8'), sys.argv[3] + "." + str(i))

elif sys.argv[1] == 'uploadkey':
    with open(sys.argv[3]) as f:
        pubkey = f.read()
    print(google.updatePGPKey(pubkey.encode("utf-8")))

elif sys.argv[1] == 'deleterequest':
    print(google.deleteMailboxExportRequest(sys.argv[3], sys.argv[4]))

else:
    usage()

# eof
