
from setuptools import setup
setup(
    name='pyttyd',
    install_requires=['fastapi', 'uvicorn', 'websockets'],
    include_package_data=True,  # 包含静态文件
)
