from setuptools import setup, find_packages


def read_requirements():
    """
    Read requirements from requirements.txt
    :return: list of dependency packages
    """
    with open("requirements.txt", "r") as f:
        return f.read().splitlines()


# Read the README file for the long description
def read_readme():

    with open("README.md", "r", encoding="utf-8") as f:
        return f.read()


setup(
    name="voyager-sdk",
    version="0.1.0",
    author="MSK CMO",
    author_email="ivkovics@mskcc.org",
    description="A Python SDK for Voyager SDK.",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/mskcc/voyager-sdk",
    packages=find_packages(),  # Automatically find packages in the directory
    install_requires=read_requirements(),  # Install dependencies from requirements.txt
    entry_points={
        "console_scripts": [
            "voyager-sdk=main:main",  # Command-line executable
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",  # Specify Python version compatibility
)
