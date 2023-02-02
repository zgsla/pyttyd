from sqlalchemy import select

from pyttyd.model import engine, tb_ssh_connect


def get_conn(ssh_id: str):
    with engine.connect() as conn:
        res = conn.execute(select(tb_ssh_connect).where(
            tb_ssh_connect.c.id == ssh_id
        ))
        data = res.fetchone()
    return data


def get_conns():
    with engine.connect() as conn:
        res = conn.execute(select(tb_ssh_connect))
        data = res.fetchall()
    return data
