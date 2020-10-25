

import os
import sys
import time
import random


from demo_opts import get_device
from luma.core.render import canvas
from PIL import ImageFont

# use custom font
font_path = os.path.join(os.getcwd(),'SourceCodePro-Light.ttf')
font     = {} 
font[15] = ImageFont.truetype(font_path, 15)
font[10] = ImageFont.truetype(font_path, 10)


class PianoData:
    _ranges = {
        "volume" : (0,100),
        "bpm"    : (0,255),
    }


    def __init__(self):
        self._data = {}
    def randomize(self):
        for k,minmax in self._ranges.items():
            self._data[k] = random.randint(minmax[0],minmax[1])

    def __getitem__(self,name):
        if name in self._data:
            return self._data[name]
        else:
            return 0
    def __setitem__(self,name,d):
        # check validity of data etc
        self._data[name] = d




def draw_screen0(device, piano_data):

    volume = piano_data['volume'] #random.randint(0,100)
    bpm    = piano_data['bpm'] #random.randint(0,255)
    
    with canvas(device) as draw:

        # Volume bar
        bar_low_width  = 10
        bar_high_width = 25

        h = 62 - (volume * (61/100) ) 
        w = bar_low_width + (volume/100)*(bar_high_width - bar_low_width)

        draw.polygon([(1,1),(bar_high_width,1),(bar_low_width,62),(1,62)],outline="white")
        draw.polygon([(1,h),(w,h),(bar_low_width,62),(1,62)],fill="white")

        draw.text((24,62-15-10),f"vol",font=font[10],fill="white")
        draw.text((15,62-15),f"{volume:>2}%",font=font[15],fill="white")

        # BPM bar
        bar_low_width  = 10
        bar_high_width = 25

        h = 62 - (bpm * (61/255) ) 
        w = bar_low_width + (bpm/255)*(bar_high_width - bar_low_width)

        draw.polygon([(126,1),(127-bar_high_width,1),(127-bar_low_width,62),(126,62)],outline="white")
        draw.polygon([(126,h),(127-w,h),(127-bar_low_width,62),(126,62)],fill="white")
        draw.text((85,62-15-10),f"bpm",font=font[10],fill="white")
        draw.text((85,62-15),f"{bpm:2}",font=font[15],fill="white")





def main():
    pd = PianoData()

    while True:
        pd.randomize()
        draw_screen0(device,pd)
        time.sleep(0.5)


if __name__ == "__main__":
    try:
        device = get_device()
        main()
    except KeyboardInterrupt:
        pass
