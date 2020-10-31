import RolandPianoUsb as rpu
import mido
import time
import yaml
import logging
import argparse
import os
from Utils import *
import Display

running_as_rpi = os.uname().nodename == "raspberrypi"

from demo_opts import get_device
from luma.core.render import canvas
from PIL import ImageFont


if running_as_rpi:
    import RotaryEncoder as re
    from RPi import GPIO

    def switch(num):
        log.info(f"SW on num:{num}") 

    def rot(piano,num,incr):
        log.info(f"R on num:{num}, incr: {incr}")
        address_name = rotary_encoder_mapping[num]
        piano.add_pending_write_action(address_name,incr)



def main():
    # ambiPiano = None

    parser = argparse.ArgumentParser(description='Connect to Roland fp-10 piano')
    parser.add_argument('-apg','--ambi_piano_gui', action='store_true', help="Use ambi piano GUI")
    

    # pd = Display.PianoData()
    

    args = parser.parse_args()
    try:
        name = mido.get_input_names()[1]
        piano = rpu.RolandPianoUsb(name)

        if running_as_rpi:
            encoder_pins = [(17,22,27,0),(14,18,15,1),(10,9,11,2),(8,7,1,4),(23,24,25,3)]
            GPIO.setmode(GPIO.BCM)
            encoders = list(map((lambda p : re.RotaryEncoder(p[0],p[1],p[2],p[3],switch,rot,piano)) ,encoder_pins))



        field_timer = 0
        fields = ['toneForSingle','masterVolume','sequencerTempoRO']
        piano.set_fields(fields)
        while True:
            time.sleep(.016)

            # pd.randomize()
            # Display.draw_screen0(device,piano.fields)

            piano.port_in_handler()
            piano.print_fields(fields, onlyUpdates=True)
            # print(piano.fields)

            piano.perform_pending_write_actions()

            if field_timer == 20:
                logging.info("Updating fields")
                field_timer = 0
                piano.update_fields()
                # piano.play_note("C-4",60)
            else:
                field_timer += 1

    except KeyboardInterrupt:
        logging.info("Exit cmd given by user, disconnecting..")
        GPIO.cleanup()
        if piano:
            piano.disconnect()


if __name__ == "__main__":
    import logging.config
    with open('logging.yaml') as f:
        config = yaml.safe_load(f)
        logging.config.dictConfig(config)
    log = logging.getLogger(__name__)

    if running_as_rpi:
        device = Display.get_device()

    main()