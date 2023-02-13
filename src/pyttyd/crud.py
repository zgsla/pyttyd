import uuid

from sqlalchemy import select, insert, update, delete, or_

from pyttyd.model import engine, tb_ssh_connect


def get_conn(ssh_id: str, q=None):
    with engine.connect() as conn:
        stmt = select(tb_ssh_connect).where(
            tb_ssh_connect.c.id == ssh_id
        )
        if q is not None:
            stmt = stmt.where(
                or_(
                    tb_ssh_connect.c.name.contains(q),
                    tb_ssh_connect.c.host.contains(q),
                    tb_ssh_connect.c.user.contains(q),
                )
            )
        res = conn.execute(stmt)
        data = res.fetchone()
    return data


def get_conns(q=None):
    with engine.connect() as conn:
        stmt = select(tb_ssh_connect)
        if q is not None:
            stmt = stmt.where(
                or_(
                    tb_ssh_connect.c.name.contains(q),
                    tb_ssh_connect.c.host.contains(q),
                    tb_ssh_connect.c.user.contains(q),
                )
            )
        res = conn.execute(stmt)
        data = res.fetchall()
    return data


def create_conn(item):
    with engine.connect() as conn:
        result = conn.execute(
            insert(tb_ssh_connect).values(
                id=uuid.uuid4().hex,
                name=item['name'],
                host=item['host'],
                port=item['port'],
                user=item['user'],
                password=item['password']
            )
        )
        lastrowid = result.lastrowid
    return lastrowid


def update_conn(item):
    with engine.connect() as conn:
        result = conn.execute(update(tb_ssh_connect).where(tb_ssh_connect.c.id == item['id']).values(
            name=item['name'],
            host=item['host'],
            port=item['port'],
            user=item['user'],
            password=item['password']
        ))
        rowcount = result.rowcount
    return rowcount


def delete_conn(item):
    with engine.connect() as conn:
        conn.execute(delete(tb_ssh_connect).where(tb_ssh_connect.c.id == item['id']))
