from setuptools import setup

setup(
	name='pont.client',
	version='0.0.0',
	packages=['pont', 'pont.client', 'pont.client.auth', 'pont.client.auth.net', 'pont.client.auth.net.packets',
	          'pont.client.auth.net.packets.constants', 'pont.client.world', 'pont.client.world.net',
	          'pont.client.world.net.packets', 'pont.client.world.net.packets.constants', 'pont.client.world.chat',
	          'pont.client.world.guild', 'pont.client.world.warden', 'pont.client.world.entities',
	          'pont.client.world.scripting', 'pont.client.console', 'pont.utility', 'pont.cryptography'],
	package_dir={'': 'src'},
	url='https://github.com/ostoic/pont.client',
	license='MIT',
	author='Shaun Ostoic',
	author_email='ostoic@uwindsor.ca',
	description=''
)
