import csv
import time

class csv_collect(object):
	def __init__(self, file_name="collect.csv", delim = ","):
		self.file_name = file_name
		self.start_time = time.time()
		self.delim = delim

		open(self.file_name, 'w').close()

	def __call__(self, sample):
		t = time.time() - self.start_time

		#Print timeSinceStart|Sample Id
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




			

    