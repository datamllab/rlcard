import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="rlcard",
    version="0.0.1",
    author="Data Analytics at Texas A&M (DATA) Lab",
    author_email="khlai037@tamu.edu",
    description="A Toolkit for Reinforcement Learning in Card Games",
    url="https://github.com/datamllab/rlcard",
    keywords=["Reinforcement Learning", "game", "RL", "AI"],
    packages=setuptools.find_packages(),
    install_requires=[
        'tensorflow',
    ],
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
