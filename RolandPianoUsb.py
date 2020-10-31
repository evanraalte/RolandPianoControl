import mido
import time
from Utils import *

import logging
log = logging.getLogger(__name__)

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
        

    def __init__(self,fields):
        self.fields = fields
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
        headerChanged = True #(data[0:1] != self.header_byte)
        isMidiMsg = len(data) == 5 and (data[2:3] in self.getAudioStatusCodes())
        return headerChanged or isMidiMsg

    def append(self,data):
        if self.isNewMsg(data):
            # new message, discard old message
            self.reset()
            try:
                # self.header_byte    = data[0:1]
                # self.timestamp_byte = data[1:2]
                self.status_byte    = data[0:1]
                self.buf            = data[1:]
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
            self.checksum = self.buf[l-1:l] 
            self.data     = self.buf[11:l-1]
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
                
                addr_name = get_address_name(self.address)

                if addr_name not in self.fields:
                    self.fields[addr_name] = (get_address_size(addr_name)*b"\x00",False)

                if self.fields[addr_name][0] != self.data: 
                    self.fields[get_address_name(self.address)] = (self.data,True)
                
                return 0
        return -1

class RolandPianoUsb():
    def get_checksum(self,addr,data):
        total = 0
        for b in addr:
            total += b
        for b in data:
            total += b        
        return int_to_byte((128 - (total % 128)) & 0x7f)  


    def access_register(self,addressName,data=None):
        readRegister = False
        addr      = addresses[addressName]   

        if data == None: # Read register
            data      = b"\x00\x00\x00" + int_to_byte(get_address_size(addressName))
            readRegister = True

        checksum = self.get_checksum(addr,data)
        cmd      = lut['cmd_read'] if readRegister else lut['cmd_write']

        msg_base = lut['id_roland'] + \
                   cmd + \
                   addr + \
                   data + \
                   checksum  
        # log.info(f"checksum: {checksum}")
        # log.info(msg_base)
        msg = mido.Message('sysex', data = msg_base)
        # print("xxx")
        # print(msg.hex()) # 'F0 41 10 00 00 00 28 12 01 00 03 06 01 75 F7'
        # log.info(msg.hex())
        self.port_out.send(msg)
        # time.sleep(0.5)


    def read_register(self,addressName):
        # print("yyy")
        self.access_register(addressName)

    def write_register(self,addressName,data):
        self.access_register(addressName,data)

    def play_note(self,note, force):
        note  = note_string_to_midi(note)
        # force = int_to_byte(force)

        msg = mido.Message('note_on',note=note,velocity=force)
        self.port_out.send(msg)


    def read_all(self):
        ret = {}
        for name in addresses.keys():
            # self.port_in  = mido.open_input(self.portName)
            self.read_register(name)
            ret[name] = ""
            time.sleep(0.1)
            for msg in self.port_in.iter_pending():
                ret[name] += " " + msg.hex()
            # self.port_in.close()
        return ret

    def read_field(self,field):
        if field in self.fields:
            (data,isNew) = self.fields[field]
            if isNew:
                self.fields[field] = (data,False)
            return (data, isNew)
        else:
            return ("", False)

    def print_fields(self,fields, onlyUpdates = False):
        for field in fields:
            (data,isNew) = self.read_field(field)
            if onlyUpdates and not isNew:
                continue
            else:
                try:
                    parser = get_parser(field)
                    # log.info(f"{field}: {parser(data)}")
                except Exception:
                    log.debug("Does not contain values yet")

    def set_fields(self,fields):
        self.requested_fields = fields

    def update_fields(self):
        for field in self.requested_fields:
            self.read_register(field)

    def add_pending_write_action(self,addr_name,incr):
        if addr_name in self.pending_write_actions:
            self.pending_write_actions[addr_name] += incr
        else:
            self.pending_write_actions[addr_name] = incr

    def perform_pending_write_actions(self):
        try:
            for address_name,incr in self.pending_write_actions.items():
                # Set correct read address
                if address_name == "sequencerTempoWO":
                    address_name_read = "sequencerTempoRO"
                else:
                    address_name_read = address_name

                # get current value
                if address_name_read not in self.fields:
                    self.fields[address_name_read] = (get_address_size(address_name_read)*b"\x00",False)
                
                # log.info(address_name)
                f = get_parser(address_name_read)
                cur_val = f(self.fields[address_name_read][0])
                # log.info(f"cur_val: {cur_val}")

                # add difference and do bound checks (increments can be larger than one, beware )
                if cur_val + incr > bound_max[address_name_read]:
                    new_val = bound_max[address_name_read]
                elif cur_val + incr < bound_min[address_name_read]:
                    new_val = bound_min[address_name_read]
                else:
                    new_val = cur_val + incr
                # log.info(f"new_val: {new_val}")
                # write to register
                f = get_reverse_parser(address_name)
                self.write_register(address_name,f(new_val))
                # Update fields manually
                self.fields[address_name_read] = (f(new_val),True)
            self.pending_write_actions = {}
        except Exception:
            log.exception(self.pending_write_actions)
            exit()
        # write_register

    def __init__(self,portName=None):
        log.info("init piano")
        if portName in mido.get_input_names():
            self.portName = portName
            self.port_in  = mido.open_input(portName)
            self.port_out = mido.open_output(portName)
            self.fields = {}
            self.pending_write_actions = {}
            self.has_pending_write_actions = False
            self.message = Message(self.fields)
            self.read_register('uptime') # 389
            self.read_register('addressMapVersion') #391
            msg = mido.Message('sysex',data = b"\x7e\x10\x06\x01")
            # print(msg.hex())
            self.port_out.send(msg)#399 (requestModelId)
            self.read_register('serverSetupFileName') #402
            self.write_register('connection',b"\x01") #409
            self.write_register('applicationMode',b"\x01") #410
            self.read_register('sequencerStatus') #411
            self.read_register('metronomeStatus') #415

            self.write_register('applicationMode',b"\x00") #410
            # self.port_in.close()
            # self.read_register('songToneLanguage') #420
            # self.read_register('songToneLanguage') #420
            # self.read_register('keyBoardMode') #424
            # self.read_register('masterVolume') #426
            # self.read_register('masterVolumeLimit') #426

            self.portsOpened = True


    def handle(self,msg):
        log.info(msg.hex())

    def disconnect(self):
        self.port_out.close()
        self.port_in.close()      

    def port_in_handler(self):
        # log.info("bleh")
        if self.portsOpened:
            for msg in self.port_in.iter_pending():
                status = self.message.append(msg.bin())
                # log.info(msg.hex())
                # log.info(status)
                if status == 1:
                    self.message.decode()

                elif status == -1:
                    log.error("Not a valid message")
                    log.error(self.message)


