import pyrebase
from datetime import datetime
import time


class VoteStorage:
    def __init__(self):
        config = {
            "apiKey": "AIzaSyBggIjrLtVh_enNEbkf6neRjBkAeFGFo8k",
            "authDomain": "footbot-b964f.firebaseapp.com",
            "databaseURL": "https://footbot-b964f.firebaseio.com",
            "projectId": "footbot-b964f",
            "storageBucket": "footbot-b964f.appspot.com",
            "messagingSenderId": "897990637274"
        }
        self.firebase = pyrebase.initialize_app(config)
        self.db = self.firebase.database()

    def next_event(self, date):
        self.db.child('next_event').set(date.isoformat())

    def get_next_event(self):
        iso_date = self.db.child('next_event').get().val()
        return datetime.strptime(iso_date, "%Y-%m-%dT%H:%M:%S.%f")

    def add(self, person):
        next_event = self._next_event()
        self.db.child("players").child(next_event).child(person["id"]).set(person)

    def all(self):
        next_event = self._next_event()
        return self.db.child("players").child(next_event).get().val()

    def remove(self, person):
        next_event = self._next_event()
        self.db.child("players").child(next_event).child(person["id"]).remove()

    def _next_event(self):
        next_event = self.get_next_event()
        next_event = int(time.mktime(next_event.timetuple()))
        return next_event


