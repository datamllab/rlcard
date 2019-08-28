import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="rlcard",
    version="0.0.1",
    author="Data Analytics at Texas A&M (DATA) Lab",
    author_email="daochen.zha@tamu.edu",
    description="A platform of Reinforcement learning on card games",
    #url="https://github.com/pypa/sampleproject",
    keywords=["Reinforcement", "Game", "RL"],
    packages=setuptools.find_packages(),
    install_requires=[
        'numpy',
    ],
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)