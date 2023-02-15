# p2app/engine/main.py
#
# ICS 33 Winter 2023
# Project 2: Learning to Fly
#
# An object that represents the engine of the application.
#
# This is the outermost layer of the part of the program that you'll need to build,
# which means that YOU WILL DEFINITELY NEED TO MAKE CHANGES TO THIS FILE.


import sqlite3
from p2app.events import*
from p2app.events.continents import Continent
class Engine:
    """An object that represents the application's engine, whose main role is to
    process events sent to it by the user interface, then generate events that are
    sent back to the user interface in response, allowing the user interface to be
    unaware of any details of how the engine is implemented.
    """

    def __init__(self):
        """Initializes the engine"""
        self.connection = None


    def process_event(self, event):
        """A generator function that processes one event sent from the user interface,
        yielding zero or more events in response."""

        # This is a way to write a generator function that always yields zero values.
        # You'll want to remove this and replace it with your own code, once you start
        # writing your engine, but this at least allows the program to run.



        if isinstance(event, OpenDatabaseEvent):

            self.connection = sqlite3.connect(event.path())
            cursor = self.connection.cursor()
            yield DatabaseOpenedEvent(event.path())


        if isinstance(event, StartContinentSearchEvent):
            try:

                cursor = self.connection.cursor()
                cursor.execute('SELECT continent_id FROM continent WHERE continent_code =?',
                               (event.continent_code(),))
                row = cursor.fetchone()
                if row is not None:
                    yield ContinentSearchResultEvent(
                        Continent(row, event.continent_code(), event.name()))
            except sqlite3.Error:
                yield DatabaseOpenFailedEvent('Failed to open database!')

        if isinstance(event, CloseDatabaseEvent):
            if self.connection is not None:
                self.connection.close()
                self.connection = None
            yield DatabaseClosedEvent()

        if isinstance(event, QuitInitiatedEvent):
            yield EndApplicationEvent()
