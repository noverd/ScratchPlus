from setuptools import setup

setup(name='scratchplus',
      version='0.9',
      description='API wrapper for scratch',
      packages=['scratchplus'],
      author_email='thefinalspacestudio@gmail.com',
      author="gagarinten",
      zip_safe=False,
      url='https://github.com/noverd/ScratchPlus',
      install_requires=["requests",
                        "websoket", "pymitter"])