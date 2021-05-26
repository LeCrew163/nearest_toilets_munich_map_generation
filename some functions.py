# This function is only necessary if you would like to get distance to a particular place.
# Variable "target_bar_name" needs to be set.
def get_distance(user_coordinates):
    target_coordinates = fetch_coordinates(
        apikey_yandex_geo, target_bar_name)
    user_lon, user_lat = target_coordinates
    target_coordinates = user_lat, user_lon

    distance_to_target = distance.distance(
        user_coordinates, target_coordinates).km
    return distance_to_target
