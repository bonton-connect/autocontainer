from distutils.core import setup

setup(
    name='autocontainer',
    packages=['src'],
    version='1.0',
    license='MIT',
    description='A modern typing based service container and dependency injector.',
    author='Omran Jamal',
    author_email='o.jamal97@gmail.com', 
    url='https://github.com/Hedronium/autocontainer',
    download_url='https://github.com/Hedronium/autocontainer/archive/v_10.tar.gz',
    keywords=['container', 'dependency', 'injection', 'inversion', 'control', 'service'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7+',
    ],
)
