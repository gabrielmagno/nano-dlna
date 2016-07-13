#!/usr/bin/env python

import sys
from setuptools import setup

install_requires = [
    'Twisted>=16.2.0',
]

if sys.version_info < (2, 7):
    install_requires.append('simplejson>=3.6.3')

setup(
    name='nanodlna',
    version='0.1.0',
    description='A minimal UPnP/DLNA media streamer',
    long_description=open('README.md').read(),
    author='Gabriel Magno',
    author_email='gabrielmagno1@gmail.com',
    url='https://github.com/gabrielmagno/nano-dlna',
    license='MIT',
    #TODO
    #classifiers=[
    #    'Development Status :: 5 - Production/Stable',
    #    'Environment :: Console',
    #    'Intended Audience :: Developers',
    #    'Intended Audience :: End Users/Desktop',
    #    'Intended Audience :: Science/Research',
    #    'License :: OSI Approved :: MIT License',
    #    'Natural Language :: English',
    #    'Operating System :: OS Independent',
    #    'Programming Language :: Python',
    #    'Programming Language :: Python :: 2.7',
    #    'Programming Language :: Python :: 3.3',
    #    'Programming Language :: Python :: 3.4',
    #    'Programming Language :: Python :: 3.5',
    #    'Programming Language :: Python :: Implementation :: CPython',
    #    'Programming Language :: Python :: Implementation :: PyPy',
    #    'Topic :: Scientific/Engineering :: Information Analysis',
    #    'Topic :: Software Development :: Libraries :: Python Modules',
    #    'Topic :: Utilities'
    #],
    packages=['nanodlna'],
    package_dir={'nanodlna': 'nanodlna'},
    package_data={'nanodlna': ['templates/*.xml']},
    entry_points={
        'console_scripts': [
            'nanodlna = nanodlna.cli:run',
        ]
    },
    install_requires=install_requires
)

