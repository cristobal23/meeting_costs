from __future__ import print_function
import datetime
from dateutil import parser
from pprint import pprint
import pytz

from utils.calendar_service import get_google_cal_service
from utils.sheets_service import get_sheets_service

EMPLOYEES = {}
DEFAULT_HOURLY = 120000 / 260 / 8

def main():
    sheets_service = get_sheets_service()
    employee_data = get_employee_data(sheets_service)

    cal_service = get_google_cal_service()
    events = get_events(cal_service)
    display_events(events)


def get_events(service):
    events_result = service.events().list(
        calendarId='primary', 
        timeMin=get_start_date(),
        timeMax=get_end_date(), 
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    events = events_result.get('items', [])
    return events


def get_start_date():
    d = datetime.datetime(2019, 1, 1, 1, 0).isoformat() + 'Z'
    print("start date is %s" % d)
    return d


def get_end_date():
    d = datetime.datetime(2019, 1, 30, 1, 0).isoformat() + 'Z'
    print("end date is %s" % d)
    return d


def get_employee_data(service):
    SAMPLE_SPREADSHEET_ID = '1P50eMsvS8alWmd7Xdd3lxbOTp1mu7rg8SkE8NbIkD3U'
    SAMPLE_RANGE_NAME = 'Rate!A2:B100'

    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range=SAMPLE_RANGE_NAME).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
    else:
        for row in values:
            EMPLOYEES[row[0]] = hourly_from_annual(row[1])


def hourly_from_annual(salary):
    return float(salary) / 260 / 8


def display_events(events):
    total_cost = 0

    if not events:
        print('No upcoming events found.')
    for event in events:
        if 'attendees' not in event:
            continue
        duration = calculate_duration(event)
        cost = calculate_cost(event, duration)

        total_cost += cost
        print("%s" % (event['summary']))
        print("\tcost: %d" % cost)
        print("\tduration: %.2f" % duration)

    print("Total cost: %d" % total_cost)


def calculate_cost(event, duration):
    cost = 0
    for a in event['attendees']:
        key = a['email']
        if key == 'trinternal@taskrabbit.com':
            cost = EMPLOYEES[key] * duration * 150;
            break
        if key in EMPLOYEES:
            cost += EMPLOYEES[key] * duration
        else:
            cost += DEFAULT_HOURLY * duration
    return cost


def calculate_duration(event):
    if 'start' not in event or 'dateTime' not in event['start']:
        return 0
        
    start = parser.parse(event['start']['dateTime'])
    end = parser.parse(event['end']['dateTime'])
    return (end - start).total_seconds() / 3600.0


if __name__ == '__main__':
    main()
