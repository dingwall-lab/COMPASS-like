import sys
import os
import argparse
import pandas as pd
import math
import time

parser = argparse.ArgumentParser(description="Counts like and unlike terms")
parser.add_argument('-a', '--inputA', help = 'The first nextLine-delimited list of terms (A)', required = True)
parser.add_argument('-b', '--inputB', help = 'The second nextLine-delimited list of terms (B)', required = True)
parser.add_argument('-o', '--outputDirectory', help = 'Folder in which the output files will be located.', required = True)
args = vars(parser.parse_args())

def main():
    dfA = pd.read_csv(args["inputA"])
    dfB = pd.read_csv(args["inputB"])
    dfA = dfA.sort_values(by = "Symbol")
    dfB = dfB.sort_values(by = "Symbol")

    outputA = []
    outputB = []
    outputShared = []
    outputA.append(list(dfA.columns.values))
    outputB.append(list(dfB.columns.values))
    outputShared.append(list(dfA.columns.values))

    shared = []
    count = 0
    for i in range(len(dfA.iloc[:,1])):
        if dfA.iloc[i,1] in list(dfB.iloc[:,1]):
            outputShared.append(list(dfA.iloc[i,]))
            shared.append(dfA.iloc[i,1])
            count += 1

    for i in range(len(dfA.iloc[:,1])):
        if dfA.iloc[i,1] not in shared:
            outputA.append(list(dfA.iloc[i,]))

    for i in range(len(dfB.iloc[:,1])):
        if dfB.iloc[i,1] not in shared:
            outputB.append(list(dfB.iloc[i,]))

    print "Number of terms in first input:\t", len(dfA.iloc[:,1])
    print "Number of terms in second input:\t", len(dfB.iloc[:,1])
    print "Number of shared terms:\t\t", count

    outputA = pd.DataFrame(outputA)
    outputB = pd.DataFrame(outputB)
    outputShared = pd.DataFrame(outputShared)
    fileNameA = args["inputA"].split('\\')[-1][:-4]
    fileNameB = args["inputB"].split('\\')[-1][:-4]

    os.chdir(args["outputDirectory"])
    outputShared.to_csv(fileNameA + '_' + fileNameB + '_shared_terms.csv', index = False, header = False)
    outputA.to_csv(fileNameA + '_' + fileNameB + '_first_only_terms.csv', index = False, header = False)
    outputB.to_csv(fileNameA + '_' + fileNameB + '_second_only_terms.csv', index = False, header = False)

time1 = time.time()
main()
time2 = time.time()
sys.stdout.write("\nTime elapsed: " + str(time2 - time1) + " s.\n")
