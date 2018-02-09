import requests
import json

URL = 'https://api.tfl.gov.uk/'

def get_url(url, payload=None):
    url = url + '?app_id=2a3e2338&app_key=240b28f5941f4c099fc40f5af851d5d6'
    response = requests.get(url, params=payload)
    content = response.content.decode('utf8')
    return content

def get_json_from_url(url,payload=None):
    content = get_url(url,payload)
    js = json.loads(content)
    return js

def getTubeStatus():
    url = URL + 'Line/Mode/Tube/Status'
    js = get_json_from_url(url)
    tubeStat = []
    N = len(js)
    for i in range(N):
        tubeStat.append({'id':js[i]['id'],'status':js[i]['lineStatuses'][0]['statusSeverityDescription']})
    return tubeStat

def getNearbytubes(location):
    nearbyTubes = []
    url = URL + 'StopPoint'
    noOfStopPoints = 0
    radius = 1000

    while (noOfStopPoints==0 and radius<3000):
        payload =  {'stopTypes':'NaptanMetroStation',
                    'modes':'tube',
                    'radius':radius,
                    'lat':float(location['latitude']),
                    'lon':float(location['longitude'])
                    }
        js = get_json_from_url(url,payload)
        if(len(js['stopPoints'])>0):
            noOfStopPoints+=len(js['stopPoints'])
        radius+=300
        print(noOfStopPoints,radius)

    for i in range(len(js['stopPoints'])):
        id = js['stopPoints'][i]['id']
        commonName = js['stopPoints'][i]['commonName']
        dist = int(round(js['stopPoints'][i]['distance'], 0))
        nearbyTubes.append({'id':id, 'commonName':commonName, 'dist':dist})

    return nearbyTubes

def getLinesServingStation(tube_station_id):
    lines = []
    url = URL + 'StopPoint/ServiceTypes'
    payload = {'id':tube_station_id,'modes':'tube'}

    js_array = get_json_from_url(url,payload)
    for i in range(len(js_array)):
        lines.append(js_array[i]['lineName'])
    return lines

def getNextTrainArrivals(tube_station_id, lines):
    trainArrivals = []
    time_a = 999999
    a_dest = 'N/A'
    time_b = 999999
    b_dest = 'N/A'
    time_c = 999999
    c_dest = 'N/A'
    for line in lines:
        url = URL + 'Line/' + line + '/Arrivals/' + tube_station_id
        js = get_json_from_url(url)
        for i in range(len(js)):
            if (time_a>js[i]['timeToStation']):
                time_a=js[i]['timeToStation']
                a_dest=js[i]['towards']
        for i in range(len(js)):
            if (time_b>js[i]['timeToStation'] and js[i]['timeToStation']!=time_a):
                time_b=js[i]['timeToStation']
                b_dest=js[i]['towards']
        for i in range(len(js)):
            if (time_c>js[i]['timeToStation'] and js[i]['timeToStation']!=time_a and js[i]['timeToStation']!=time_b):
                time_c=js[i]['timeToStation']
                c_dest=js[i]['towards']
        nextTrainByLine = {'line':line, 'next_arrival':[round(time_a/60,1),round(time_b/60,1),round(time_c/60,1)], 'towards':[a_dest,b_dest,c_dest]}
        trainArrivals.append(nextTrainByLine)

    return trainArrivals
