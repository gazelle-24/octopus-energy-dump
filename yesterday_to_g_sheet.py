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
WORKSHEET = os.getenv('WORKSHEET')

def main():
    # Work out dates
    today = date.today()
    yesterday = today - timedelta(days=1)
    if time.daylight == 0:
        start_datetime = f"{yesterday.strftime('%Y-%m-%d')}T00:00:00Z"
        end_datetime = f"{yesterday.strftime('%Y-%m-%d')}T23:30:00Z"
    else:
        day_before_yesterday = today - timedelta(days=2)
        start_datetime = f"{day_before_yesterday.strftime('%Y-%m-%d')}T23:00:00Z"
        end_datetime = f"{yesterday.strftime('%Y-%m-%d')}T22:30:00Z"

    # Get the data from Octopus
    res_list = []
    r = requests.get(f"https://api.octopus.energy/v1/electricity-meter-points/{MPAN}/meters/{SERIAL_NUMBER}/consumption/?period_from={start_datetime}&period_to={end_datetime}&order_by=period", auth=(API_KEY, ''))
    for i in r.json()['results']:
        res_list.append([i['consumption'], i['interval_start'], i['interval_end']])

    # Now add it to the Google Sheet
    service_account = gspread.service_account()
    sheet = service_account.open(SHEET)
    worksheet = sheet.worksheet(WORKSHEET)
    worksheet.append_rows(res_list)

if __name__ == "__main__":
    main()