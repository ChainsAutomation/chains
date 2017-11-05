from chains.service import Service
from chains.common import log, config
from papirus import PapirusComposite, Papirus
from papirus.composite import WHITE, BLACK
from PIL import ImageFont, Image
import os

# https://github.com/PiSupply/PaPiRus

class PapirusService(Service):

    def onInit(self):
        if not self._checkEpdSizeSet():
            log.error("Please select your screen size by running: papirus-config")
        self.rotation = self._getRotation()
        self.display = PapirusComposite(autoupdate=False, rotation=self.rotation)

    def action_add_text(self, text, size=None, x=None, y=None, invert=False, font=None, update=False):
        """
        Add text to display (but do not update before update is called)
        @param  text    string   The text to display
        @param  size    int      Font size
        @param  x       int      X coordinate (or None for horizontal center)
        @param  y       int      Y coordinate (or None for vertical center)
        @param  invert  boolean  Show white on black instead of default black on white
        @param  font    string   Path to font, absolute or relative to /usr/share/fonts/truetype
        """
        font = self._getFont(font)
        size = self._getFontSize(size)
        x = self._getCoordinateX(x, font, size, text)
        y = self._getCoordinateY(y, font, size, text)
        self.display.AddText(text, x=x, y=y, size=size, invert=invert, fontPath=font)
        if update:
            self.action_update()

    def action_set_text(self, text, size=None, x=None, y=None, invert=False, font=None):
        """
        Add text to display (and update immediately, overwriting any previous texts)
        @param  text    string   The text to display
        @param  size    int      Font size
        @param  x       int      X coordinate (or None for horizontal center)
        @param  y       int      Y coordinate (or None for vertical center)
        @param  invert  boolean  Show white on black instead of default black on white
        @param  font    string   Path to font, absolute or relative to /usr/share/fonts/truetype
        """
        self.action_add_text(text, size, x, y, invert, font, True)

    def action_update(self):
        """
        Render texts on display after multiple calls to add_text
        """
        self.display.WriteAll()
        # Start fresh with a new display after update
        # (else all previous add_text() calls are still there)
        self.display = PapirusComposite(autoupdate=False, rotation=self.rotation)

    # ====================================================================
    # Helpers
    # ====================================================================

    # Get rotation setting from config
    def _getRotation(self):
        rotation = self.config.getInt('rotation')
        if not rotation:
            self.rotation = 0
        if rotation not in [0,90,180,270]:
            log.warn("Invalid config main.rotation: %s, valid is: 0 or 90 or 180 or 270, will use 0")
            rotation = 0

    # Take relative font path and make absolute (unless already absolute)
    # or return default font from config (or FreeMono) if none passed.
    def _getFont(self, font):
        if not font:
            defaultFont = self.config.get('font')
            if defaultFont: font = defaultFont
            else: font = 'freefont/FreeMono.ttf'
        if font[0] != '/':
            font = '/usr/share/fonts/truetype/%s' % font
        return font

    # Take font size argument and ensure it is int
    # or return default font size if none passed.
    def _getFontSize(self, size):
        try: size = int(size)
        except: size = 0
        if not size:
            defaultSize = self.config.getInt('fontsize')
            if defaultSize: size = defaultSize
            else: size = 20
        return size

    # Take x argument and ensure it is int
    # or return coordinate that centers text horizontally if none passed.
    def _getCoordinateX(self, x, font, size, text):
        if x != None:
            try: x = int(x)
            except: x = 0
            return x
        f = ImageFont.truetype(font, size)
        font_width = font.getsize(text)[1]
        p = Papirus()
        disp_width = p.width
        return (disp_width-font_width) / 2

    # Take y argument and ensure it is int
    # or return coordinate that centers text vertically if none passed.
    def _getCoordinateY(self, y, font, size, text):
        if y != None:
            try: y = int(y)
            except: y = 0
            return y
        f = ImageFont.truetype(font, size)
        font_height = font.getsize(text)[0]
        p = Papirus()
        disp_height = p.height
        return (disp_height-font_height) / 2


    def _checkEpdSizeSet():
        # Check EPD_SIZE is defined
        EPD_SIZE=0.0
        if os.path.exists('/etc/default/epd-fuse'):
            exec(open('/etc/default/epd-fuse').read())
        if EPD_SIZE == 0.0:
            return False
        return True
