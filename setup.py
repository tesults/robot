#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import codecs
from setuptools import setup


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return codecs.open(file_path, encoding='utf-8').read()


setup(
    name='robot-tesults',
    version='1.2.0',
    author='Tesults',
    author_email='help@tesults.com',
    maintainer='Tesults',
    maintainer_email='help@tesults.com',
    license='MIT',
    url='https://www.tesults.com/docs?doc=robot',
    description='Tesults listener for Robot Framework',
    long_description=read('README.rst'),
    long_description_content_type='text/x-rst',
    py_modules=['TesultsListener'],
    python_requires='>=2.7',
    install_requires=['tesults'],
    keywords='robot framework tesults test results automation automated dashboard reporting plugin',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Framework :: Robot Framework',
        'Topic :: Software Development :: Testing',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
    ],
    entry_points={
        'pytest11': [
            'robot-tesults = TesultsListener',
        ],
    },
)
