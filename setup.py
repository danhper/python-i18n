from setuptools import setup  # type: ignore

setup(
    name="python-i18n",
    version="0.3.9",
    description="Translation library for Python",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Daniel Perez",
    author_email="tuvistavie@gmail.com",
    url="https://github.com/tuvistavie/python-i18n",
    download_url="https://github.com/tuvistavie/python-i18n/archive/master.zip",
    license="MIT",
    packages=["i18n", "i18n.loaders"],
    include_package_data=True,
    zip_safe=True,
    extras_require={
        "YAML": ["pyyaml>=3.10"],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries",
    ],
)
