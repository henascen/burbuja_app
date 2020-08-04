import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "burbuja_app",
    version = "0.0.1",
    author = "grupo bicion",
    description = ("Una aplicación que califica examenes de tipo burbuja"),
    keywords = "examen calificar visión artificial",
    packages=['procesador'],
    long_description=read('README'),
)