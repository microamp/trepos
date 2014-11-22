# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

import trepos

setup(name="Trepos",
      version=trepos.__version__,
      description="A simple client for GitHub trending repos",
      long_description=open("README.rst").read(),
      author="James Sangho Nah",
      author_email="sangho.nah@gmail.com",
      url="https://github.com/microamp/trepos",
      packages=find_packages(),
      package_data={"": ["README.rst", "LICENSE"]},
      include_package_data=True,
      license="GNU GPL v3.0",
      zip_safe=False,
      install_requires=("Scrapy >= 0.24.4",
                        "requests >= 2.4.3",),
      classifiers=("Development Status :: 2 - Pre-Alpha",
                   "Intended Audience :: Developers",
                   "License :: OSI Approved :: GNU GPL v3.0"
                   "Operating System :: OS Independent",
                   "Programming Language :: Python",
                   "Programming Language :: Python :: 2.7",
                   "Topic :: Software Development :: Libraries",))
