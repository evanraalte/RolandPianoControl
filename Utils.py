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
    return answer 


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


bound_max = {
    "masterVolume" : 100,
    "sequencerTempoRO" : 250,
}

bound_min= {
    "masterVolume" : 0,
    "sequencerTempoRO" : 0,
}

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
    try:
        return list(addresses.keys())[list(addresses.values()).index(address)]
    except ValueError:
        return "unknown"

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


rotary_encoder_mapping = [
    "masterVolume",
    "sequencerTempoWO"
]