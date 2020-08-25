from bluepy import btle
import time
import pandas as pd
# 1. Install library: https://github.com/IanHarvey/bluepy
# 2. Add the following lines in: /etc/bluetooth/main.conf
#     EnableLE = true           # Enable Low Energy support. Default is false.
#     AttributeServer = true    # Enable the GATT attribute server. Default is false.

# def enable_notify(self,  chara_uuid):
#     notify = self.ble_conn.getCharacteristics(uuid=chara_uuid)[0]
#     notify_handle = notify.getHandle() + 1
#     self.ble_conn.writeCharacteristic(notify_handle, setup_data, withResponse=True)

class MyDelegate(btle.DefaultDelegate):
    def __init__(self, params = None):
        btle.DefaultDelegate.__init__(self)
        # ... initialise here

    def handleNotification(self, cHandle, data):
        # ... perhaps check cHandle
        # ... process 'data'
        print(data)


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


def int_to_byte(num):
    return num.to_bytes(1,byteorder='big')

def byte_to_int(byte):
    return int.from_bytes(byte,byteorder='big')

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




mac_addr_roland_fp_10        = "c3:14:a9:3e:8f:77"  





class RolandPiano(btle.Peripheral):
    service_uuid        = "03b80e5a-ede8-4b33-a751-6ce34ec4c700"
    characteristic_uuid = "7772e5db-3868-4112-a1a9-f2669d106bf3"
    setup_data = b"\x01\x00"

    # http://www.chromakinetics.com/handsonic/rolSysEx.htm
    lut_midi = {
        'msg_start' : b'\xf0',
        'msg_end'   : b'\xf7',
        'id_roland' : b'\x41',
        'id_device' : b'\x10',
        'id_fp10'   : b'\x28',
        'cmd_write' : b'\x12',
        'cmd_read'  : b'\x11',
    }

    lookup_status = {
        'note_on_ch0' : b'\x90'}
        

    def build_handle_table(self):
        cols = ['handle','uuid_bytes','uuid_str']
        rows = []
        for desc in self.getDescriptors():
            rows.append(pd.DataFrame([{'handle' : desc.handle, 'uuid_bytes' : desc.uuid, 'uuid_str' : str(desc.uuid)}],columns = cols))

        self.handle_table = pd.concat(rows)

    def read_register(self,addr):
        ut        = self.get_unix_time()
        header    = self.get_header(ut)
        timestamp = self.get_timestamp(ut)

        
        total = 0
        for b in addr:
            total += b
        total += 8 # data is fixed to 00000008
        checksum = int_to_byte(128 - (total % 128))

        msg = header + timestamp + self.lut_midi['msg_start'] + \
            self.lut_midi['id_roland'] + \
            self.lut_midi['id_device'] + \
            b"\x00\x00\x00" + \
            self.lut_midi['id_fp10'] + \
            self.lut_midi['cmd_read'] + \
            addr + \
            b"\x00\x00\x00\x08" + \
            checksum + \
            timestamp + \
            self.lut_midi['msg_end']
        
        # TODO: check if msg exceeds BLE size
        print(msg.hex())
        print(self.writeCharacteristic(16,msg))
            


        # <header> <timestamp> f0 41 10 00 00 00 28 12 <addr 4> <data> <checksum> <timestamp>
        pass

    def write_register(self,addr,data):
        pass

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

        msg = self.get_header(ut) + self.get_timestamp(ut) + self.lookup_status['note_on_ch0'] + note + force
        self.writeCharacteristic(16,msg) # 16 is the handler of the midi characteristic

    def get_handle(self,uuid):
        return self.handle_table.loc[self.handle_table['uuid_str'].str.contains(uuid)].at[0,'handle']

    def get_uuid(self,handle):
        return self.handle_table.loc[self.handle_table['handle'] == handle].at[0,'uuid_bytes']

    def read_all_characteristics(self):
        for _,row in self.handle_table.iterrows():
            self.readCharacteristic(row['handle'])

    def __init__(self,mac_addr):
        btle.Peripheral.__init__(self, mac_addr,"random")
        self.midi_ble_service = self.getServiceByUUID(self.service_uuid)
        self.midi_ble_characteristic = self.midi_ble_service.getCharacteristics(self.characteristic_uuid)[0]

        self.build_handle_table()

        self.read_all_characteristics()

        print(f"Type of piano: {self.readCharacteristic(self.get_handle('2a00'))}") # device_name

        # Enable notifications (Not working)
        self.writeCharacteristic(self.get_handle('2902'),self.setup_data,withResponse=True)
        if not self.readCharacteristic(self.get_handle('2902')) == b'\x01\x00':
            print("Notification not correctly set in descriptor")
        self.setDelegate(MyDelegate())






fp10 = RolandPiano(mac_addr_roland_fp_10)

fp10.play_note("C-3",50)
time.sleep(1)
fp10.play_note("C-4",50)
fp10.read_register(addresses['uptime'])



fp10.disconnect()








     

    


    

