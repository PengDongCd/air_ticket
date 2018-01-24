import re
import requests
import urllib.parse
import yaml
import os
import io
from requests import RequestException
import json
from prettytable import PrettyTable

def load_yaml_config_file():
    file_path = os.path.join(os.getcwd(), 'config.yml')
    with io.open(file_path, 'r', encoding='utf-8') as stream:
        config = yaml.load(stream)
    return config

def get_flight_ticket():
    config = load_yaml_config_file()
    query_params = config.get('QueryParams')
    url = config.get('URL') + '?' + urllib.parse.urlencode(query_params)
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36",
        "Connection": "keep-alive",
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            json_pattern = re.compile(r'\{.+\}')
            json_str = json_pattern.search(response.text).group()
            data = json.loads(json_str).get('data')
            aircode_name_map = data.get('aircodeNameMap')
            airport_name_map = data.get('airportMap')
            flights_info = data['flight']
            for flight in flights_info:
                yield [
                    aircode_name_map.get(flight['airlineCode']),
                    flight['flightNo'],
                    airport_name_map.get(flight['depAirport']),
                    flight['depTerm'],
                    flight['depTime'],
                    flight['flightType'],
                    airport_name_map.get(flight['arrAirport']),
                    flight['arrTime'],
                    flight['cabin']['bestPrice']
                ]
        else:
            print("Can't got 200 when request URL")
    except RequestException:
        print("Request Failed")
        return None

def main():
    table = PrettyTable(["航空公司", "航班号", "起飞机场", "起飞航站楼", "起飞时间", "飞机", "到达机场", "到达时间", "价格"])
    table.padding_width = 3
    table.align = 'c'
    table.valign = 'm'
    for flight in get_flight_ticket():
        table.add_row(flight)
    print(table)

if __name__ == '__main__':
    main()