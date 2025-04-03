import json

tranformed_cities = []
with open("cities.json", "r") as cities_json:
    cities = json.loads(cities_json.read())
    id = 0
    for city in cities:
        tranformed_cities.append({
            "id": id,
            "name": city["name"],
            "population": city["population"],
            "province": city["province"]
        })
        id += 1
    
with open("cities.json", "w") as cities_json:
    cities_json.write(json.dumps(tranformed_cities))
