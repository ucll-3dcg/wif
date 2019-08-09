from setuptools import setup

setup(name='wif',
      version='0.1',
      description='WIF tools',
      url='http://github.com/UCLeuvenLimburg/wif',
      author='Frederic Vogels',
      author_email='frederic.vogels@ucll.be',
      license='MIT',
      packages=['wif'],
      scripts=['bin/wif'],
      install_requires=['pillow'],
      zip_safe=False)