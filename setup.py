#!/usr/bin/env python

import sys
from setuptools import setup

install_requires = [
    'Twisted>=16.2.0',
]

setup(
    name='nanodlna',
    version='0.1.0',
    description='A minimal UPnP/DLNA media streamer',
    long_description='nano-dlna is a command line tool that allows you to play a local video file in your TV (or any other DLNA compatible device)',
    author='Gabriel Magno',
    author_email='gabrielmagno1@gmail.com',
    url='https://github.com/gabrielmagno/nano-dlna',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
	'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Multimedia :: Sound/Audio',
        'Topic :: Multimedia :: Video',
        'Topic :: Utilities'
    ],
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

