from bluepy import btle
import time
import pandas as pd
import logging
log = logging.getLogger(__name__)



# TODO: yaml files?
lut = {
    "note_on"         : b'\x90',
    "note_off"        : b'\x80',
    "control_change"  : b'\xb0',
    "sysex_msg_start" : b'\xf0',
    "sysex_msg_end"   : b'\xf7',
    "cmd_read"        : b'\x11',
    "cmd_write"       : b'\x12', 
    "id_roland"       : b'\x41\x10\x00\x00\x00\x28'
}



def int_to_byte(num):
    return num.to_bytes(1,byteorder='big')

def byte_to_int(byte):
    return int.from_bytes(byte,byteorder='big')

def parse_sequencer_tempo(data):
    # TODO: 2 byte to integer
    return (data[1] & b"\x7F"[0]) | ((data[0] & b"\x7F"[0]) << 7)


def note_string_to_midi(midstr):
    notes = [["C"],["C#","Db"],["D"],["D#","Eb"],["E"],["F"],["F#","Gb"],["G"],["G#","Ab"],["A"],["A#","Bb"],["B"]]
    answer = 0
    i = 0
    #Note
    letter = midstr.split('-')[0].upper()
    for note in notes:
        for form in note:
            if letter.upper() == form:
                answer = i
                break
        i += 1
    #Octave
    answer += (int(midstr[-1]))*12
    return int_to_byte(answer)



fields = {}




def get_parser(addressName):
    parsers = {
        "sequencerTempoRO": parse_sequencer_tempo,
        "masterVolume"    : byte_to_int
    }

    if addressName in parsers:
        return parsers[addressName]
    else:
        return (lambda x : x) 

addresses = {
    # 010000xx
    "serverSetupFileName":            b"\x01\x00\x00\x00",
    # 010001xx
    "songToneLanguage":               b"\x01\x00\x01\x00",
    "keyTransposeRO":                 b"\x01\x00\x01\x01",
    "songTransposeRO":                b"\x01\x00\x01\x02",
    "sequencerStatus":                b"\x01\x00\x01\x03",
    "sequencerMeasure":               b"\x01\x00\x01\x05",
    "sequencerTempoNotation":         b"\x01\x00\x01\x07",
    "sequencerTempoRO":               b"\x01\x00\x01\x08",
    "sequencerBeatNumerator":         b"\x01\x00\x01\x0A",
    "sequencerBeatDenominator":       b"\x01\x00\x01\x0B",
    "sequencerPartSwAccomp":          b"\x01\x00\x01\x0C",
    "sequencerPartSwLeft":            b"\x01\x00\x01\x0D",
    "sequencerPartSwRight":           b"\x01\x00\x01\x0E",
    "metronomeStatus":                b"\x01\x00\x01\x0F",
    "headphonesConnection":           b"\x01\x00\x01\x10",
    # 010002xx
    "keyBoardMode":                   b"\x01\x00\x02\x00",
    "splitPoint":                     b"\x01\x00\x02\x01",
    "splitOctaveShift":               b"\x01\x00\x02\x02",
    "splitBalance":                   b"\x01\x00\x02\x03",
    "dualOctaveShift":                b"\x01\x00\x02\x04",
    "dualBalance":                    b"\x01\x00\x02\x05",
    "twinPianoMode":                  b"\x01\x00\x02\x06",
    "toneForSingle":                  b"\x01\x00\x02\x07",
    "toneForSplit":                   b"\x01\x00\x02\x0A",
    "toneForDual":                    b"\x01\x00\x02\x0D",
    "songNumber":                     b"\x01\x00\x02\x10",
    "masterVolume":                   b"\x01\x00\x02\x13",
    "masterVolumeLimit":              b"\x01\x00\x02\x14",
    "allSongPlayMode":                b"\x01\x00\x02\x15",
    "splitRightOctaveShift":          b"\x01\x00\x02\x16",
    "dualTone1OctaveShift":           b"\x01\x00\x02\x17",
    "masterTuning":                   b"\x01\x00\x02\x18",
    "ambience":                       b"\x01\x00\x02\x1A",
    "headphones3DAmbience":           b"\x01\x00\x02\x1B",
    "brilliance":                     b"\x01\x00\x02\x1C",
    "keyTouch":                       b"\x01\x00\x02\x1D",
    "transposeMode":                  b"\x01\x00\x02\x1E",
    "metronomeBeat":                  b"\x01\x00\x02\x1F",
    "metronomePattern":               b"\x01\x00\x02\x20",
    "metronomeVolume":                b"\x01\x00\x02\x21",
    "metronomeTone":                  b"\x01\x00\x02\x22",
    "metronomeDownBeat":              b"\x01\x00\x02\x23",
    # 010003xx
    "applicationMode":                b"\x01\x00\x03\x00",
    "scorePageTurn":                  b"\x01\x00\x03\x02",
    "arrangerPedalFunction":          b"\x01\x00\x03\x03",
    "arrangerBalance":                b"\x01\x00\x03\x05",
    "connection":                     b"\x01\x00\x03\x06",
    "keyTransposeWO":                 b"\x01\x00\x03\x07",
    "songTransposeWO":                b"\x01\x00\x03\x08",
    "sequencerTempoWO":               b"\x01\x00\x03\x09",
    "tempoReset":                     b"\x01\x00\x03\x0B",
    # 010004xx
    "soundEffect":                    b"\x01\x00\x04\x00",
    "soundEffectStopAll":             b"\x01\x00\x04\x02",
    # 010005xx
    "sequencerREW":                   b"\x01\x00\x05\x00",
    "sequencerFF":                    b"\x01\x00\x05\x01",
    "sequencerReset":                 b"\x01\x00\x05\x02",
    "sequencerTempoDown":             b"\x01\x00\x05\x03",
    "sequencerTempoUp":               b"\x01\x00\x05\x04",
    "sequencerPlayStopToggle":        b"\x01\x00\x05\x05",
    "sequencerAccompPartSwToggle":    b"\x01\x00\x05\x06",
    "sequencerLeftPartSwToggle":      b"\x01\x00\x05\x07",
    "sequencerRightPartSwToggle":     b"\x01\x00\x05\x08",
    "metronomeSwToggle":              b"\x01\x00\x05\x09",
    "sequencerPreviousSong":          b"\x01\x00\x05\x0A",
    "sequencerNextSong":              b"\x01\x00\x05\x0B",
    # 010006xx
    "pageTurnPreviousPage":           b"\x01\x00\x06\x00",
    "pageTurnNextPage":               b"\x01\x00\x06\x01",
    # 010007xx
    "uptime":                         b"\x01\x00\x07\x00",
    # 010008xx
    "addressMapVersion":              b"\x01\x00\x08\x00"}

def get_address_name(address):
    return list(addresses.keys())[list(addresses.values()).index(address)]

def get_address_size(addressName):
    addressSizeMap = {  # consider implementing this to read all registers
        "sequencerMeasure" : 2,
        "sequencerTempoRO" : 2,
        "masterTuning"     : 2
    }

    if addressName in addressSizeMap:
        return addressSizeMap[addressName]
    else:
        return 1


class Message():
    key_status           = {}
    sustained_key_status = {}
    sustain              = 0
    header_byte          = b""

    buf = b""
    def __str__(self):
        buffer = ""
        buffer += f"buf: {self.buf.hex()}\n"
        buffer += f"header_byte: {self.header_byte}, timestamp_byte: {self.timestamp_byte}\n"
        buffer += f"status_byte: {self.status_byte}\n"

        for idx,_ in enumerate(self.notes):
            buffer += f"note: {self.notes[idx]}, velocity: {self.velocities[idx]}\n"

        return buffer
        

    def __init__(self):
        for i in range(0,88+1):
            self.sustained_key_status[i] = 0
            self.key_status[i] = 0

    def reset(self):
        self.buf = b""
        self.header_byte    = None
        self.timestamp_byte = None
        self.status_byte    = None

        self.status_bytes   = None
        self.notes          = None
        self.velocities     = None

        self.man_id         = None
        self.cmd            = None
        self.address        = None
        self.data           = None
        self.checksum       = None
        return

    def getAudioStatusCodes(self):
        return [lut['note_on'], lut['note_off'], lut['control_change']]

    def isAudioMsg(self):
        return self.status_byte in self.getAudioStatusCodes()

    def isValidAudioMsg(self):
        return self.status_byte and self.notes and self.velocities
    
    def isSysExMsg(self):
        return self.status_byte == lut['sysex_msg_start']

    def timeStampChanged(self,data):
        return self.timestamp_byte != data[2:3]

    def sysExMsgEnded(self):
        return (lut['sysex_msg_end'] in self.buf)

    def validSysExMsgLength(self):
        # cmd (2) + address (8) + data (>=1) + checksum (1)
        return len(self.buf) >= (2+8+1+1)

    def isNewMsg(self, data):
        headerChanged = data[0:1] != self.header_byte
        isMidiMsg = len(data) == 5 and (data[2:3] in self.getAudioStatusCodes())
        return headerChanged or isMidiMsg

    def append(self,data):
        if self.isNewMsg(data):
            # new message, discard old message
            self.reset()
            try:
                self.header_byte    = data[0:1]
                self.timestamp_byte = data[1:2]
                self.status_byte    = data[2:3]
                self.buf            = data[3:]
            except Exception:
                return -1 # done, with errors
            if self.isAudioMsg():

                # len is 5 + (n*4)
                # n is not larger than 2, so basically a message can hold 3 midi audio updates. 
                #TODO: write more elegantly

                if len(self.buf) == 2: # Contains one midi msg
                    try:
                        self.status_bytes = [self.status_byte]
                        self.notes     = [self.buf[0:1]]
                        self.velocities = [self.buf[1:2]]
                    except Exception:
                        return -1  # done, with errors
                elif len(self.buf) == 6: # Contains two midi msgs ('compressed')
                    try:
                        self.status_bytes = [self.status_byte, self.buf[3:4]]
                        self.notes     = [self.buf[0:1],self.buf[4:4+1]]
                        self.velocities = [self.buf[1:2],self.buf[5:5+1]]
                    except Exception:
                        return -1  # done, with errors
                return 1 # done
        else: 
            self.buf += data[1:] # append message
    
        if self.isSysExMsg() and self.sysExMsgEnded() and self.validSysExMsgLength():
            self.buf      = self.buf.split(lut['sysex_msg_end'])[0] # cut the message at the end
            self.man_id   = self.buf[0:6]
            self.cmd      = self.buf[6:6+1]
            self.address  = self.buf[7:7+4]
            l             = len(self.buf)
            self.checksum = self.buf[l-2:l-1] 
            self.data     = self.buf[11:l-2]
            return 1 # done succesfully
        else:
            return 0 # not done

    def get_checksum(self,addr,data):
        total = 0
        for b in addr:
            total += b
        for b in data:
            total += b        
        return int_to_byte(128 - (total % 128))  

    def isValidRolandMsg(self):
        cmp_checksum = self.get_checksum(self.address, self.data)
        correct_size = get_address_size(get_address_name(self.address)) == len(self.data)
        return self.man_id == lut['id_roland'] and self.cmd and self.address and self.checksum == cmp_checksum and correct_size


    def decode(self):
        if self.isAudioMsg():
            if self.isValidAudioMsg():
                for idx,_ in enumerate(self.notes):
                    key = byte_to_int(self.notes[idx]) - 21
                    vel = byte_to_int(self.velocities[idx])

                    if self.status_bytes[idx]   == lut['note_on']:
                        self.key_status[key] = vel
                    elif self.status_bytes[idx] == lut['note_off']: #TODO: fix bug when sustain is released and note is not turned of
                        self.key_status[key] = 0
                    elif self.status_bytes[idx] == lut['control_change']:
                        self.sustain = vel

                    log.debug(f"key: {key}, vel: {vel}")
                    log.debug(f"{self.status_bytes[idx].hex()} - note: {self.notes[idx].hex()}, velocity: {self.velocities[idx].hex()}")

                log.debug(list(self.key_status.values())[-10:])
                log.debug(f"sustain: {self.sustain}")    

                # # Handle sustain pedal
                if self.sustain == 0:
                    self.sustained_key_status = self.key_status.copy()
                else:
                    for k,_ in self.key_status.items(): 
                        if self.key_status[k] >= self.sustained_key_status[k]: 
                            self.sustained_key_status[k] = self.key_status[k]

                log.debug(list(self.sustained_key_status.values())[-10:])
                return 0

        elif self.isSysExMsg():
            if self.isValidRolandMsg():
                log.debug(f"address: {self.address.hex()}, data: {self.data.hex()}, cmd: {self.cmd.hex()}")
                fields[get_address_name(self.address)] = (self.data,True)
                return 0
        return -1


class MyDelegate(btle.DefaultDelegate):
    message = Message()
    def __init__(self, params = None):
        btle.DefaultDelegate.__init__(self)

    def handleNotification(self, cHandle, data):
        status = self.message.append(data)
        if status == 1:
            self.message.decode()
        elif status == -1:
            log.error("Not a valid message")
            log.error(self.message)


class RolandPiano(btle.Peripheral):
    service_uuid        = "03b80e5a-ede8-4b33-a751-6ce34ec4c700"
    characteristic_uuid = "7772e5db-3868-4112-a1a9-f2669d106bf3"
    setup_data = b"\x01\x00"

    def build_handle_table(self):
        cols = ['handle','uuid_bytes','uuid_str']
        rows = []
        for desc in self.getDescriptors():
            rows.append(pd.DataFrame([{'handle' : desc.handle, 'uuid_bytes' : desc.uuid, 'uuid_str' : str(desc.uuid)}],columns = cols))

        self.handle_table = pd.concat(rows)

    def get_checksum(self,addr,data):
        total = 0
        for b in addr:
            total += b
        for b in data:
            total += b        
        return int_to_byte(128 - (total % 128))        

    def access_register(self,addressName,data=None):
        readRegister = False

        addr      = addresses[addressName]
        ut        = self.get_unix_time()
        header    = self.get_header(ut)
        timestamp = self.get_timestamp(ut)      

        if data == None: # Read register
            data      = b"\x00\x00\x00" + int_to_byte(get_address_size(addressName))
            readRegister = True

        checksum = self.get_checksum(addr,data)
        cmd      = lut['cmd_read'] if readRegister else lut['cmd_write']

        msg_base = header + timestamp + lut['sysex_msg_start'] + \
            lut['id_roland'] + \
            cmd + \
            addr + \
            data + \
            checksum  

        if readRegister:
            msg_pt2 = header + timestamp + lut['sysex_msg_end']
            self.writeCharacteristic(16,msg_base,withResponse=False)
            self.writeCharacteristic(16,msg_pt2,withResponse=False)
        else:
            msg = msg_base + timestamp + lut['sysex_msg_end']
            self.writeCharacteristic(16,msg)

        self.waitForNotifications(2.0)


    def read_register(self,addressName):
        self.access_register(addressName)

    def write_register(self,addressName,data):
        self.access_register(addressName,data)


    def read_field(self,field):
        if field in fields:
            (data,isNew) = fields[field]
            if isNew:
                fields[field] = (data,False)
            return (data, isNew)
        else:
            return ("", False)

    def print_fields(self,fields, onlyUpdates = False):
        for field in fields:
            (data,isNew) = self.read_field(field)
            if onlyUpdates and not isNew:
                continue
            else:
                parser = get_parser(field)
                log.info(f"{field}: {parser(data)}")

    def update_fields(self,fields):
        for field in fields:
            self.read_register(field)

    def get_header(self,unix_time):
        mask_header    = b'\x7f'
        return ((mask_header[0]    & unix_time[0]) | b'\x80'[0]).to_bytes(1,byteorder='little') #0b10000000
    
    def get_timestamp(self,unix_time):
        mask_timestamp = b'\x3f'
        return ((mask_timestamp[0] & unix_time[0]) | b'\x80'[0]).to_bytes(1,byteorder='little') #0b10000000

    def get_unix_time(self):
        return int(bin(int(time.time()))[-8:],2).to_bytes(1,byteorder='little')

    def play_note(self,note, force):
        note  = note_string_to_midi(note)
        force = int_to_byte(force)

        ut = self.get_unix_time()

        msg = self.get_header(ut) + self.get_timestamp(ut) + lut['note_on'] + note + force
        self.writeCharacteristic(16,msg) # 16 is the handler of the midi characteristic

    def get_handle(self,uuid):
        return self.handle_table.loc[self.handle_table['uuid_str'].str.contains(uuid)].at[0,'handle']

    def get_uuid(self,handle):
        return self.handle_table.loc[self.handle_table['handle'] == handle].at[0,'uuid_bytes']

    def read_all_characteristics(self):
        for _,row in self.handle_table.iterrows():
            self.readCharacteristic(row['handle'])

    isInitialized = False
    def connect(self, max_attempts):
        for attempt_num in range(1,max_attempts+1):
            try:
                log.info(f"Attempt {attempt_num} to connect to {self.mac_addr}")
                if not self.isInitialized:
                    btle.Peripheral.__init__(self, self.mac_addr,"random")
                    self.isInitialized = True
                else:
                    btle.Peripheral.connect(self,self.mac_addr,"random")
                break
            except Exception:
                if attempt_num < max_attempts:
                    continue
                else:
                    log.error(f"Was not able to connect to {self.mac_addr} after {max_attempts} attempts..")
                    return False
        log.info(f"Connection with {self.mac_addr} established")
        return True

    def __init__(self,mac_addr):
        self.mac_addr = mac_addr
        self.connect(3)

        self.midi_ble_service = self.getServiceByUUID(self.service_uuid)
        self.midi_ble_characteristic = self.midi_ble_service.getCharacteristics(self.characteristic_uuid)[0]

        self.build_handle_table()

        self.read_all_characteristics()

        self.setDelegate(MyDelegate())
        
        self.writeCharacteristic(self.get_handle('2902'),self.setup_data,withResponse=False)
        if not self.readCharacteristic(self.get_handle('2902')) == self.setup_data:
            log.error("Notification not correctly set in descriptor")
        self.write_register('connection',b"\x01")
        log.info("Initialisation sequence completed")

    def idle(self):
        try:
            self.waitForNotifications(0.0166)
            return
        except btle.BTLEDisconnectError:
            log.error("Disconnected from device, attemping to reconnect")
            if self.connect(3):
                return
            else:
                log.critical("Could not reconnect, exitting")
                raise     



