import requests
from environs import Env
from geopy import distance


env = Env()
env.read_env()


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_place = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_place:
        return None

    most_relevant = found_place[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split("")
    return lon, lat


if __name__ == "__main__":
    apikey = env('YANDEX_API')
    print(apikey)
    coords = fetch_coordinates(apikey, "")
    print(coords)
