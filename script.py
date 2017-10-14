import os
import shutil
import sys

path = '/mnt/files/Movies/'
#path = '/home/jacob/test/'

for foldername, subfolders, filenames in os.walk(path):
	print foldername
	print filenames
	for filename in filenames:
		#shutil.move(foldername + '/' + filename, '../' + filename)
		os.rename(foldername + '/' + filename, path + filename)
