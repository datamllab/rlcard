import setuptools

with open("README.md", "r", encoding="utf8") as fh:
    long_description = fh.read()

extras = {
    'torch': ['torch>=1.3', 'matplotlib>=3.0'],
    'tensorflow': ['tensorflow>=1.14,<2.0', 'matplotlib>=3.0'],
    'tensorflow-gpu': ['tensorflow-gpu>=1.14,<2.0', 'matplotlib>=3.0'],
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
    author_email="khlai037@tamu.edu",
    description="A Toolkit for Reinforcement Learning in Card Games",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/datamllab/rlcard",
    keywords=["Reinforcement Learning", "game", "RL", "AI"],
    packages=setuptools.find_packages(exclude=('tests',)),
    package_data={
        'rlcard': ['models/pretrained/leduc_holdem_nfsp/*',
                   'models/pretrained/leduc_holdem_cfr/*',
                   'models/pretrained/leduc_holdem_nfsp_pytorch/*',
                   'games/uno/jsondata/action_space.json',
                   'games/limitholdem/card2index.json',
                   'games/leducholdem/card2index.json',
                   'games/doudizhu/jsondata/*',
                   'games/uno/jsondata/*',
                   'games/simpledoudizhu/jsondata/*',
                   'agents/gin_rummy_human_agent/gui_cards/*',
                   'agents/gin_rummy_human_agent/gui_cards/cards_png/*',
                   'agents/gin_rummy_human_agent/gui_gin_rummy/*'
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
