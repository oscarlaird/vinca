import setuptools

setuptools.setup(
	name="vinca",
	version="130",
	author="Oscar Laird", 
	data_files = [('man/man1', ['vinca.1'])],
	include_package_data = True,
	install_requires = ['fire'],
	packages=setuptools.find_packages(),
	scripts=[
	    'scripts/vinca',
	    'scripts/vinca_debug',
	   ]
)
