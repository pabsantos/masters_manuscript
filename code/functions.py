import datetime

columns = {
    'RMC': ['Date', 'Time', 'X', 'Y',
            'Latitude', 'Longitude'],
    'VTG': ['Heading', 'Knots', 'M/H', 'KM/H'],
    'GGA': ['Altitude (m)', 'Altitude (ft)'],
    'GLL': ['Valid?']
}

def RMCData(msg):
    '''
    Date, Time, X, Y, Latitude, Longitude
    Brasilia Time (BRT), UTC -3
    '''
    try:
        UTC = datetime.datetime.combine(msg.datestamp, msg.timestamp)
        BR = UTC - datetime.timedelta(hours=3)

        return [BR.date().isoformat(), BR.time().isoformat(), msg.longitude,
                msg.latitude, msg.latitude, msg.longitude]
    except:
        return ['', '', msg.longitude, msg.latitude, msg.latitude, msg.longitude]

def VTGData(msg):
    '''
    Heading, Knots, M/H, KM/H
    '''
    try:
        knot = float(msg.spd_over_grnd_kts)
        knot2mh = 1.15078
        miles = knot2mh * knot
        heading = msg.true_track
        kmhr = msg.spd_over_grnd_kmph

        return [heading, knot, miles, kmhr]
    except:
        return ['', '', '', '']

def GGAData(msg):
    '''
    Altitude (m), Altitude (ft)
    '''
    meter2feet = 3.28084
    try:
        feet = meter2feet * msg.altitude
        return [msg.altitude, feet]
    except:
        return ['', '']

def GLLData(msg):
    '''
    Valid?
    '''
    status = False
    if msg.status == 'A':
        status = True

    return [status]

functions = {
    'RMC': RMCData,
    'VTG': VTGData,
    'GGA': GGAData,
    'GLL': GLLData,
}

