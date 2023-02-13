from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from pyttyd import __template__
from pyttyd.crypto import rsa_key
from pyttyd.crud import get_conns

router = APIRouter(
    prefix="",
    tags=['html']
)

template = Jinja2Templates(directory=__template__)
publickey = rsa_key.pb_text.decode('utf8')


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return template.TemplateResponse(
        "index.html",
        context={
            'request': request,
            'publickey': publickey
        }
    )


@router.get("/ssh/connect", response_class=HTMLResponse)
async def ssh(request: Request):
    return template.TemplateResponse(
        "terminal.html",
        context={
            'request': request,
            'publickey': publickey
        }
    )
