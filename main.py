from bluepy import btle
import time
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


mac_addr     = "c3:14:a9:3e:8f:77"  
service_uuid = "03b80e5a-ede8-4b33-a751-6ce34ec4c700" # MIDI BLE service

setup_data = b"\x01\x00"


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


def construct_msg(data):
    unix_time      = int(bin(int(time.time()))[-8:],2).to_bytes(1,byteorder='little')

    mask_header    = b'\x7f'
    mask_timestamp = b'\x3f'
    # https://devzone.nordicsemi.com/nordic/short-range-guides/b/bluetooth-low-energy/posts/midi-over-bluetooth-le
    header    = ((mask_header[0]    & unix_time[0]) | b'\x80'[0]).to_bytes(1,byteorder='little') #0b10000000
    timestamp = ((mask_timestamp[0] & unix_time[0]) | b'\x80'[0]).to_bytes(1,byteorder='little') #0b10000000

    status_note = b'\x90'

    return header + timestamp + status_note + data


def play_note(dev,note_string,intensity_int):
    note = note_string_to_midi(note_string)
    force = int_to_byte(intensity_int)

    msg = construct_msg(note + force)
    midi_ble_dev.writeCharacteristic(16,msg)


def getNotificationHandle(dev,uuid):
    for desc in midi_ble_dev.getDescriptors():
        if uuid in str(desc.uuid):
            return desc.handle

try:
    midi_ble_dev = btle.Peripheral(mac_addr,"random")

    midi_ble_dev.setDelegate(MyDelegate())

    midi_ble_service = midi_ble_dev.getServiceByUUID(service_uuid)

    midi_ble_characteristic = midi_ble_service.getCharacteristics("7772e5db-3868-4112-a1a9-f2669d106bf3")[0]

    # Get notification handle
    midi_ble_notify_handle  = getNotificationHandle(midi_ble_dev,'2902')
    
    print(midi_ble_dev.readCharacteristic(midi_ble_notify_handle))
    # Enable notifications
    midi_ble_dev.writeCharacteristic(midi_ble_notify_handle,setup_data,withResponse=True)

    for desc in midi_ble_dev.getDescriptors():
            print(desc.handle, str(desc.uuid))
            midi_ble_dev.readCharacteristic(desc.handle) 

    print(midi_ble_dev.readCharacteristic(getNotificationHandle(midi_ble_dev,'2a00')))

    print(midi_ble_dev.readCharacteristic(midi_ble_notify_handle))

     

    play_note(midi_ble_dev,"C-0",50)
    play_note(midi_ble_dev,"C-1",50)
    play_note(midi_ble_dev,"C-2",50)
    play_note(midi_ble_dev,"C-3",50)
    play_note(midi_ble_dev,"C-4",50)
    play_note(midi_ble_dev,"C-5",50)
    play_note(midi_ble_dev,"C-6",50)
    


    
finally:
    if midi_ble_dev:
        midi_ble_dev.disconnect()
        print("Disconnected")   

