import sys
import os
import argparse
import pandas as pd
import math
import time

parser = argparse.ArgumentParser(description="Filters based on p-value, RPKM, and fold change")
parser.add_argument('-i', '--input', help = 'The csv file for the RNAseq dataset.', required = True)
parser.add_argument('-d', '--direction', help = 'Type u to select for upregulated genes in input, or type d to select for downregulated genes,' +
'or type n to skip selection by direction.', nargs = '?', default = 'n')
parser.add_argument('-f', '--foldChange', help = 'The fold change by which to filter out genes. (direction specified in --direction)', type = float, nargs = '?', default = 0)
parser.add_argument('-o', '--outputDirectory', help = 'Folder in which the output files will be located.', required = True)
parser.add_argument('-r', '--minRPKM', help = 'the minimum RPKM value allowed to be present in the output.', type = float, nargs = '?', default = 1.0)
parser.add_argument('-p', '--maxPValue', help = 'the maximum p-value allowed to be present in the output.', type = float, nargs = '?', default = 0.05)
args = vars(parser.parse_args())

def main():
    if args["direction"] == 'u':
        upDown = "Up"
    elif args["direction"] == 'd':
        upDown = "Down"
    else:
        upDown = "UpDown"
    output = []

    df = pd.read_csv(args["input"])
    df = df.sort_values(by = "Symbol")
    output.append(list(df.columns.values))

    sys.stdout.write("Progress:\n---------------------------------------------------\n")
    for i in range(df.shape[0]):
        if i % (df.shape[0] / 50) == 0:
            sys.stdout.write("#")
        if float(df.iloc[i,9]) <= args['maxPValue'] and float(df.iloc[i,5]) >= args['minRPKM'] and float(df.iloc[i,6]) >= args['minRPKM']:
            if upDown == 'UpDown':
                output.append(list(df.iloc[i,]))
            elif upDown == 'Up':
                if 2**float(df.iloc[i,7]) >= args['foldChange']:
                    output.append(list(df.iloc[i,]))
            elif upDown == 'Down':
                if 1 / (2**float(df.iloc[i,7])) >= args['foldChange']:
                    output.append(list(df.iloc[i,]))

    os.chdir(args["outputDirectory"])
    output = pd.DataFrame(output)
    fileName = args["input"].split('\\')[-1][:-4]
    output.to_csv(fileName + "_filtered_dir_" + str(args["direction"]) + "_fold_" + str(args['foldChange']) + "_rpkm_" + str(args['minRPKM']) + "_p_val_" + str(args['maxPValue']) + ".csv", index = False, header = False)

time1 = time.time()
main()
time2 = time.time()
sys.stdout.write("\nTime elapsed: " + str(time2 - time1) + " s.\n")
