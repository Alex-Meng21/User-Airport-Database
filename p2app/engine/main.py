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
from p2app.events.countries import Country
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
            self.connection.execute('PRAGMA foreign_keys = ON')
            yield DatabaseOpenedEvent(event.path())

        # Continent related events
        if isinstance(event, StartContinentSearchEvent):
            try:

                cursor = self.connection.cursor()
                cursor.execute('SELECT * FROM continent WHERE (continent_code =? AND name=?) OR continent_code =? OR name =?',
                               (event.continent_code(),event.name(),event.continent_code(),event.name()))
                rows = cursor.fetchall()
                for row in rows:
                    if (row[1] == event.continent_code() and event.name() == None) or (row[2] == event.name() and event.continent_code() == None) or (row[1] == event.continent_code() and row[2] == event.name()):

                        yield ContinentSearchResultEvent(
                            Continent(row[0], row[1], row[2]))
                cursor.close()

            except sqlite3.Error:
                yield DatabaseOpenFailedEvent('File is not a database')
            except:
                yield ErrorEvent('Error searching continent. Continent may not exist')

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
                if (event.continent().continent_code != '') and (event.continent().name != ''):

                    cursor3.execute(
                        'INSERT INTO continent(continent_code, name) VALUES (?,?);',
                        (event.continent().continent_code, event.continent().name))
                    yield ContinentSavedEvent(Continent(event.continent().continent_id, event.continent().continent_code, event.continent().name))
                    self.connection.commit()
                    cursor3.close()
                else:
                    yield SaveContinentFailedEvent('Empty code and/or name')
            except sqlite3.Error:
                yield SaveContinentFailedEvent(f'Continent failed to save {event.continent().continent_code} is already in the database' )

        if isinstance(event, SaveContinentEvent):

            try:
                cursor4 = self.connection.cursor()
                if (event.continent().continent_code != '') and (event.continent().name != ''):
                    cursor4.execute(
                        'UPDATE continent SET continent_code=?, name=? WHERE continent_id=?;',
                        (event.continent().continent_code, event.continent().name, event.continent().continent_id))
                    yield ContinentSavedEvent(Continent(event.continent().continent_id, event.continent().continent_code, event.continent().name))
                    self.connection.commit()
                    cursor4.close()
                else:
                    yield SaveContinentFailedEvent('Empty code and/or name')
            except sqlite3.Error:
                yield SaveContinentFailedEvent(f'Continent failed to save {event.continent().continent_code} is already in the database' )


        if isinstance(event, CloseDatabaseEvent):
            if self.connection is not None:
                self.connection.close()
                self.connection = None
            yield DatabaseClosedEvent()

        if isinstance(event, QuitInitiatedEvent):
            yield EndApplicationEvent()

#country related events

        if isinstance(event, StartCountrySearchEvent):
            try:
                cursor5 = self.connection.cursor()
                cursor5.execute('SELECT * FROM country WHERE (country_code =? AND name=?) OR country_code =? OR name =?',
                               (event.country_code(),event.name(),event.country_code(),event.name()))
                rows = cursor5.fetchall()
                for row in rows:
                    if (row[1] == event.country_code() and event.name() == None) or (
                            row[2] == event.name() and event.country_code() == None) or (
                            row[1] == event.country_code() and row[2] == event.name()):
                        yield CountrySearchResultEvent(
                            Country(row[0], row[1], row[2],row[3],row[4],row[5]))
                cursor5.close()
            except sqlite3.Error:
                yield DatabaseOpenFailedEvent('File is not a database')
            except:
                yield ErrorEvent('Error searching continent. Continent may not exist')

        if isinstance(event, LoadCountryEvent):

            try:
                cursor6 = self.connection.cursor()
                cursor6.execute('SELECT * FROM country WHERE country_id = ?',
                                (event.country_id(),))
                row = cursor6.fetchone()
                yield CountryLoadedEvent(Country(row[0],row[1], row[2],row[3],row[4],row[5]))
                cursor6.close()

            except sqlite3.Error:
                yield ErrorEvent('Error loading continent')

        if isinstance(event, SaveNewCountryEvent):

            try:

                cursor7 = self.connection.cursor()
                if (event.country().country_code != '') and (event.country().name != '') and (event.country().wikipedia_link != '') and (event.country().continent_id != 0):

                    cursor7.execute(
                        'INSERT INTO country(country_code, name, continent_id, wikipedia_link, keywords) VALUES (?,?,?,?,?);',
                        (event.country().country_code, event.country().name, event.country().continent_id, event.country().wikipedia_link, event.country().keywords))
                    yield CountrySavedEvent(
                        Country(event.country().country_id, event.country().country_code, event.country().name,
                                  event.country().continent_id, event.country().wikipedia_link, event.country().keywords))
                    self.connection.commit()
                    cursor7.close()
                if event.country().continent_id == 0:
                    yield SaveCountryFailedEvent('Continent ID cannot be 0!')
                else:
                    yield SaveCountryFailedEvent('Empty code, name, continent id, or wikipedia link')
            except sqlite3.Error:
                yield SaveCountryFailedEvent(
                    f'Country failed to save! {event.country().country_code} is already in the database')

