import geonamescache
gc = geonamescache.GeonamesCache()
all_cities = {c["name"].lower() for c in gc.get_cities().values()}

def validateCity(city):
    return city.lower() in all_cities

# # Example:
# print(is_valid_city_offline("Thane(West)"))
# print(is_valid_city_offline("Gotham"))