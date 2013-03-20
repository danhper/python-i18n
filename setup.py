from setuptools import setup

setup(
    name='python-i18n',
    version='0.0.1',
    description='Translation library for Python',
    long_description=open('README.md').read(),
    author='Daniel Perez',
    author_email='tuvistavie@gmail',
    url='https://github.com/tuvistavie/python-i18n',
    download_url='https://github.com/tuvistavie/python-i18n/archive/master.zip',
    license='MIT',
    packages=['i18n', 'i18n.tests'],
    include_package_data=True,
    zip_safe=False,
    test_suite='i18n.tests',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'License :: MIT',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries'
    ],
)
