import os


__version__ = '1.0.1'

__basepath__ = os.path.dirname(os.path.abspath(__file__))

__static__ = os.path.join(__basepath__, 'static')
__template__ = os.path.join(__basepath__, 'template')

# print('basepath: ', __basepath__)
