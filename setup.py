from setuptools import setup, find_packages

setup(name='OpenBCI_Python',
      version='1.0.2',
      description='A lib for controlling OpenBCI Devices',
      author='AJ Keller',
      author_email='pushtheworldllc@gmail.com',
      license='MIT',
      packages=find_packages(),
      install_requires=['numpy==1.9.2', 'pylsl==1.10.4', 'python-osc==1.6.3', 'pyserial==2.7', 'requests==2.7.0', 'six==1.9.0', 
                        'socketIO-client==0.6.5', 'websocket-client==0.32.0', 'wheel==0.24.0', 'Yapsy==1.11.23', 'xmltodict'],
      url='https://github.com/openbci/openbci_python',  # use the URL to the github repo
      download_url='https://github.com/openbci/openbci_python/archive/v1.0.2.tar.gz',
      keywords=['device', 'control', 'eeg', 'emg', 'ekg', 'ads1299', 'openbci', 'ganglion', 'cyton', 'wifi'],
      zip_safe=False)
