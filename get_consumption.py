'''Script to download consumption data from Octopus Energy API'''

from dotenv import load_dotenv
from pathlib import Path
import os
import requests
import csv

load_dotenv()
env_path = Path('.')/'.env'
load_dotenv(dotenv_path=env_path)

MPAN = os.getenv('MPAN')
SERIAL_NUMBER = os.getenv('SERIAL_NUMBER')
API_KEY = os.getenv('API_KEY')
OUTPUT_DIR = os.getenv('OUTPUT_DIR')

filepath_output = os.path.join(OUTPUT_DIR, "octopus_energy.csv")

def make_request(next):
    res = requests.get(next, auth=(API_KEY, ''))
    return res

def main():
    with open(filepath_output, 'w', newline='') as f:
        csv_writer = csv.writer(f, delimiter=',')

        start_datetime = input('Enter start date in format YYYY-MM-DD: ') + 'T00:00:00Z'
        end_datetime = input('Enter end date in format YYYY-MM-DD: ') + 'T00:00:00Z'
        print('Getting consumption data...')
        
        res_list = []
        next_res = None

        r = make_request(f"https://api.octopus.energy/v1/electricity-meter-points/{MPAN}/meters/{SERIAL_NUMBER}/consumption/?period_from={start_datetime}&period_to={end_datetime}&order_by=period")
        for i in r.json()['results']:
            res_list.append(i)
        if 'next' in r.json():
            next_res = r.json()['next']

        while True:
            if next_res is not None:
                next_res_request = make_request(next_res)
                for i in next_res_request.json()['results']:
                    res_list.append(i)
                if 'next' in next_res_request.json():
                    next_res = next_res_request.json()['next']
                else:
                    next_res is None
            else:
                break
        
        csv_writer.writerow([
            'consumption',
            'interval_start',
            'interval_end'
        ])

        for i in res_list:
            csv_writer.writerow([
                i['consumption'],
                i['interval_start'],
                i['interval_end'],
            ])

        print('...done!')

if __name__ == "__main__":
    main()