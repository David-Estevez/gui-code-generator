from setuptools import setup
from os.path import normpath

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='gui-code-generator',
    version='0.0.1',
    url='https://github.com/David-Estevez/gui-code-generator',
    license='',
    author='def',
    author_email='',
    description='Generate Python code to use a PySide/PyQt UI from a XML .ui file',
    packages=['gui_code_generator'],
    package_dir={'gui_code_generator': normpath('./gui_code_generator')},
    install_requires=requirements,
    entry_points={'gui_scripts': 'gui-code-generator=gui_code_generator.gui_code_generator:main.start'} # See https://pypi.python.org/pypi/begins/0.8#entry-points
)
