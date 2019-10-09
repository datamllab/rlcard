import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="rlcard",
    version="0.1",
    author="Data Analytics at Texas A&M (DATA) Lab",
    author_email="khlai037@tamu.edu",
    description="A Toolkit for Reinforcement Learning in Card Games",
    url="https://github.com/datamllab/rlcard",
    keywords=["Reinforcement Learning", "game", "RL", "AI"],
    packages=setuptools.find_packages(),
    install_requires=[
        'tensorflow>=1.14,<2.0',
        'tensorflow_probability==0.7.0',
        'dm-sonnet==1.35',
        'numpy>=1.16.3',
        'matplotlib>=3.0'
    ],
    requires_python='>=3.5',
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
