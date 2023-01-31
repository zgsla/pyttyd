import os

import uvicorn
from pyttyd import __basepath__


def main():
    uvicorn.run(
        'pyttyd.webapp:app',
        reload=True,
        reload_dirs=__basepath__,
        # ssl_keyfile=os.path.join(__basepath__, 'ca-key.pem'),
        # ssl_certfile=os.path.join(__basepath__, 'ca.crt'),
        # ssl_keyfile_password='passphrase'
    )
