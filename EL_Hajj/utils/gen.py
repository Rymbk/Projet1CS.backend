import json
query = f"insert into registration_baladiya (id, name, wilaya) values"

def get_sql_value(value):
    if type(value) == str:
        escaped_quote = value.replace("'", "''")
        return f"""'{escaped_quote}'"""
    else:
        return value

def get_tuple(city):
    return f"({get_sql_value(city['id'])}, {get_sql_value(city['name'])}, {get_sql_value(city['province'])})"
with open("cities.json", "r") as cities_json:
    values = ',\n'.join(list(map(get_tuple, json.loads(cities_json.read()))))
    query = f"{query} {values}"
    with open("query.sql", "w") as query_file:
        query_file.write(query)

