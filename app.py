#!/usr/bin/python3
import argparse
import RolandPiano as rp
from bluepy import btle
import logging
import yaml

def main():
    log.info("Exit cmd given by user, disconnecting..")
    piano = None
    parser = argparse.ArgumentParser(description='Connect to Roland fp-10 piano')
    parser.add_argument('mac_addr',metavar = 'mac_addr', type=str, help="mac address of the piano")

    
    args = parser.parse_args()
    try:
        piano = rp.RolandPiano(args.mac_addr)
        
        while True:
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


     

    


    

