from setuptools import setup

setup(name='wif',
      version='0.1',
      description='WIF tools',
      url='http://github.com/UCLeuvenLimburg/wif',
      author='Frederic Vogels',
      author_email='frederic.vogels@ucll.be',
      license='MIT',
      packages=['wif'],
      entry_points = {
            'console_scripts': [ 'wif=wif.main:main']
      },
      install_requires=['pillow', 'numpy', 'opencv-contrib-python'],
      zip_safe=False)