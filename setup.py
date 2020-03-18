import setuptools

with open("README.md", "r", encoding="utf8") as fh:
    long_description = fh.read()

extras = {
    'torch': ['torch>=1.3'],
    'tensorflow': ['tensorflow>=1.14,<2.0', 'tensorflow_probability==0.7.0']
}

setuptools.setup(
    name="rlcard",
    version="0.1.12",
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
                   'games/simpledoudizhu/jsondata/*'
                   ]},
    install_requires=[
        'numpy>=1.16.3',
        'matplotlib>=3.0',
        'termcolor',
    ],
    extras_require=extras,
    requires_python='>=3.5',
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
