from __future__ import print_function
import datetime

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
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    print('Getting the upcoming 10 events')
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                        maxResults=10, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])
    return events


def get_employee_data(service):
    SAMPLE_SPREADSHEET_ID = '1P50eMsvS8alWmd7Xdd3lxbOTp1mu7rg8SkE8NbIkD3U'
    SAMPLE_RANGE_NAME = 'Rate!A2:B9'

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
    return int(salary) / 260 / 8


def display_events(events):
    total_cost = 0

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        if 'attendees' not in event:
            continue
        cost = calculate_cost(event['attendees'])
        total_cost += cost

        print("%s: %d" % (event['summary'], cost))
        
    print("Total cost: %d" % total_cost)


def calculate_cost(attendees):
    cost = 0
    for a in attendees:
        key = a['email']
        if key in EMPLOYEES:
            cost += EMPLOYEES[key]
        else:
            cost += DEFAULT_HOURLY
    return cost


if __name__ == '__main__':
    main()
