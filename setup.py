import setuptools

with open("README.md", "r") as fh:
	long_description = fh.read()

setuptools.setup(
	name='WorldD',
	version='0.1',
	scripts=['src/__init__.py', 'src/main.py', 'src/options.toml'] ,
	author="Aleks Baran",
	author_email="legominefan@gmail.com",
	description="Level editor made specifically for pygame-ce",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://github.com/NotMEE12/WorldD",
	packages=setuptools.find_packages(),
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
)