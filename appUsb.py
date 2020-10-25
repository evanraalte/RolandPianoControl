import RolandPianoUsb as rpu
import mido
import time
import yaml
import logging
import argparse
import os

running_as_rpi = os.uname().nodename == "raspberrypi"

rotary_encoder_mapping = [
    ("masterVolume",0,100),
    ("sequencerTempoWO",0,200)
]

def int_to_byte(num):
    return num.to_bytes(1,byteorder='big')

def byte_to_int(byte):
    return int.from_bytes(byte,byteorder='big')

def get_reverse_parser(address_name):
    parsers = {
        "sequencerTempoWO": lambda x: int_to_byte((x & 0xff80) >> 7) + int_to_byte(x & 0x7f),
        "keyTransposeRO"  : lambda x  : int_to_byte(x+64),
        # "toneForSingle" : lambda x : (x[0],x[2])
    }

    if address_name in parsers:
        return parsers[address_name]
    else:
        return int_to_byte

def get_parser(addressName):
    parsers = {
        "sequencerTempoRO": lambda data: (data[1] & b"\x7F"[0]) | ((data[0] & b"\x7F"[0]) << 7),
        "keyTransposeRO"  : lambda x  : x[0]-64,
        "toneForSingle" : lambda x : (x[0],x[2])
    }

    if addressName in parsers:
        return parsers[addressName]
    else:
        return byte_to_int

def get_address_size(addressName):
    addressSizeMap = {  # consider implementing this to read all registers
        "serverSetupFileName" : 32,
        "sequencerMeasure" : 2,
        "sequencerTempoRO" : 2,
        "toneForSingle"    : 2,
        "toneForSplit"     : 3,
        "toneForDual"      : 3,
        "songNumber"       : 3,
        "masterTuning"     : 2,
        "arrangerPedalFunction" : 2,
        "sequencerTempoWO" : 2,
        "uptime" : 8
    }

    if addressName in addressSizeMap:
        return addressSizeMap[addressName]
    else:
        return 1



if running_as_rpi:
    import RotaryEncoder as re
    from RPi import GPIO

    def switch(num):
        print(f"SW on num:{num}")

    def rot(piano,num,countUp):
        log.info(f"R on num:{num}, count: {countUp}")

        address_name = rotary_encoder_mapping[num][0]
        minimum      = rotary_encoder_mapping[num][1] 
        maximum      = rotary_encoder_mapping[num][2]

        if address_name == "sequencerTempoWO":
            address_name_read = "sequencerTempoRO"
        else:
            address_name_read = address_name


        if address_name_read not in piano.fields:
            piano.fields[address_name_read] = (get_address_size(address_name_read)*b"\x00",False)

        parser = get_parser(address_name_read)

        var = parser(piano.fields[address_name_read][0])

        var_new = (var + 1) if countUp else (var - 1)
        if maximum > var_new > minimum:
            var = var_new

        reverse_parser = get_reverse_parser(address_name)

        log.info(f"var: {var}")
        if var != piano.fields[address_name_read]: # if changed
            piano.fields[address_name_read] = (reverse_parser(var),True)
            piano.add_pending_write_action(address_name,reverse_parser(var))



def main():
    # ambiPiano = None

    parser = argparse.ArgumentParser(description='Connect to Roland fp-10 piano')
    parser.add_argument('-apg','--ambi_piano_gui', action='store_true', help="Use ambi piano GUI")
    
    

    args = parser.parse_args()
    try:
        name = mido.get_input_names()[1]
        piano = rpu.RolandPianoUsb(name)

        if running_as_rpi:
            encoder_pins = [(17,22,27,0),(14,15,18,1),(10,9,11,2),(8,7,1,4),(23,24,25,3)]
            GPIO.setmode(GPIO.BCM)
            encoders = list(map((lambda p : re.RotaryEncoder(p[0],p[1],p[2],p[3],switch,rot,piano)) ,encoder_pins))



        field_timer = 0
        fields = ['toneForSingle','masterVolume','sequencerTempoRO']
        piano.set_fields(fields)
        while True:
            time.sleep(.2)
            piano.port_in_handler()
            piano.print_fields(fields, onlyUpdates=True)
            # print(piano.fields)

            piano.perform_pending_write_actions()

            if field_timer == 5:
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
    main()