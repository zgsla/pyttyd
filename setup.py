
from setuptools import setup
setup(
    name='pyttyd',
    install_requires=['cryptography', 'fastapi', 'uvicorn', 'paramiko', 'websockets', 'sqlalchemy', 'jinja2'],
    include_package_data=True,  # 包含静态文件
)
