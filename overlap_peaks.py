import sys
import time
import re

def isOverlap(x1, x2, y1, y2):
	return x1 <= y2 and y1 <= x2

def parseFile(fileName):
	output = open(fileName, 'r').readlines()
	return [re.compile("[:-]").split(i[:-1]) for i in output]

def main():
	if len(sys.argv) != 3 and len(sys.argv) != 4:
		sys.stdout.write("\nFORMAT: overlap_peaks.py filename1.bed filename2.bed [extension]\n\n")
		return

	bed1 = parseFile(sys.argv[1])
	bed2 = parseFile(sys.argv[2])
	extension = 0
	if len(sys.argv) == 4:
		extension = int(sys.argv[3])

	count = 0
	for i in range(len(bed1)):
		#print (i, "out of", len(bed1))
		for j in range(len(bed2)):
			if bed1[i][0] == bed2[j][0]:
				try:
					int(bed1[i][1])
					int(bed1[i][2])
					int(bed2[j][1])
					int(bed2[j][2])
				except:
					print(bed1[i][1], bed1[i][2], bed2[j][1], bed2[j][2])
					break
				if isOverlap(int(bed1[i][1]) - extension, int(bed1[i][2]) + extension, int(bed2[j][1]), int(bed2[j][2])):
					count += 1
					break
	print(count, "/", len(bed1))

start = time.time()
main()
end = time.time()
sys.stdout.write("time: " + str(end - start))