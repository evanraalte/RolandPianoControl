#!/usr/bin/python3
import argparse
import RolandPiano as rp
from bluepy import btle
import logging
import yaml




def main():
    piano = None
    ambiPiano = None

    parser = argparse.ArgumentParser(description='Connect to Roland fp-10 piano')
    parser.add_argument('-m','--mac_addr', type=str, help="Mac address of the piano")
    parser.add_argument('-apg','--ambi_piano_gui', action='store_true', help="Use ambi piano GUI")


    args = parser.parse_args()
    try:
        if args.ambi_piano_gui:
            import AmbiPiano
            ambiPiano = AmbiPiano.Canvas(randomize=False)

        piano = rp.RolandPiano(args.mac_addr)
        field_timer = 0
        fields = ['masterVolume','sequencerTempoWO']
        while True:
            # Update state of the key_status
            for k,v in piano.delegate.message.sustained_key_status.items():
                if v > 0 : piano.delegate.message.sustained_key_status[k] -= 1

            # Update velocity on canvas
            if args.ambi_piano_gui:
                ambiPiano.velocities = piano.delegate.message.sustained_key_status 

            piano.idle()

            piano.print_fields(fields, onlyUpdates=True)

            if field_timer == 60:
                field_timer = 0
                piano.update_fields(fields)
            else:
                field_timer += 1

                
    except KeyboardInterrupt:
        log.info("Exit cmd given by user, disconnecting..")
        if ambiPiano:
            ambiPiano.kill()
        if piano:
            piano.disconnect()


if __name__ == "__main__":
    import logging.config
    with open('logging.yaml') as f:
        config = yaml.safe_load(f)
        logging.config.dictConfig(config)
    log = logging.getLogger(__name__)
    main()


     

    


    

