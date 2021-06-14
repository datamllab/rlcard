import setuptools

with open("README.md", "r", encoding="utf8") as fh:
    long_description = fh.read()

extras = {
    'torch': ['torch', 'GitPython', 'gitdb2', 'matplotlib'],
}

def _get_version():
    with open('rlcard/__init__.py') as f:
        for line in f:
            if line.startswith('__version__'):
                g = {}
                exec(line, g)
                return g['__version__']
        raise ValueError('`__version__` not defined')

VERSION = _get_version()

setuptools.setup(
    name="rlcard",
    version=VERSION,
    author="Data Analytics at Texas A&M (DATA) Lab",
    author_email="daochen.zha@tamu.edu",
    description="A Toolkit for Reinforcement Learning in Card Games",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/datamllab/rlcard",
    keywords=["Reinforcement Learning", "game", "RL", "AI"],
    packages=setuptools.find_packages(exclude=('tests',)),
    package_data={
        'rlcard': ['models/pretrained/leduc_holdem_cfr/*',
                   'games/uno/jsondata/action_space.json',
                   'games/limitholdem/card2index.json',
                   'games/leducholdem/card2index.json',
                   'games/doudizhu/jsondata.zip',
                   'games/uno/jsondata/*',
                   ]},
    install_requires=[
        'numpy>=1.16.3',
        'termcolor'
    ],
    extras_require=extras,
    requires_python='>=3.6',
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
