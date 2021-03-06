import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    author = 'Matt Groot',
    author_email = '',
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Topic :: Utilities',
        'License :: GNU GENERAL PUBLIC LICENSE :: Version 3',
    ],
    description = ('A Rasp of Sand Helper Tool'),
    entry_points = {
        'console_scripts': [
            'aros = aros.aros:main',
        ],
    },
    include_package_data = True,
    install_requires = [
        'ruamel.yaml==0.15.100',
        # 'requests==2.20.1',
    ],
    keywords = 'aros rasp of sand generator',
    license = 'GPL3',
    long_description = read('README.md'),
    long_description_content_type='text/markdown',
    name = 'aros',
    packages = find_packages(),
    python_requires = '>=3.5',
    url = 'https://github.com/wmgroot/aros',
    version = '1.1.0',
)
