import sys, os
from distutils.core import setup

import weld

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='weld',
      version=weld.__version__,
      description='A Gmail-XMPP transport.',
      long_description=read('README'),
      classifiers=['Development Status :: 3 - Alpha',
                   'Environment :: Console',
                   'License :: OSI Approved :: MIT License',
                   'Topic :: Communications :: Email',
                   'Topic :: Communications :: Chat',
                   'Topic :: System :: Networking',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python'],
      keywords='xmpp sleekxmpp gmail email transport gateway',
      author='Lance Stout',
      author_email='lancestout@gmail.com',
      url='http://github.com/legastero/weld',
      license='MIT',
      packages=['weld'],
      scripts=['scripts/weld'])
