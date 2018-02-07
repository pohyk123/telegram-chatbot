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
    payload =  {'stopTypes':'NaptanMetroStation',
                'modes':'tube',
                'lat':float(location['latitude']),
                'lon':float(location['longitude'])
                }

    js = get_json_from_url(url,payload)
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
    time_b = 999999
    for line in lines:
        url = URL + 'Line/' + line + '/Arrivals/' + tube_station_id
        js = get_json_from_url(url)
        for i in range(len(js)):
            if (time_a>js[i]['timeToStation']):
                time_a=js[i]['timeToStation']
        for i in range(len(js)):
            if (time_b>js[i]['timeToStation'] and js[i]['timeToStation']!=time_a):
                time_b=js[i]['timeToStation']
        nextTrainByLine = {'line':line, 'next_arrival':str(round(time_a/60,1))+', '+str(round(time_b/60,1))}
        trainArrivals.append(nextTrainByLine)

    return trainArrivals
