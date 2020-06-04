from setuptools import setup

install_requires = ['docopt']

setup(name='t',
      version='0.1',
      description='CLI tool for removing files safely.',
      url='https://github.com/adamheins/t',
      author='Adam Heins',
      author_email='mail@adamheins.com',
      install_requires=['docopt'],
      license='MIT',
      scripts=['t'],
      python_requires='>=3',
      zip_safe=False)
