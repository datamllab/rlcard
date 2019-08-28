import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="rlcard",
    version="0.0.1",
    author="DATA lab",
    author_email="author@example.com",
    description="A platform of Reinforcement learning on card games",
    long_description='A platform of Reinforcement learning on card games',
    long_description_content_type="text/markdown",
    #url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)