# -*- coding: UTF8 -*-

import folium
import urllib2
import xml.etree.ElementTree as ET

from constants import *


def parse_google_xml_response(xml):
    root = ET.fromstring(xml)
    if root.find('status').text != 'OK':
        return 1
    results = []
    for result in root.findall('result'):
        place = dict()
        if result.find('name') is not None:
            place['name'] = result.find('name').text
        else:
            place['name'] = ''
        if result.find('vicinity') is not None:
            place['vicinity'] = result.find('vicinity').text
        else:
            place['vicinity'] = ''
        if result.find('geometry') is not None:
            place['lng'] = result.find('geometry').find('location').find('lng').text
        else:
            place['lng'] = ''
        if result.find('geometry') is not None:
            place['lat'] = result.find('geometry').find('location').find('lat').text
        else:
            place['lat'] = ''
        if result.find('type') is not None:
            s = ''
            for type in result.findall('type'):
                s += type.text + ';'
            s = s[:-1]
            place['types'] = s
        else:
            place['types'] = ''
        results.append(place)
    return results


def get_google_info(latitude, longitude, radius, key, types):
    try:
        if not types:
            url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/xml?location=%s,%s&radius=%s&key=%s' % (
                latitude, longitude, radius, key)
        else:
            url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/xml?location=%s,%s&radius=%s&types=%s&key=%s' % (
                latitude, longitude, radius, types, key)
        response = urllib2.urlopen(url)
        xml = response.read()
        return parse_google_xml_response(xml)
    except Exception as e:
        # TODO Remove print and add logger
        print  e
        return 1


def find_lat_long(country, key):
    url = 'https://maps.googleapis.com/maps/api/geocode/xml?components=country:%s&key=%s' % \
          (country, key)
    response = urllib2.urlopen(url)
    xml = response.read()
    root = ET.fromstring(xml)
    for result in root.findall('result'):
        if result.find('geometry') is not None:
            lat = result.find('geometry').find('location').find('lat').text
            lon = result.find('geometry').find('location').find('lng').text
        else:
            lat = 190
            lon = 190
    return lat, lon


# TODO Review word in spanish as ciudad, lugares, etc. Change by city
def get_places(country, key, radio=10000, types=None):
    lat, lon = find_lat_long(country, key)
    if lat == 190:
        return 'Error al meter los datos'
    else:
        if not types:
            lugares = get_google_info(lat, lon, radio, key, types)
        else:
            lugares = []
            for i in types:
                lugar = get_google_info(lat, lon, radio, key, i)
                lugares.append(lugar)
        return (float(lat), float(lon), lugares)


# TODO Hacer clase de test con todos los paises de la lista, creo que a veces da error porque algunos no tienen museos. Vigilar esos errores
def generate_pois(country_code):
    print country_code
    lat_origen, lon_origen, lugares = get_places(country_code, GOOGLE_KEY, types=POI_TYPES)
    restaurant = lugares[0]
    bank = lugares[1]
    museum = lugares[2]
    map = folium.Map(location=[lat_origen, lon_origen], zoom_start=12)

    # creamos los marcadores con los puntos donde se situan los POIs
    for dicc in museum:
        lat = float(dicc['lat'])
        lon = float(dicc['lng'])
        name = dicc['name']
        folium.Marker([lat, lon], popup=name, icon=folium.Icon(color='red', icon='info-sign')).add_to(map)

    # Para probar exportamos a un html y vemos si ha funcionado
    map.save(POI_FILE)


'''
if __name__ == '__main__':
    # TODO INPUT
    lat_origen, lon_origen, lugares = get_places('BE', GOOGLE_KEY, types=POI_TYPES)

    restaurant = lugares[0]
    bank = lugares[1]
    museum = lugares[2]
    map = folium.Map(location=[lat_origen, lon_origen], zoom_start=12)

    # creamos los marcadores con los puntos donde se situan los POIs
    for dicc in museum:
        lat = float(dicc['lat'])
        lon = float(dicc['lng'])
        name = dicc['name']
        folium.Marker([lat, lon], popup=name, icon=folium.Icon(color='red', icon='info-sign')).add_to(map)

    # Para probar exportamos a un html y vemos si ha funcionado
    map.save('map.html')
'''
