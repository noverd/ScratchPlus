from setuptools import setup
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()
setup(name='scratchplus',
      version='0.99',
      description='API wrapper for scratch',
      packages=['scratchplus'],
      author_email='thefinalspacestudio@gmail.com',
      author="gagarinten",
      zip_safe=False,
      url='https://github.com/noverd/ScratchPlus',
      install_requires=["requests",
                        "websocket", "pymitter"],
      long_description=long_description,
      long_description_content_type='text/markdown'
      )