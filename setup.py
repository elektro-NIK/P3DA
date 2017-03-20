from setuptools import setup, find_packages
from pip import get_installed_distributions
from sys import exit

PACKAGE = 'software'
NAME = 'P3DA'
DESCRIPTION = 'P3DA - RGB controller based on Arduino board'
AUTHOR = 'Bogdan Kalinin'
AUTHOR_EMAIL = 'bogdan.kalinin@gmail.com'
URL = 'https://github.com/elektro-NIK/P3DA'
VERSION = __import__(PACKAGE).__version__

if not 'pyqt5' in [i.key for i in get_installed_distributions()]:
    exit('ERROR! Install PyQt5, use:\n  pip3 install PyQt5')

setup(name=NAME,
      version=VERSION,
      url=URL,
      license='GNU GPL v.3',
      author=AUTHOR,
      author_email=AUTHOR_EMAIL,
      description=DESCRIPTION,
      long_description=open('README.md').read(),
      packages=find_packages(),
      platforms='any',
      install_requires=['pyqt5>=5.8.1',
                        'pyserial>=3.3',
                        'numpy>=1.12.1',
                        'pyqtgraph>=0.10.0'],
      entry_points={'console_scripts': ['p3da = software.main']},
      include_package_data=True,
      )
