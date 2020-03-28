from distutils.core import setup

setup(
    name='autocontainer',
    packages=['src'],
    version='1.0.0',
    license='MIT',
    description='A modern typing based service container and dependency injector.',
    author='Omran Jamal',
    author_email='o.jamal97@gmail.com', 
    url='https://github.com/Hedronium/autocontainer',
    download_url='https://github.com/Hedronium/autocontainer/archive/v_10.tar.gz',
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
