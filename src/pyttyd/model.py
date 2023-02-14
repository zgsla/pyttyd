import os
import datetime

from pyttyd import __basepath__

from sqlalchemy import MetaData, create_engine, Table, String, Column, PrimaryKeyConstraint, TIMESTAMP, Integer

metadata = MetaData()


engine = create_engine(
    f'sqlite:///{os.path.join(__basepath__, "sqlite.db")}',
    echo=False,
    pool_recycle=120,
    implicit_returning=False
)

tb_ssh_connect = Table(
    'tb_ssh_connect', metadata,
    Column('id', String),
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
    pass
