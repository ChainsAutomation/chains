# encoding: utf-8

from papirus import PapirusTextPos, Papirus
from PIL import ImageFont, ImageDraw, Image
import os, sys

WHITE = 1
BLACK = 0
FONT = '/usr/share/fonts/truetype/freefont/FreeMono.ttf'

def checkEpdSizeSet():
    # Check EPD_SIZE is defined
    EPD_SIZE=0.0
    if os.path.exists('/etc/default/epd-fuse'):
        exec(open('/etc/default/epd-fuse').read())
    if EPD_SIZE == 0.0:
        print("Please select your screen size by running 'papirus-config'.")
        sys.exit()

def getFontSize(my_papirus, printstring, fontsize=0):
    #returns (ideal fontsize, (length of text, height of text)) that maximally
    #fills a papirus object for a given string

    if not fontsize:

        stringlength = 0
        stringwidth = 0

        maxLength = my_papirus.width
        maxHeight = my_papirus.height

        while (stringlength <= maxLength and stringwidth <= maxHeight):

            fontsize += 1
            font = ImageFont.truetype(FONT, fontsize)
            size = font.getsize(printstring)
            stringlength = size[0]
            stringwidth = size[1]

        fontsize = fontsize - 1

    font = ImageFont.truetype(FONT, fontsize)
    return fontsize, font.getsize(printstring)

def drawWords(my_papirus, printstring, fontsize, dims):

    #initially set all white background
    image = Image.new('1', my_papirus.size, WHITE)

    # prepare for drawing
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(FONT, fontsize)

    draw.text(((my_papirus.width-dims[0])/2, (my_papirus.height/2) - (dims[1]/2)), printstring, font=font, fill=BLACK)

    my_papirus.display(image)
    my_papirus.update()


def writeFullWidth(text, rot=0):

    printString = text

    if len(printString) > 40:
        # print('WARNING: string length is too large for single line printing, truncating at 40 chars')
        printString = printString[0:40]

    my_papirus = Papirus(rotation = int(rot))
    fontsize, dims= getFontSize(my_papirus, printString)
    drawWords(my_papirus, printString, fontsize, dims)

def writeCenter(text, size=20, padding=None):

    size = int(size)

    if padding:
        padding_y = padding
    else:
        padding_y = int(round(size/10)+1)

    display = PapirusTextPos(False, rotation=0)

    p = Papirus()
    display_width = p.width
    display_height = p.height

    font = ImageFont.truetype(FONT, size)
    dims = font.getsize('text')
    font_height = dims[1]

    lines = text.split('\n')
    lines_height = len(lines) * (font_height+padding_y)

    y = (display_height - lines_height) / 2
    for line in lines:
        dims = font.getsize(line)
        x = (display_width - dims[0]) / 2
        display.AddText(line, x, y, size)
        print "%s x %s = %s" % (x,y,line)
        y += font_height + padding_y
            
    #display.Clear()
    display.WriteAll()


