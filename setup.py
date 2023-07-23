import setuptools

with open("README.md", "r") as fh:
	long_description = fh.read()

setuptools.setup(
	name='WorldD',
	version='0.12',
	author="Aleks Baran",
	author_email="legominefan@gmail.com",
	description="Level editor made specifically for pygame games",
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://github.com/NotMEE12/WorldD",
	packages=['WorldD'],
	requires=['pygame', 'tomlkit'],
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
	package_dir={'WorldD': 'src/WorldD'},
	package_data={'WorldD': ['*.toml']}
)