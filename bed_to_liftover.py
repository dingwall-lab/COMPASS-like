import sys
import os
import argparse
import math
import time

parser = argparse.ArgumentParser(description="converts a bed file to liftover input.")
parser.add_argument('-i', '--inputFile', help = 'A tab-delimited bed file.', required = True)
parser.add_argument('-o', '--outputDirectory', help = 'The folder in which the output will be stored.', required = True)
args = vars(parser.parse_args())

def main():
    f = open(args['inputFile'])
    s = f.readlines()
    f.close()

    sys.stdout.write('\n\n' + str(len(s)) + '\n\n')

    os.chdir(args['outputDirectory'])
    o = open('overlift_input.txt','w')
    for line in s:
        line = line.split('\t')
        o.write(str(line[0]) + ':' + str(line[1]) + '-' + str(line[2]))
    o.close()

time1 = time.time()
main()
time2 = time.time()
sys.stdout.write("\nTime elapsed: " + str(time2 - time1) + " s.\n")
