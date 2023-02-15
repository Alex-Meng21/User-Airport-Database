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
            yield DatabaseOpenedEvent(event.path())


        if isinstance(event, StartContinentSearchEvent): #Continent related events
            try:

                cursor = self.connection.cursor()
                cursor.execute('SELECT * FROM continent WHERE continent_code =? OR name=?',
                               (event.continent_code(),event.name()))
                rows = cursor.fetchall()
                for row in rows:
                    if (row[1] == event.continent_code() and row[2] == event.name()) or (row[1] == event.continent_code() and row[2] == 'None') or (row[2] == event.name() and row[1] == 'None'):
                        #right now doesn't yield anything if only code or name is entered alone
                        yield ContinentSearchResultEvent(
                            Continent(row[0], row[1], row[2]))
                        cursor.close()
            except sqlite3.Error:
                yield DatabaseOpenFailedEvent('File is not a database')
            except Exception:
                yield ErrorEvent('Error searching continent. Continent may not exis')

        if isinstance(event, LoadContinentEvent):
            try:
                cursor2 = self.connection.cursor()
                cursor2.execute('SELECT * FROM continent WHERE continent_id = ?',
                                (event.continent_id(),))
                row = cursor2.fetchone()
                yield ContinentLoadedEvent(Continent(row[0],row[1],row[2]))
                cursor2.close()

            except sqlite3.Error:
                yield ErrorEvent('Error loading continent')

        if isinstance(event, SaveNewContinentEvent):
            try:
                cursor3 = self.connection.cursor()
                cursor3.execute(
                    'INSERT INTO continent(continent_code, name) VALUES (?,?);',
                    (event.continent().continent_code, event.continent().name))
                yield ContinentSavedEvent(Continent(event.continent().continent_id, event.continent().continent_code, event.continent().name))
                self.connection.commit()
                cursor3.close()
            except sqlite3.Error:
                yield SaveContinentFailedEvent(f'Continent failed to save {event.continent().continent_code} is already in the database' )

        if isinstance(event, SaveContinentEvent):

            try:
                cursor4 = self.connection.cursor()
                cursor4.execute('UPDATE continent SET (continent_code = ?, name = ?)'
                    )
            except:
                pass


        if isinstance(event, CloseDatabaseEvent):
            if self.connection is not None:
                self.connection.close()
                self.connection = None
            yield DatabaseClosedEvent()

        if isinstance(event, QuitInitiatedEvent):
            yield EndApplicationEvent()
