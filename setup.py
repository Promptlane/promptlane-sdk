from setuptools import setup, find_packages

setup(
    name="promptlane-sdk",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
        "sqlalchemy>=1.4.0",
        "pydantic>=1.8.0",
        "python-dotenv>=0.15.0",
    ],
    author="PromptLane Team",
    author_email="team@promptlane.ai",
    description="SDK for interacting with PromptLane",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/promptlane/promptlane-sdk",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
) 