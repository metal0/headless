from setuptools import setup, find_packages

setup(
	name='headless.client',
	version='0.0.1',
	packages=find_packages('src/'),
	package_dir={'': 'src'},
	url='https://github.com/ostoic/pont',
	license='GPLv3',
	author='Shaun Ostoic',
	author_email='ostoic@uwindsor.ca',
	description=''
)
