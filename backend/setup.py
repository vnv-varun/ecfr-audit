#!/usr/bin/env python3

from setuptools import setup, find_packages
import os

# Read README from the parent directory
with open(os.path.join(os.path.dirname(__file__), '..', 'README.md'), 'r', encoding='utf-8') as f:
    long_description = f.read()

with open('requirements.txt', 'r', encoding='utf-8') as f:
    requirements = f.read().splitlines()

setup(
    name="ecfr-analyzer",
    version="0.1.0",
    author="DOGE Team",
    description="A tool to analyze the Electronic Code of Federal Regulations (eCFR)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/username/ecfr",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'ecfr-analyzer=backend.main:main',        # Main command for the analyzer
            'ecfr-bulk=backend.processors.bulk_process:main',  # Bulk processing command
            'ecfr-seed=backend.processors.bulk_to_db:main',  # Database seeding command
            'ecfr-scrape=backend.processors.scraper:main',  # Web scraper command
        ],
    },
    scripts=[
        'bin/ecfr-bulk',
        'bin/ecfr-seed',
        'bin/ecfr-scrape',
    ],
)