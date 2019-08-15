from PIL import Image, ImageDraw, ImageFont
import sys
import os
import argparse
import numpy
import scipy.stats
import math
import time
import random

parser = argparse.ArgumentParser(description="Genes at Peaks tells the user the pecentage of their selected genes that are within a certain range of a set of binding peaks.")
parser.add_argument('-g', '--geneListDir', help = 'The directory containing newline-delimited list of gene IDs.', required = True)
parser.add_argument('-f', '--geneToFBGN', help = 'A table to convert gene IDs to FBGN IDs.', required = True)
parser.add_argument('-c', '--geneCoordinates', help = 'The file from flybase the gives the coordinates for each FBGN.', required = True)
parser.add_argument('-p', '--bindingPeaks', help = 'The binding peak file.', required = True)
parser.add_argument('-w', '--wigPeaks', help = 'The wig file of peaks.', required = True)
parser.add_argument('-b', '--bgGenes', help = 'data to display all genes.', required = True)
parser.add_argument('-n', '--font', help = 'the file containing the text font', required = True)
parser.add_argument('-o', '--outputDirectory', help = 'Location of the output file.', required = True)
parser.add_argument('-d', '--distance', help = 'maximum distance from gene start site to center of nearest peak', type = float, nargs = '?', default = 5000.0)
parser.add_argument('-e', '--enhancers', help = 'a list of enhancers to filter out peaks that are not near them.', nargs = '?', default = '-')
parser.add_argument('-r', '--enhancerRange', help = 'The range at which a peak can be within in enhancer to remain in the peak list.', nargs = '?', type = float, default = 5000.0)
args = vars(parser.parse_args())

def histogram(start,stop,l,x):
    for i in range(start,stop+1):
        for j in range(l.count(i) / 200):
            sys.stdout.write('#')
        if i == x:
            sys.stdout.write('          *')
        sys.stdout.write('\n')

def locToNums(loc):
    if not (':' in loc and '..' in loc):
        return ['-']
    if 'chr' in loc:
        loc = loc[3:]
    if loc != 'NA':
        if len(loc.split('(')) > 1:
            if int(loc.split('(')[1].split(')')[0]) == -1:
                return [loc.split(':')[0], int(loc.split(':')[1].split('..')[1].split('(')[0]), int(loc.split(':')[1].split('..')[0])]
            else:
                return [loc.split(':')[0], int(loc.split(':')[1].split('..')[0]), int(loc.split(':')[1].split('..')[1].split('(')[0])]
        else:
            return [loc.split(':')[0], int(loc.split(':')[1].split('..')[0]), int(loc.split(':')[1].split('..')[1].split('(')[0])]
    else:
        return ['-']

def filterPeaks(enhancers,peaks):
    output = []
    for i in range(len(peaks)):
        for j in range(len(enhancers)):
            peakLoc = locToNums(peaks[i])
            enhancLoc = locToNums(enhancers[j])
            if peakLoc[0] == enhancLoc[0] and abs(((peakLoc[1] + peakLoc[2]) / 2.0) - ((enhancLoc[1] + enhancLoc[2]) / 2.0)) < args['enhancerRange']:
                output.append(peaks[i])
                break
    return output

def getAtPeaks(tag, l, fbgnDict, geneDict, peaks):
    count = 0
    totalGenes = 0
    o = open(tag + '_isAtPeak.csv','w')
    geneLocs = [] #the genes
    atPeak = []
    sys.stdout.write("\n\nProgress:\n--------------------------------------------------\n")
    for i in range(len(l)):
        if i % (len(l) / 50.0) < 1:
            sys.stdout.write("#")
        if l[i].strip() in fbgnDict.keys():
            temp = geneDict[fbgnDict[l[i].strip()].strip()]
            isFound = False
            geneLocs.append(temp.strip())
            for peak in peaks:
                peakCenter = (locToNums(peak)[1] + locToNums(peak)[2]) / 2.0
                if locToNums(peak)[0] == locToNums(temp)[0] and abs(peakCenter - locToNums(temp)[1]) <= args['distance']:
                    count += 1
                    isFound = True
                    break
            o.write(l[i].strip() + ',' + str(isFound) + '\n')
            atPeak.append(isFound)
            totalGenes += 1
        else:
            o.write(l[i].strip() + ',notFound\n')
    o.close()
    sys.stdout.write('\n\nTotal number of genes at peaks: ' + str(count) + '\n')
    sys.stdout.write('Total number of found genes: ' + str(totalGenes) + '\n')
    sys.stdout.write('Percentage:' + str(round((count / float(totalGenes))*10000) / 100.0) + '%\n\n')
    return geneLocs, atPeak, count, totalGenes

def drawGraphs(chrLenDict,oldPeaks,peaks,enhancers,wigPeaks,wigAtPeak,genes,genesAtPeak,geneNames,genesSample,fnt,d,label):
    fntInfo = ImageFont.truetype(fnt, 12)

    for key, value in chrLenDict.iteritems():
        sys.stdout.write(key + '\n')
        image = Image.new('RGB', (value / 1000, 400), (25,25,25))
        draw = ImageDraw.Draw(image, 'RGBA')

        for i in range(value/100000):
            draw.line((i*100,188,i*100,192), (255,255,255,100), 2)
            draw.text((i*100+5,184), str(i*100000), fill = (255,255,255,50), font = fntInfo)

        for i in range(25):
            draw.line((0,((i+1)*50/3.0),value / 1000,((i+1)*50/3.0)), (255,255,255,50), 1)

        if enhancers != '-':
            for line in enhancers:
                loc = locToNums(line)
                if loc[0] == key:
                    x1 = float(loc[1]) / 1000.0
                    x2 = float(loc[2]) / 1000.0
                    for i in range(401):
                        if (i / 5) % 2 == 0:
                            draw.line((x1,i,x2,i), (255,255,255,50), 1)

        if oldPeaks != '-':
            for line in oldPeaks:
                loc = locToNums(line)
                if loc[0] == key:
                    x1 = float(loc[1]) / 1000.0
                    x2 = float(loc[2]) / 1000.0
                    for i in range(401):
                        draw.line((x1,i,x2,i), (255,255,255,50), 1)

        for line in peaks:
            loc = locToNums(line)
            if loc[0] == key:
                x1 = float(loc[1]) / 1000.0
                x2 = float(loc[2]) / 1000.0
                for i in range(401):
                    draw.line((x1,i,x2,i), (0,255,0,50), 1)

        for line in wigPeaks:
            if line.split(' ')[0] == key:
                x = float(line.split(' ')[2]) / 1000.0
                y = float(line.split(' ')[3]) / 3.0
                draw.line((x,0,x,y), (200,200,200), 1)

        n = 0
        count = 0
        for line in genes:
            loc = locToNums(line)
            if loc[0] == key:
                x1 = float(loc[1]) / 1000.0
                x2 = float(loc[2]) / 1000.0
                for i in range(5):
                    if wigAtPeak[count]:
                        draw.line((x1,n % 5 * 10 + 350 + i,x2,n % 5 * 10 + 350 + i), (0,255,0), 1)
                    else:
                        draw.line((x1,n % 5 * 10 + 350 + i,x2,n % 5 * 10 + 350 + i), (255,0,0), 1)
                n += 1
            count += 1

        n = 0
        count = 0
        for line in genesSample:
            loc = locToNums(line)
            if loc[0] == key:
                x1 = float(loc[1]) / 1000.0
                x2 = float(loc[2]) / 1000.0
                for i in range(10):
                    if genesAtPeak[count]:
                        draw.line((x1,330+i,x2,330+i), (0,255,0), 1)
                        draw.text((x1,310), geneNames[count], fill = (0,255,0), font = fntInfo)
                    else:
                        draw.line((x1,330+i,x2,330+i), (255,0,0), 1)
                        draw.text((x1,310), geneNames[count], fill = (255,0,0), font = fntInfo)
                n += 1
            count += 1

        image.save(d + '\\chr' + key + '_' + label + '.png', "PNG")
    return

def getPvalue(sampleSize, genomeSize, sampleFit, genomeFit):
    sys.stdout.write('Progress:\n--------------------------------------------------\n')
    distribution = []
    for i in range(100000):
        if i % (100000/50) == 0:
            sys.stdout.write('#')
        count = 0
        for j in range(sampleSize):
            r = random.randint(1,genomeSize)
            if r <= genomeFit:
                count += 1
        distribution.append(count)
    sys.stdout.write('\n')
    histogram(min(distribution),max(distribution),distribution,sampleFit)
    mean = sum(distribution) / float(len(distribution))
    sys.stdout.write('\nMean: ' + str(mean) + '\n')
    stdev = numpy.std(distribution)
    sys.stdout.write('\nStandard deviation: ' + str(stdev) + '\n')
    z = abs(sampleFit - mean) / stdev
    sys.stdout.write('\nZ-score: ' + str(z) + '\n')
    p = scipy.stats.norm.sf(z)*2
    sys.stdout.write('\np-value: ' + str(p) + '\n')
    return p

def main():
    chrLenDict = {'2L':23011544, '2R':21146735, '3L':24543557, '3R':27905053, '4':1351857, 'X':22422847}

    if args['enhancers'] != '-':
        sys.stdout.write('Reading in list of enhancers... ')
        enhancers = open(args['enhancers'], 'r').readlines()
        sys.stdout.write('read.\n')
    else:
        enhancers = '-'

    sys.stdout.write('Reading in data for called peaks... ')
    peaks = open(args['bindingPeaks'], 'r').readlines()
    sys.stdout.write('read.\n')

    if enhancers != '-':
        oldPeaks = peaks
        peaks = filterPeaks(enhancers, peaks)
    else:
        oldPeaks = '-'

    sys.stdout.write('Reading in data for ChIP-seq binding... ')
    wigPeaks = open(args['wigPeaks'], 'r').readlines()
    sys.stdout.write('read.\n')

    sys.stdout.write('Reading in Gene ID to FBGN table... ')
    fbgn = open(args['geneToFBGN'], 'r').readlines()
    sys.stdout.write('read.\n')

    sys.stdout.write('Reading in gene coordinates table... ')
    coord = open(args['geneCoordinates'], 'r').readlines()
    sys.stdout.write('read.\n')

    sys.stdout.write('Reading in list of background genes... ')
    bgGenes = open(args['bgGenes'], 'r').readlines()
    sys.stdout.write('read.\n')

    sys.stdout.write('Creating Gene ID to FBGN dictionary... ')
    fbgnDict = {}
    for i in range(len(fbgn)):
        fbgnDict[fbgn[i].split(',')[0]] = fbgn[i].split(',')[1]
    sys.stdout.write('done.\n')

    sys.stdout.write('Creating FBGN to genomic coordinate dictionary... ')
    geneDict = {}
    for i in range(len(coord)):
        if coord[i].count('\t') > 0:
            if coord[i].split('\t')[-1].strip() == '':
                geneDict[coord[i].split('\t')[1]] = 'NA'
            else:
                geneDict[coord[i].split('\t')[1]] = coord[i].split('\t')[-1].strip()
    sys.stdout.write('done.\n')
    sys.stdout.write('Finding all genes, and determining peak proximity... ')
    genes, wigAtPeak, countAll, totalAll = getAtPeaks(args['outputDirectory'] + '\\all', bgGenes, fbgnDict, geneDict, peaks)
    sys.stdout.write('done.\n')

    os.chdir(args['geneListDir'])
    files = os.listdir(os.curdir)
    infoFile = open(args['outputDirectory'] + '\\p_values.txt', 'w')
    infoFile.write('Background Genes:\nTotal genes: ' + str(totalAll) + '\nGenes near peaks: ' + str(countAll) + '\nPercentage: ' + str(round((countAll / float(totalAll))*10000) / 100.0) + '%\n')
    for f in files:
        sys.stdout.write('Reading in list of genes to study... ')
        geneList = open(f, 'r').readlines()
        sys.stdout.write('read.\n')

        sys.stdout.write('Finding genes from within the sample, and determining peak proximity... ')
        genesSample, genesAtPeak, countSample, totalSample = getAtPeaks(args['outputDirectory'] + '\\' + f[:-4] + '_sample', geneList, fbgnDict, geneDict, peaks)
        sys.stdout.write('done.\n')

        sys.stdout.write('Calculating enrichment p-value...\n')
        #p = getPvalue(totalSample, totalAll, countSample, countAll)
        odds, p = scipy.stats.fisher_exact([[countSample,totalSample-countSample],[countAll,totalAll-countAll]])

        sys.stdout.write('file ' + f + ' p-value: ' + str(p))
        infoFile.write('\n' + f + '\np-value: ' + str(p) + '\nTotal genes: ' + str(totalSample) + '\nGenes near peaks: ' + str(countSample) + '\nPercentage: ' + str(round((countSample / float(totalSample))*10000) / 100.0) + '%\n')

        sys.stdout.write('\nDrawing graphs...\n')
        drawGraphs(chrLenDict,oldPeaks,peaks,enhancers,wigPeaks,wigAtPeak,genes,genesAtPeak,geneList,genesSample,args['font'],args['outputDirectory'], f[:-4])
        sys.stdout.write('done.\n')
    infoFile.close()

time1 = time.time()
main()
time2 = time.time()
sys.stdout.write("\nTime elapsed: " + str(time2 - time1) + " s.\n")
