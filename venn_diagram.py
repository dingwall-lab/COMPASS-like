from PIL import Image, ImageDraw, ImageFont
import sys
import os
import argparse
import math
import time

parser = argparse.ArgumentParser(description= "Venn Diagram allows the user to enter population sizes to build a Venn diagram."
+ " The user must enter the total population of each of the two sets, as well as the population size that is included in both.")
parser.add_argument('-o', '--outputDirectory', help = 'The folder in which the output will be stored.', required = True)
parser.add_argument('-f', '--outputFileName', help = 'The name of the output png file (no suffix).', nargs = '?', default = 'venn')
parser.add_argument('-a', '--areaA', help = 'total population in circle A', type = int, required = True)
parser.add_argument('-b', '--areaB', help = 'total population in circle B', type = int, required = True)
parser.add_argument('-v', '--overlap', help = 'overlapping population in both circles A and B', type = int, required = True)
parser.add_argument('-m', '--nameA', help = 'name of population in circle A', nargs = '?', default = 'circle A')
parser.add_argument('-n', '--nameB', help = 'name of population in circle B', nargs = '?', default = 'circle B')
parser.add_argument('-c', '--colorA', help = 'color of circle A as defined by a comma-delimited list of rgb values e.g. 123,34,255', nargs = '?', type = str, default = '0,150,255')
parser.add_argument('-d', '--colorB', help = 'color of circle B as defined by a comma-delimited list of rgb values e.g. 123,34,255', nargs = '?', type = str, default = '255,0,0')
parser.add_argument('-r', '--resolution', help = 'The height and width of the output in pixels.', nargs = '?', type = int, default = 500)
parser.add_argument('-t', '--font', help = 'a TrueType font file', nargs = '?', default = 'C:\\Windows\\Fonts\\constanb.ttf')
parser.add_argument('-y', '--fontSizeNums', help = 'The font size coefficient for the numbers in the diagram; 1 is the original (default) size. Also adjusts line thickness.', nargs = '?', type = float, default = 1)
parser.add_argument('-z', '--fontSizeInfo', help = 'The font size coefficient for the information below the diagram; 1 is the original (default) size. Also adjusts line thickness.', nargs = '?', type = float, default = 1)


args = vars(parser.parse_args())

def thickCircle(x1,y1,x2,y2,thickness,r,g,b,draw):
    draw.ellipse((x1, y1, x2, y2), fill = (r, g, b, 100))
    for i in range(thickness):
        for j in range(10):
            draw.ellipse((float(x1)-(float(i)+j/10.0), float(y1)-(float(i)+j/10.0), float(x2)+(float(i)+j/10.0), float(y2)+(float(i)+j/10.0)), fill = (0, 0, 0, 0), outline = (r, g, b, 255))

def main():
    rgb1 = args['colorA'].strip().split(',')
    rgb1 = map(int,rgb1)
    rgb2 = args['colorB'].strip().split(',')
    rgb2 = map(int,rgb2)
    os.chdir(args["outputDirectory"])
    res = args["resolution"]
    rA = math.sqrt(args["areaA"] / math.pi)
    rB = math.sqrt(args["areaB"] / math.pi)
    distance = max([rA,rB])
    bottom = abs(rA - rB)
    top = rA + rB
    area = 0
    while abs(args['overlap'] - area) > 0.001:
        area = ((rA**2.0) * math.acos((distance**2.0 + rA**2.0 - rB**2.0) / (2.0*distance*rA))) + ((rB**2.0) * math.acos((distance**2.0 + rB**2.0 - rA**2.0) / (2.0*distance*rB))) - (0.5 * math.sqrt((-distance+rA+rB)*(distance+rA-rB)*(distance-rA+rB)*(distance+rA+rB)))
        if area < args['overlap']:
            top = distance
            distance = (distance + bottom) / 2.0
        elif area > args['overlap']:
            bottom = distance
            distance = (distance + top) / 2.0

    f = 1.8 / (rA + distance + rB)

    image = Image.new('RGB', (res*2, res*4), (255,255,255))
    draw = ImageDraw.Draw(image, 'RGBA')

    thickCircle(res*0.1,res*(1-(rA*f)),res*(0.1+(rA*f*2)),res*(1+(rA*f)),int(math.floor((res*args["fontSizeInfo"])/50.0)),rgb1[0],rgb1[1],rgb1[2],draw)
    thickCircle(res*(1.9-(rB*f*2)),res*(1-(rB*f)),res*1.9,res*(1+(rB*f)),int(math.floor((res*args["fontSizeInfo"])/50.0)),rgb2[0],rgb2[1],rgb2[2],draw)

    fntNums = ImageFont.truetype(args["font"], int(math.floor((res/10)*args["fontSizeNums"])))
    fntInfo = ImageFont.truetype(args["font"], int(math.floor((res/10)*args["fontSizeInfo"])))

    circleAName = args['nameA']
    circleANameW, circleANameH = draw.textsize(circleAName, fntInfo)
    circleBName = args['nameB']
    circleBNameW, circleBNameH = draw.textsize(circleBName, fntInfo)

    circleACount = str(args["areaA"] - args["overlap"])
    circleACountW, circleACountH = draw.textsize(circleACount, fntNums)
    circleBCount = str(args["areaB"] - args["overlap"])
    circleBCountW, circleBCountH = draw.textsize(circleBCount, fntNums)
    overlapCount = str(args["overlap"])
    overlapCountW, overlapCountH = draw.textsize(overlapCount, fntNums)

    thickCircle(res*0.1,max([res*(1+(rB*f)), res*(1+(rA*f))]) + circleANameH*1.5,res*(0.1)+circleANameH*2,max([res*(1+(rB*f)), res*(1+(rA*f))]) + circleANameH*3.5,int(math.floor((res*args["fontSizeInfo"])/50.0)),rgb1[0],rgb1[1],rgb1[2],draw)
    thickCircle(res*0.1,max([res*(1+(rB*f)), res*(1+(rA*f))]) + circleANameH*4.5,res*(0.1)+circleANameH*2,max([res*(1+(rB*f)), res*(1+(rA*f))]) + circleANameH*6.5,int(math.floor((res*args["fontSizeInfo"])/50.0)),rgb2[0],rgb2[1],rgb2[2],draw)
    draw.text((res*0.1 + circleANameH*3,max([res*(1+(rB*f)), res*(1+(rA*f))]) + circleANameH*2), circleAName, fill=(0, 0, 0, 255), font = fntInfo)
    draw.text((res*0.1 + circleANameH*3,max([res*(1+(rB*f)), res*(1+(rA*f))]) + circleANameH*5), circleBName, fill=(0, 0, 0, 255), font = fntInfo)

    draw.text(((res*0.1 + res*(1.9-(rB*f*2)))/2.0 - (circleACountW/2.0), (res*(1-(rA*f)) + res*(1+(rA*f)))/2.0 - (circleACountH/2.0)), circleACount, fill = (0, 0, 0, 255), font = fntNums)
    draw.text(((res*(0.1+(rA*f*2)) + res*1.9)/2.0 - (circleBCountW/2.0), (res*(1-(rB*f)) + res*(1+(rB*f)))/2.0 - (circleBCountH/2.0)), circleBCount, fill = (0, 0, 0, 255), font = fntNums)
    draw.text(((res*(1.9-(rB*f*2)) + res*(0.1+(rA*f*2)))/2.0 - (overlapCountW/2.0), (res*(1-(rA*f)) + res*(1+(rA*f)))/2.0 - (overlapCountH/2.0)), overlapCount, fill = (0, 0, 0, 255), font = fntNums)

    image = image.resize((res,res*2), Image.ANTIALIAS)
    image = image.crop((0,min([0.5*res*(1-(rB*f)), 0.5*res*(1-(rA*f))]) - int(math.floor(circleANameH / args["fontSizeInfo"])),res,max([0.5*res*(1+(rB*f)), 0.5*res*(1+(rA*f))])+circleANameH*4))
    image.save((args["outputFileName"]+'.png'), "PNG")

time1 = time.time()
main()
time2 = time.time()
sys.stdout.write("\nTime elapsed: " + str(time2 - time1) + " s.\n")
