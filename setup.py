from setuptools import setup, find_packages

setup(name = 'OpenBCI_Python',
      version = '1.0.0',
      description = 'A lib for controlling OpenBCI Devices',
      author='AJ Keller',
      author_email='pushtheworldllc@gmail.com',
      license='MIT',
      packages=find_packages(),
      install_requires=['numpy'],
      url='https://github.com/openbci/openbci_python',  # use the URL to the github repo
      download_url='https://github.com/openbci/openbci_python/archive/v0.1.0.tar.gz',
      keywords=['device', 'control', 'eeg', 'emg', 'ekg', 'ads1299', 'openbci', 'ganglion', 'cyton', 'wifi'],  # arbitrary keywords
      zip_safe=False)
