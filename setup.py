from setuptools import setup, find_packages

setup(
    name="tddr",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "moviepy>=1.0.3",
        "whisper>=1.0.0",
        "numpy>=1.19.0",
        "torch>=1.7.0",
    ],
    author="lakk1",
    author_email="laxminarayana.en@gmail.com",
    description="Video caption generator using Whisper",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/username/tddr",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
