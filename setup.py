from setuptools import setup, find_packages

setup(
    name="fileguardian",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pillow>=10.2.0",
        "pypdf2>=3.0.1",
        "python-magic>=0.4.27",
    ],
)