
from yapsy.IPlugin import IPlugin

class PluginPrint(IPlugin):
	# args: passed by command line
	def activate(self, args):
		print "I'm activated"
		# tell outside world that init went good
		return True
    
	def deactivate(self):
		print "Goodbye"
	
	def show_help(self):
		print "I do not need any parameter, just printing stuff."
	
	# called with each new sample
	def __call__(self, sample):
		print "----------------"
		print("%f" %(sample.id))
		print sample.channel_data
		print sample.aux_data