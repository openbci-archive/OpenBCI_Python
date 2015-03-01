
from yapsy.IPlugin import IPlugin

class PluginPrint(IPlugin):
	# args: passed by command line
	def activate(self, args):
		print "Print activated"
		# tell outside world that init went good
		return True
    
	def deactivate(self):
		print "Print Deactivated"
	
	def show_help(self):
		print "I do not need any parameter, just printing stuff."
	
	# called with each new sample
	def __call__(self, sample):
		sample_string = "ID: %f\n%s\n%s" %(sample.id, str(sample.channel_data)[1:-1], str(sample.aux_data)[1:-1])
		print "---------------------------------"
		print sample_string
		print "---------------------------------"
		
		# DEBBUGING
		# try:
		#     sample_string.decode('ascii')
		# except UnicodeDecodeError:
		#     print "Not a ascii-encoded unicode string"
		# else:
		#     print sample_string
		