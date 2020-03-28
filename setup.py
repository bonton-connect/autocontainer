from setuptools import setup

from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='autocontainer',
    packages=['src'],
    version='1.0.3',
    license='MIT',
    description='A modern typing based service container and dependency injector.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Omran Jamal',
    author_email='o.jamal97@gmail.com', 
    url='https://github.com/Hedronium/autocontainer',
    download_url='https://github.com/Hedronium/autocontainer/archive/v1.0.3.tar.gz',
    keywords=['container', 'dependency', 'injection', 'inversion', 'control', 'service'],
    python_requires='>=3.5',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Object Brokering',
        'License :: OSI Approved :: MIT License',
    ],
)
