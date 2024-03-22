import uvicorn


def main(**kwargs):
    if kwargs.get('port') is None:
        kwargs['port'] = 19310
    uvicorn.run(
        'pyttyd.app:app',
        **kwargs
    )
