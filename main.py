import csv
import requests
import os
import folium
from settings import APIKEY_YANDEX_GEO
from geopy import distance
from pprint import pprint
from flask import Flask


NEAREST_TOILETS_AMOUNT = 5


def fetch_coordinates(apikey, place):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    params = {"geocode": place, "apikey": apikey, "format": "json"}
    response = requests.get(base_url, params=params)
    response.raise_for_status()
    places_found = response.json(
    )['response']['GeoObjectCollection']['featureMember']
    most_relevant = places_found[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


def get_user_coordinates(asked_user_location):
    user_coordinates = fetch_coordinates(
        APIKEY_YANDEX_GEO, asked_user_location)
    user_lon, user_lat = user_coordinates
    user_coordinates = user_lat, user_lon
    return user_coordinates


def get_toilet_distance(toilet):
    return toilet['distance']


def create_geo_html(nearest_toilets, user_coordinates):
    map_structure = folium.Map(
        location=user_coordinates,
        zoom_start=12,
        tiles='OpenStreetMap'
    )

    tooltip = 'Жми!'

    for toilet in nearest_toilets:
        toilet_name = toilet['title']
        toilet_lat = toilet['latitude']
        toilet_lon = toilet['longitude']
        toilet_coord = [toilet_lat, toilet_lon]
        folium.Marker(toilet_coord, popup='<b>{}</b>'.format(toilet_name),
                      icon=folium.Icon(color='green'),
                      tooltip=tooltip).add_to(map_structure)

    folium.Marker(
        user_coordinates,
        popup='<i>Ваше местоположение</i>',
        icon=folium.Icon(color='red', icon='info-sign'),
        tooltip=tooltip
    ).add_to(map_structure)
    map_structure.save('index.html')


def open_geo_html():
    with open('index.html') as file:
        return file.read()


def convert_csv_to_list_of_dicts(csv_public_toilets):
    reader = csv.DictReader(csv_public_toilets, delimiter='\t')
    list_public_toilets = []
    for line in reader:
        dict_public_toilets = {
            'address_id': line['address_id'],
            'address_organisation': line['address_organisation'],
            'address_organisationsbereich': line['address_organisationsbereich'],
            'bezeichnung': line['bezeichnung'],
            'address_ort': line['address_ort'],
            'latitude': line['latitude'],
            'longitude': line['longitude'],
            'service_oeffnungszeiten': line['service_oeffnungszeiten'],
            'service_bezeichnung': line['service_bezeichnung'],
            'service_anzeigename': line['service_anzeigename'],
            'service_beschreibung': line['service_beschreibung'],
            'service_kurzbeschreibung': line['service_kurzbeschreibung'],
            'gebuehren': line['gebuehren'],
            'duschen': line['duschen']
        }
        list_public_toilets.append(dict_public_toilets)
    return list_public_toilets


def create_toilets_with_distances(public_toilets):
    toilets_with_distances = []
    for toilet_data in public_toilets:
        toilet_name = toilet_data['bezeichnung']
        toilet_lon = toilet_data['longitude']
        toilet_lat = toilet_data['latitude']
        target_toilet_coordinates = toilet_lat, toilet_lon
        distance_to_target = distance.distance(
            user_coordinates, target_toilet_coordinates).km
        toilet_geoinfo = {
            'distance': distance_to_target,
            'latitude': toilet_lat,
            'longitude': toilet_lon,
            'title': toilet_name
        }
        toilets_with_distances.append(toilet_geoinfo)
    return toilets_with_distances


if __name__ == "__main__":
    with open("oeffentlichetoilettenmuenchen2016-06-28.csv") as csv_public_toilets:
        public_toilets = convert_csv_to_list_of_dicts(csv_public_toilets)

    asked_user_location = input('Где вы находитесь? ')
    user_coordinates = get_user_coordinates(asked_user_location)
    toilets_with_distances = create_toilets_with_distances(public_toilets)

    nearest_toilets = sorted(
        toilets_with_distances, key=get_toilet_distance)[:NEAREST_TOILETS_AMOUNT]

    create_geo_html(nearest_toilets, user_coordinates)
    app = Flask(__name__)
    app.add_url_rule('/', 'hello', open_geo_html)
    app.run('0.0.0.0')
