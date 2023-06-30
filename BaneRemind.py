import json
import os
import time

from datetime import datetime
from datetime import timedelta

class Reminder:
    def __init__(self):
        self.text = ""
        self.time = None
        self.user = None


def create_reminder(text, time, user):
    reminder = Reminder()
    reminder.text = text
    reminder.time = time
    reminder.user = user
    return reminder

def get_reminders():
    try:
        with open('reminders/reminders.json', 'r') as f:
            reminders = json.load(f)
            return reminders
    except FileNotFoundError:
        return None
    
def save_reminders(reminders):
    if not os.path.exists('reminders'):
        os.makedirs('reminders')

    with open('reminders/reminders.json', 'w') as f:
        json.dump(reminders, f, indent=2)


def add_reminder(text, time, user):
    reminders = get_reminders()
    reminders.append(create_reminder(text, time, user).__dict__)
    save_reminders(reminders)


def remove_reminder(reminder):
    reminders = get_reminders()
    reminders.remove(reminder)
    save_reminders(reminders)


if __name__ == '__main__':
    add_reminder('test', datetime.now().timestamp(), 'test')

    time.sleep(5)

    reminders = get_reminders()
    for reminder in reminders:
        if reminder['time'] < datetime.now().timestamp():
            print(reminder['text'])
            remove_reminder(reminder)