import csv
import timeit

from yapsy.IPlugin import IPlugin

class PluginCSVCollect(IPlugin):
	def __init__(self, file_name="collect.csv", delim = ","):
		self.file_name = file_name
		self.start_time = timeit.default_timer()
		self.delim = delim

	def activate(self, args):
		if len(args) > 0:
			self.file_name = args[0]
		print "Will export CSV to:", self.file_name
		open(self.file_name, 'w').close()
		return True
		
	def deactivate(self):
		#TODO: flush?
		return

	def show_help(self):
		print "Optional argument: [filename] (default: collect.csv)"

	def __call__(self, sample):
		t = timeit.default_timer() - self.start_time

		#print timeSinceStart|Sample Id
		print("%f | %d" %(t,sample.id))

		row = ''
		row += str(t)
		row += self.delim
		row += str(sample.id)
		row += self.delim
		for i in sample.channel_data:
			row += str(i)
			row += self.delim
		for i in sample.aux_data:
			row += str(i)
			row += self.delim
		#remove last comma
		row += '\n'
		with open(self.file_name, 'a') as f:
			f.write(row)
