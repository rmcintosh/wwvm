from setuptools import setup

setup(
    name="wwvm",
    version="0.0.1-dev",
    packages=["wwvm", ],
    entry_points={
        "console_scripts": ["wwvm=wwvm.__main__:main"],
    }
    # long_description=open("README.txt").read(),
)
