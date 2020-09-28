"mosromgr - Python library for managing MOS running orders"

__project__ = 'mosromgr'
__version__ = '0.1'
__python_requires__ = '>=3.6'
__author__ = 'BBC News Labs'
__author_email__ = 'bbcnewslabs@bbc.co.uk'
__url__ = 'https://bbcnewslabs.co.uk/'
__platforms__ = 'ALL'

__requires__ = ['xmltodict', 'boto3']

__extra_requires__ = {
    'test': ['pytest', 'coverage', 'mock', 'flake8'],
    'doc': ['sphinx'],
}

__classifiers__ = [
    'Development Status :: 4 - Beta',
    'Operating System :: POSIX',
    'Operating System :: Unix',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3 :: Only',
    'Topic :: Utilities',
]

__entry_points__ = {
    'console_scripts': [
        'mosromgr = mosromgr.cli.mosromgr:main',
    ]
}
