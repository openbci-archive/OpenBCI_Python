"""
Extends Yapsy IPlugin interface to pass information about the board to plugins.

Fields of interest for plugins:
  args: list of arguments passed to the plugins
  sample_rate: actual sample rate of the board
  eeg_channels: number of EEG
  aux_channels: number of AUX channels
  
If needed, plugins that need to report an error can set self.is_activated to False during activate() call.

NB: because of how yapsy discovery system works, plugins must use the following syntax to inherit to use polymorphism (see http://yapsy.sourceforge.net/Advices.html):

    import plugin_interface as plugintypes

    class PluginExample(plugintypes.IPluginExtended):
       ...
"""

from yapsy.IPlugin import IPlugin


class IPluginExtended(IPlugin):
    # args: passed by command line
    def pre_activate(self, args, sample_rate=250, eeg_channels=8, aux_channels=3, imp_channels=0):
        self.args = args
        self.sample_rate = sample_rate
        self.eeg_channels = eeg_channels
        self.aux_channels = aux_channels
        self.imp_channels = imp_channels
        # by default we say that activation was okay -- inherited from IPlugin
        self.is_activated = True
        self.activate()
        # tell outside world if init went good or bad
        return self.is_activated

    # inherited from IPlugin
    def activate(self):
        print("Plugin %s activated." % (self.__class__.__name__))

    # inherited from IPlugin
    def deactivate(self):
        print("Plugin %s deactivated." % (self.__class__.__name__))

    # plugins that require arguments should implement this method
    def show_help(self):
        print("I, %s, do not need any parameter." % (self.__class__.__name__))
