from setuptools import setup

setup(
    name='python-i18n',
    version='0.1.0',
    description='Translation library for Python',
    long_description=open('README.md').read(),
    author='Daniel Perez',
    author_email='tuvistavie@gmail',
    url='https://github.com/tuvistavie/python-i18n',
    download_url='https://github.com/tuvistavie/python-i18n/archive/master.zip',
    license='MIT',
    packages=['i18n', 'i18n.tests'],
    include_package_data=True,
    zip_safe=True,
    test_suite='i18n.tests',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries'
    ],
)
