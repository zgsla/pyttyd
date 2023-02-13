import json

from fastapi import APIRouter, Depends

from pyttyd import crud
from pyttyd.depends import CryptoDepend, to_dict
from pyttyd.schema import CommonResponse, BaseResponse

router = APIRouter(
    prefix="/ssh",
    tags=['ssh']
)


def _ellipsis(name):
    if len(name) > 5:
        return name[:3] + '...' + name[-2:]
    return name


@router.get("/", response_model=CommonResponse)
async def ssh(q: str = None, cryptor: CryptoDepend = Depends(CryptoDepend)):
    if cryptor.token:
        ssh_id = cryptor.decrypt(cryptor.token)
        data = crud.get_conn(ssh_id, q=q)
        data = to_dict(data)
        data['ellipsis'] = _ellipsis(data['name'])

    else:
        data = crud.get_conns(q=q)
        data = [to_dict(row) for row in data]

        for i in data:
            i['ellipsis'] = _ellipsis(i['name'])

    return {
        'data': cryptor.encrypt(json.dumps(data).encode())
    }


@router.post("/", response_model=CommonResponse)
async def ssh(*, cryptor: CryptoDepend = Depends(CryptoDepend)):

    # data = cryptor.decrypt(cryptor.token)
    item = cryptor.json()
    lastrowid = crud.create_conn(item)
    return {
        'data': cryptor.encrypt(str(lastrowid).encode())
    }


@router.put("/", response_model=CommonResponse)
async def ssh(cryptor: CryptoDepend = Depends(CryptoDepend)):
    item = cryptor.json()
    rowcount = crud.update_conn(item)
    return CommonResponse(
        data=cryptor.encrypt(str(rowcount).encode())
    )


@router.delete("/", response_model=BaseResponse)
async def ssh(cryptor=Depends(CryptoDepend)):

    item = cryptor.json()
    crud.delete_conn(item)
    return BaseResponse()
