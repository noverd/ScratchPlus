from setuptools import setup
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")
setup(name='scratchplus',
      version='1.1.1',
      description='API wrapper for scratch',
      packages=['scratchplus'],
      author_email='thefinalspacestudio@gmail.com',
      author="gagarinten",
      zip_safe=False,
      url='https://github.com/noverd/ScratchPlus',
      install_requires=["requests",
                        "websocket-client", "pymitter", "bs4"],
      long_description=long_description,
      long_description_content_type='text/markdown'
      )