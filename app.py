#!/usr/bin/python3
import argparse
import RolandPiano as rp
from bluepy import btle
import logging
import yaml
import AmbiPiano

def main():
    log.info("Exit cmd given by user, disconnecting..")
    piano = None
    parser = argparse.ArgumentParser(description='Connect to Roland fp-10 piano')
    parser.add_argument('mac_addr',metavar = 'mac_addr', type=str, help="mac address of the piano")

    canvas = AmbiPiano.Canvas(randomize=False)
    
    args = parser.parse_args()
    try:
        piano = rp.RolandPiano(args.mac_addr)
        
        while True:
            for k,v in piano.delegate.message.key_status.items():
                if v > 0 : piano.delegate.message.key_status[k] -= 1
            canvas.velocities = piano.delegate.message.key_status #list(map(lambda x: x*(300/127),piano.delegate.key_status))

            piano.idle()
                
    except KeyboardInterrupt:
        log.info("Exit cmd given by user, disconnecting..")
        if piano:
            piano.disconnect()


if __name__ == "__main__":
    import logging.config
    with open('logging.yaml') as f:
        config = yaml.safe_load(f)
        logging.config.dictConfig(config)
    log = logging.getLogger(__name__)
    main()


     

    


    

