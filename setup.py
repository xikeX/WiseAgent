"""
Author: Huang Weitao
Date: 2024-09-16 16:34:07
LastEditors: Huang Weitao
LastEditTime: 2024-09-17 15:26:17
Description: 
"""
from setuptools import find_packages, setup

# requirment setup
install_requires = []
with open("requirement.txt", "r", encoding="utf-8") as f:
    install_requires = [package.strip() for package in f.readlines()]
# deveopment mode
extras_require = {}
extras_require["dev"] = ["pytest", "coverage", "check-manifest"]

setup(
    name="wiseagent",  # Name of your package
    version="0.1",  # Version number
    description="A multi-agent framework with continuous learning capabilities",  # Description
    long_description=open("README.md", encoding="utf-8").read(),  # Long description, usually read from the README file
    long_description_content_type="text/markdown",  # Content type of the long description
    url="https://github.com/yourusername/your_package_name",  # URL of the project
    license="MIT",  # License
    packages=find_packages(exclude=["contrib", "docs", "tests"]),  # Packages included
    install_requires=install_requires,  # Installation dependencies
    extras_require=extras_require,  # Optional dependencies
    entry_points={  # Entry points
        "console_scripts": [
            "run-your-package=your_package_name:main",
        ],
    },
)
