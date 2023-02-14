import os

import uvicorn
from pyttyd import __basepath__
from pyttyd.ctl import ctl


def main():
    uvicorn.run(
        'pyttyd.app:app',
        reload=False,
        # reload_dirs=__basepath__,
        port=8221
        # ssl_keyfile=os.path.join(__basepath__, 'ca-key.pem'),
        # ssl_certfile=os.path.join(__basepath__, 'ca.crt'),
        # ssl_keyfile_password='passphrase'
    )
