'''Download usage data for yesterday from Octopus Energy and send to Google Sheets'''

from dotenv import load_dotenv
from pathlib import Path
import os
import requests
import gspread
from datetime import date, timedelta
import time

load_dotenv()
env_path = Path('.')/'.env'
load_dotenv(dotenv_path=env_path)
MPAN = os.getenv('MPAN')
SERIAL_NUMBER = os.getenv('SERIAL_NUMBER')
API_KEY = os.getenv('API_KEY')
SHEET = os.getenv('SHEET')
WS_ELEC_CONSUMPTION = os.getenv('WS_ELEC_CONSUMPTION')
WS_YESTERDAY_TEMPS = os.getenv('WS_YESTERDAY_TEMPS')
LATITUDE = os.getenv('LATITUDE')
LONGITUDE = os.getenv('LONGITUDE')

today = date.today()
print('\n' + str(today)) # Output for logfile
yesterday = today - timedelta(days=1)

def get_electricity_consumption():
    if time.daylight == 0:
        start_datetime = f"{yesterday.strftime(r'%Y-%m-%d')}T00:00:00Z"
        end_datetime = f"{yesterday.strftime(r'%Y-%m-%d')}T23:30:00Z"
    else:
        day_before_yesterday = today - timedelta(days=2)
        start_datetime = f"{day_before_yesterday.strftime(r'%Y-%m-%d')}T23:00:00Z"
        end_datetime = f"{yesterday.strftime(r'%Y-%m-%d')}T22:30:00Z"

    # Get the data from Octopus
    res_list = []
    r = requests.get(f"https://api.octopus.energy/v1/electricity-meter-points/{MPAN}/meters/{SERIAL_NUMBER}/consumption/?period_from={start_datetime}&period_to={end_datetime}&order_by=period", auth=(API_KEY, ''))
    print(r.status_code)
    print(r.json())
    for i in r.json()['results']:
        res_list.append([i['consumption'], i['interval_start'].replace('T',' ')[:19], i['interval_end'].replace('T',' ')[:19]])

    return res_list

def get_yesterday_temps():
    r = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={LATITUDE}&longitude={LONGITUDE}&hourly=temperature_2m&start_date={yesterday.strftime(r'%Y-%m-%d')}&end_date={yesterday.strftime(r'%Y-%m-%d')}")
    print(r.json())
    if r.status_code == 200:
        res = []
        for i in range(24):
            res.append([
                f"{r.json()['hourly']['time'][i].replace('T', ' ')}:00",
                r.json()['hourly']['temperature_2m'][i]
            ])
        print(res)
        return res
    else:
        return [r.status_code]

def main():
    # Get data
    electricity_consumption = get_electricity_consumption()
    yesterday_temps = get_yesterday_temps()

    # Send to Google Sheets
    service_account = gspread.service_account()
    sheet = service_account.open(SHEET)
    ws_elec_consumption = sheet.worksheet(WS_ELEC_CONSUMPTION)
    ws_elec_consumption.append_rows(electricity_consumption)
    ws_yesterday_temps = sheet.worksheet(WS_YESTERDAY_TEMPS)
    ws_yesterday_temps.append_rows(yesterday_temps)

if __name__ == "__main__":
    main()
