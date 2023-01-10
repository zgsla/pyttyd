import datetime

from sqlalchemy import MetaData, create_engine, Table, String, Column, PrimaryKeyConstraint, TIMESTAMP, Integer

metadata = MetaData()
engine = create_engine(
    'sqlite:///sqlite.db',
    echo=True,
    pool_recycle=120
)

tb_ssh_connect = Table(
    'tb_ssh_connect', metadata,
    Column('id', Integer, autoincrement=True),
    Column('name', String),
    Column('host', String),
    Column('port', Integer),
    Column('user', String),
    Column('password', String),

    Column('create_time', TIMESTAMP, default=datetime.datetime.utcnow),
    Column('update_time', TIMESTAMP, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow),
    PrimaryKeyConstraint('id', name='tb_ssh_connect_pk')
)


tb_ssh_connect.create(engine, checkfirst=True)


if __name__ == '__main__':
    from sqlalchemy import insert, select, update
    with engine.connect() as conn:

        # stmt = insert(tb_ssh_connect).values(name='1', host='1', port='1', user='1', password='1')
        # stmt = update(tb_ssh_connect).where(tb_ssh_connect.c.id == 1).values(
        #     name='2'
        # )
        # conn.execute(stmt)
        stmt = select(tb_ssh_connect)
        a = conn.execute(stmt)

        print(a.fetchall())
