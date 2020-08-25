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
    "serverSetupFileName":            "01000000",
    # 010001xx
    "songToneLanguage":               "01000100",
    "keyTransposeRO":                 "01000101",
    "songTransposeRO":                "01000102",
    "sequencerStatus":                "01000103",
    "sequencerMeasure":               "01000105",
    "sequencerTempoNotation":         "01000107",
    "sequencerTempoRO":               "01000108",
    "sequencerBeatNumerator":         "0100010A",
    "sequencerBeatDenominator":       "0100010B",
    "sequencerPartSwAccomp":          "0100010C",
    "sequencerPartSwLeft":            "0100010D",
    "sequencerPartSwRight":           "0100010E",
    "metronomeStatus":                "0100010F",
    "headphonesConnection":           "01000110",
    # 010002xx
    "keyBoardMode":                   "01000200",
    "splitPoint":                     "01000201",
    "splitOctaveShift":               "01000202",
    "splitBalance":                   "01000203",
    "dualOctaveShift":                "01000204",
    "dualBalance":                    "01000205",
    "twinPianoMode":                  "01000206",
    "toneForSingle":                  "01000207",
    "toneForSplit":                   "0100020A",
    "toneForDual":                    "0100020D",
    "songNumber":                     "01000210",
    "masterVolume":                   "01000213",
    "masterVolumeLimit":              "01000214",
    "allSongPlayMode":                "01000215",
    "splitRightOctaveShift":          "01000216",
    "dualTone1OctaveShift":           "01000217",
    "masterTuning":                   "01000218",
    "ambience":                       "0100021A",
    "headphones3DAmbience":           "0100021B",
    "brilliance":                     "0100021C",
    "keyTouch":                       "0100021D",
    "transposeMode":                  "0100021E",
    "metronomeBeat":                  "0100021F",
    "metronomePattern":               "01000220",
    "metronomeVolume":                "01000221",
    "metronomeTone":                  "01000222",
    "metronomeDownBeat":              "01000223",
    # 010003xx
    "applicationMode":                "01000300",
    "scorePageTurn":                  "01000302",
    "arrangerPedalFunction":          "01000303",
    "arrangerBalance":                "01000305",
    "connection":                     "01000306",
    "keyTransposeWO":                 "01000307",
    "songTransposeWO":                "01000308",
    "sequencerTempoWO":               "01000309",
    "tempoReset":                     "0100030B",
    # 010004xx
    "soundEffect":                    "01000400",
    "soundEffectStopAll":             "01000402",
    # 010005xx
    "sequencerREW":                   "01000500",
    "sequencerFF":                    "01000501",
    "sequencerReset":                 "01000502",
    "sequencerTempoDown":             "01000503",
    "sequencerTempoUp":               "01000504",
    "sequencerPlayStopToggle":        "01000505",
    "sequencerAccompPartSwToggle":    "01000506",
    "sequencerLeftPartSwToggle":      "01000507",
    "sequencerRightPartSwToggle":     "01000508",
    "metronomeSwToggle":              "01000509",
    "sequencerPreviousSong":          "0100050A",
    "sequencerNextSong":              "0100050B",
    # 010006xx
    "pageTurnPreviousPage":           "01000600",
    "pageTurnNextPage":               "01000601",
    # 010007xx
    "uptime":                         "01000700",
    # 010008xx
    "addressMapVersion":              "01000800"}


def int_to_byte(num):
    return num.to_bytes(1,byteorder='big')

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



class RolandPiano():
    service_uuid        = "03b80e5a-ede8-4b33-a751-6ce34ec4c700"
    characteristic_uuid = "7772e5db-3868-4112-a1a9-f2669d106bf3"
    setup_data = b"\x01\x00"
    midi_ble_dev = None

    lookup_status = {
        'note_on_ch0' : b'\x90'}
        

    def build_handle_table(self):
        cols = ['handle','uuid_bytes','uuid_str']
        rows = []
        for desc in self.midi_ble_dev.getDescriptors():
            rows.append(pd.DataFrame([{'handle' : desc.handle, 'uuid_bytes' : desc.uuid, 'uuid_str' : str(desc.uuid)}],columns = cols))

        self.handle_table = pd.concat(rows)

    def construct_msg(self,status_note, data):
        unix_time      = int(bin(int(time.time()))[-8:],2).to_bytes(1,byteorder='little')

        mask_header    = b'\x7f'
        mask_timestamp = b'\x3f'
        # https://devzone.nordicsemi.com/nordic/short-range-guides/b/bluetooth-low-energy/posts/midi-over-bluetooth-le
        header    = ((mask_header[0]    & unix_time[0]) | b'\x80'[0]).to_bytes(1,byteorder='little') #0b10000000
        timestamp = ((mask_timestamp[0] & unix_time[0]) | b'\x80'[0]).to_bytes(1,byteorder='little') #0b10000000

        status_note = b'\x90'

        return header + timestamp + status_note + data


    def play_note(self,note, force):
        note  = note_string_to_midi(note)
        force = int_to_byte(force)

        msg = self.construct_msg(self.lookup_status['note_on_ch0'],note + force)
        self.midi_ble_dev.writeCharacteristic(16,msg)

    def get_handle(self,uuid):
        return self.handle_table.loc[self.handle_table['uuid_str'].str.contains(uuid)].at[0,'handle']

    def get_uuid(self,handle):
        return self.handle_table.loc[self.handle_table['handle'] == handle].at[0,'uuid_bytes']

    def read_all_characteristics(self):
        for _,row in self.handle_table.iterrows():
            self.midi_ble_dev.readCharacteristic(row['handle'])

    def __init__(self,mac_addr):
        self.midi_ble_dev = btle.Peripheral(mac_addr,"random")
        self.midi_ble_service = self.midi_ble_dev.getServiceByUUID(self.service_uuid)
        self.midi_ble_characteristic = self.midi_ble_service.getCharacteristics(self.characteristic_uuid)[0]

        self.build_handle_table()

        self.read_all_characteristics()

        print(f"Type of piano: {self.midi_ble_dev.readCharacteristic(self.get_handle('2a00'))}")

        # # # Enable notifications
        # self.midi_ble_dev.writeCharacteristic(self.midi_ble_notify_handle,self.setup_data,withResponse=True)
        # if not self.midi_ble_dev.readCharacteristic(midi_ble_notify_handle) == b'\x01\x00':
        #     print("Notification not correctly set in descriptor")

    def disconnect(self):
        self.midi_ble_dev.disconnect()



fp10 = RolandPiano(mac_addr_roland_fp_10)

fp10.play_note("C-3",50)
time.sleep(1)
fp10.play_note("C-4",50)
fp10.disconnect()








     

    


    

