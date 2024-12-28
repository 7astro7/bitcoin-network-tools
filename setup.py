
from setuptools import setup 

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name="bitcoin_network_tools",
    version="0.1",
    packages=["bitcoin_network_tools"],
    install_requires=[
        "requests",
        "dnspython"
    ],
    entry_points={
        "console_scripts": [
            "bitcoin_network_tools=bitcoin_network_tools.cli:main",
        ],
    },
    author="Zachary A. Kraehling",
    author_email="zak@zakkraehling.net",
    description="A wrapper for the Bitnodes API.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    test_suite="bitcoin_network_tools.tests",
    url="https://github.com/7astro7/bitcoin_network_tools",
    project_urls={"Tracker": "https://github.com/7astro7/bitcoin-network-tools/issues", 
                    "Source": "https://github.com/7astro7/bitcoin_network_tools"
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Internet :: WWW/HTTP",
    ],
    python_requires=">=3.6",
    keywords=[
        "bitcoin",
        "blockchain",
        "cryptocurrency",
        "network analysis",
        "bitnodes",
        "api",
        "tools",
        "python",
        "development",
        "crypto",
        "financial technology",
        "decentralized networks",
    ],
    platforms=["Any"]
    )
