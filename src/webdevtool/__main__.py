import os
import sys
import uvicorn
import asyncio

from .webapp import app


def debug():
    uvicorn.run('webdevtool.webapp:app', reload=True)


def main():
    debug()
