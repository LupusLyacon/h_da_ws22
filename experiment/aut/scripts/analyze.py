import csv
import numpy as np
import os
import sys

MAIN_DIR = 'analyzed'
act_data = []
act_rtts = []
COLUMN_NAMES = ["id","avg","std","median","0.75-qtl","0.95-qtl"]

def read_result(name_of_file):
    del act_data[:]
    del act_rtts[:]
    with open(name_of_file) as csv_file:
        rows = csv.reader(csv_file, delimiter=',')
        for row in rows:
            tmp_row = []
            for value in row:
                tmp_row.append(value)
            finite_row = []
            act_rtts.append(tmp_row.pop(0))
            for value in tmp_row:
                finite_row.append(float(value))
            act_data.append(finite_row)
    return

def make_dir(name_of_file):
    if not os.path.exists(MAIN_DIR):
        os.makedirs(MAIN_DIR)
    subdir_index = name_of_file.rfind('/')
    if subdir_index == -1:
            directory = MAIN_DIR
    else:
            directory = '{}/{}'.format(MAIN_DIR, name_of_file[:subdir_index])
    if not os.path.exists(directory):
            os.makedirs(directory)
    return '{}/{}'.format(MAIN_DIR, name_of_file)

def setup(name_of_file):
    read_result(name_of_file)
    return make_dir(name_of_file)

def calculate_qunatiles(data):
    result = []
    result.append(act_rtts.pop(0))
    result.append(np.mean(data))
    result.append(np.std(data))
    result.append(np.quantile(data, 0.5))
    result.append(np.quantile(data, .75))
    result.append(np.quantile(data, .95))
    return result

# Main

files_to_analyze = []

if len(sys.argv) > 1:
	for i in range (1, len(sys.argv)):
		dirPath = sys.argv[i]
		secLevels = [d for d in os.listdir(dirPath) if os.path.isdir(os.path.join(dirPath, d))]
		print(secLevels)
		for j in range (0, len(secLevels)):
			subdirPath = dirPath + "/" + secLevels[j]
			for f in os.listdir(subdirPath):
				files_to_analyze.append(subdirPath + "/" + f)
	for file in files_to_analyze:
		print(file)
else:
        sys.exit("Error: No handed filename - Please add name of the file that should be analyzed while calling this script")

for file in files_to_analyze:
        filepath = setup(file)
        with open(filepath,'a') as out:
                csv_out = csv.writer(out)
                csv_out.writerow(COLUMN_NAMES)
                for row in act_data:
                        csv_out.writerow(calculate_qunatiles(row))
