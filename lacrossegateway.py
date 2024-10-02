import re

matchList = [
    ("^\\S+\\s+24", "PCA301"),
    ("^\\S+\\s+22", "EC3000"),
    ("^\\S+\\s+9", "LaCrosse"),
    ("^OK\\sWS\\s", "LaCrosseWS"),
    ("^OK\\sEMT7110\\s", "EMT7110"),
    ("^OK\\sLS\\s", "Level"),
    ("^OK\\sVALUES\\s", "KeyValueProtocol"),
    ("^OK\\sCL\\s", "CapacitiveLevel"),
    ("^\[LaCrosseITPlusRead", "Info"), # LGW command = v
    ("", "Nodevice"), #
]
def decodeEC3k(data):
    """
    The output can be:
    - OK 22 208 36 0 74 46 236 0 74 46 236 0 5 175 116 0 44 42 79 4 0
    """
    regex = re.compile(r'OK (\d+) (\d+) (\d+) (\d+) (\d+) (\d+) (\d+) (\d+) (\d+) (\d+) (\d+) (\d+) (\d+) (\d+) (\d+) (\d+) (\d+) (\d+) (\d+) (\d+) (\d+)')
    match = regex.match(data)
    if match:
        data = [int(c) for c in match.group().split()[1:]]
        sensortype = data[0]
        sensorid = ''.join(f'{i:02X}' for i in [data[1], data[2]]) # str([f'{i:02x}' for i in [data[1], data[2]]])
        ontime = ((data[3] * 16777216) + (data[4] * 65536) + (data[5] * 256) + data[6])/3600
        totaltime = ((data[7] * 16777216) + (data[8] * 65536) + (data[9] * 256) + data[10])/3600
        energy = ((data[11] * 16777216) + (data[12] * 65536) + (data[13] * 256) + data[14])
        power = ((data[15] * 256) + data[16])/10
        maxpower = ((data[17] * 256) + data[18])/10
        resets = data[19]
        return sensorid, power, energy

def decodeLaCrosse(data):
    """
    The output can be:
    - OK 9 248 1 4 150 106
    """
    regex = re.compile(r'OK (\d+) (\d+) (\d+) (\d+) (\d+) (\d+)')
    match = regex.match(data)
    if match:
        data = [int(c) for c in match.group().split()[1:]]
        sensorid = data[1]
        sensortype = data[2] & 0x7f
        new_battery = True if data[2] & 0x80 else False
        temperature = float(data[3] * 256 + data[4] - 1000) / 10
        humidity = data[5] & 0x7f
        low_battery = True if data[5] & 0x80 else False
        return sensorid, temperature, humidity

def decodeLaCrosseWS(data):
    """
    The output can be:
    - OK WS 0 4 4 96 50 255 255 255 255 255 255 255 255 0 255 255 255 255 255 255 255 255 255 255 255
    """
    regex = re.compile(r'OK WS (\d+) (\d+) (\d+) (\d+) (\d+) (\d+) (\d+) (\d+) (\d+) (\d+) (\d+) (\d+) (\d+) (\d+) (\d+) (\d+) (\d+) (\d+) (\d+) (\d+) (\d+) (\d+) (\d+) (\d+) (\d+)')
    match = regex.match(data)
    if match:
        data = [int(c) for c in match.group().split()[2:]]
        typenumber = data[1]
        new_battery = True if data[13] & 0x01 else False
        temperature = float(data[2] * 256 + data[3] - 1000) / 10
        humidity = data[4] & 0x7f
        #determ hum_status
        #0=Normal 30-45%
        #1=Comfortable 45-70%
        #2=Dry < 30%
        #3=Wet > 70%
        if humidity <= 30:
            hum_status = 2
        if 30 <= humidity <= 45:
            hum_status = 0
        if 45 <= humidity <= 70:
            hum_status = 1
        if 70 <= humidity:
            hum_status = 3
        low_battery = True if data[13] & 0x04 else False
        return typenumber, temperature, humidity, hum_status

def decodeKVP(data):
    """
    The output can be:
    - OK VALUES LGW 8936539 UpTimeSeconds=280010,UpTimeText=3Tg. 5Std. 46Min. 50Sek. ,WIFI=myaccespoint,ReceivedFrames=76447,FramesPerMinute=24,RSSI=-19,FreeHeap=24888,LD.Min=0.52,LD.Avg=0.53,LD.Max=26.46,OLED=none
    """

def decodePCA301(data):
    regex = re.compile(r"OK 24 (\d+) 4 (\d+) (\d+) (\d+) (\d+) (\d+) (\d+) (\d+) (\d+)")
    match = regex.match(data)
    if match:
        data = [int(c) for c in match.group().split()[1:]]
        line = match.group().split(" ")
        sensorid = (str(line[4]).zfill(3) + str(line[5]).zfill(3) + str(line[6]).zfill(3))
        power = (int(line[8]) * 256 + int(line[9])) / 10.0
        state = int(line[7])
        consumption = (int(line[10]) * 256 + int(line[11])) / 100.0
        return sensorid, power, consumption

def decodeInfo(data):
    """
    The output can be:
    - [LaCrosseITPlusReader.10.1s (RFM12B f:0 r:17241)]
    - [LaCrosseITPlusReader.10.1s (RFM12B f:0 t:10~3)]
    - [LaCrosseITPlusReader.Gateway.1.35 (1=RFM69 f:868300 r:8) {IP=192.168.178.40}]
    - [LaCrosseITPlusReader.Gateway.1.35 (1=RFM69 f:868300 r:20000) {IP=192.168.1.7}]
    """
    re_info = re.compile(
        r'\[(?P<name>\w+\.\w+).(?P<ver>.*) ' +
        r'\(1=(?P<rfm1name>\w+) (\w+):(?P<rfm1freq>\d+) ' +
        r'(?P<rfm1mode>.*)\) {IP=(?P<address>.*)}\]')

    info = {
        'name': None,
        'version': None,
        'address': None,
        'rfm1name': None,
        'rfm1frequency': None,
        'rfm1datarate': None,
        'rfm1toggleinterval': None,
        'rfm1togglemask': None,
    }
    match = re_info.match(data)
    if match:
        info['name'] = match.group('name')
        info['version'] = match.group('ver')
        info['address'] = match.group('address')
        info['rfm1name'] = match.group('rfm1name')
        info['rfm1frequency'] = match.group('rfm1freq')
        values = match.group('rfm1mode').split(':')
        if values[0] == 'r':
            info['rfm1datarate'] = values[1]
        elif values[0] == 't':
            toggle = values[1].split('~')
            info['rfm1toggleinterval'] = toggle[0]
            info['rfm1togglemask'] = toggle[1]

    return info

def parse(Data):
    data = Data.decode('utf-8').strip('\r\n')
    for pattern, sensortype in matchList:
        if re.search(pattern, data):
            return sensortype, data
    else:
        return None
