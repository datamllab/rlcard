import setuptools

with open("README.md", "r", encoding="utf8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="rlcard",
    version="0.1.5",
    author="Data Analytics at Texas A&M (DATA) Lab",
    author_email="khlai037@tamu.edu",
    description="A Toolkit for Reinforcement Learning in Card Games",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/datamllab/rlcard",
    keywords=["Reinforcement Learning", "game", "RL", "AI"],
    packages=setuptools.find_packages(),
    package_data={
    	'rlcard': [ 'models/pretrained/leduc_holdem_nfsp/*',
    				'games/uno/jsondata/action_space.json',
    				'games/limitholdem/card2index.json',
    				'games/leducholdem/card2index.json',
    				'games/doudizhu/jsondata/*'
	]},
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
