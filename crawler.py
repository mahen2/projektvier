#!/usr/bin/python
# -*- coding: utf-8 -*-
# Quelle website-import:
# http://answers.oreilly.com/topic/1088-how-to-build-a-simple-web-crawler/

import urllib2
import re
import csv
import collections
from datetime import datetime
import locale
from bs4 import BeautifulSoup


def generate_1live_url(day, hour, minute):
    """
    Simply generate a valid 1live URL
    for the given day (as a number between 1 and 360), hour and minute

    """
    url = "http://www.einslive.de/musik/playlists/index."\
        "jsp?wday=%s&hour=%s&minute=%s"
    return url % (day, hour, minute)


def fetch_1live_data(_1live_website_url):
    """ Fetch data of the songs for the specific 1live-URL
    and return it as a list

    """
    try:
        c = urllib2.urlopen(_1live_website_url)
        contents = c.read()
        soup = BeautifulSoup(contents)
        # return none if there are no titles at the specific time for some
        # reason
        if not "Es konnten keine Titel gefunden werden." in soup:
            # Tabelle mit den Songs holen über Klassennamen:
            threetracks = BeautifulSoup(
                soup.select(".wsPlaylistsEL")[0].prettify())
            # Datum steht manchmal in den Einträgen, manchmal nicht (komisch!!),
            # deshalb muss es aus der Tabelle gelesen und später in die Songtabelle
            # eingefügt werden:
            table = threetracks.table
            # enthält z.B.: Die am Samstag, 11. Januar 2014, 14:20 Uhr gespielten
            # Titel
            summary = table['summary']
            # nur das Datum rausholen:
            date = summary.split(', ')[1]
            # es werden drei Songs angezeigt, finde die entsprechenden
            # Tabellenzeilen:
            played_songs = threetracks.find_all(
                "tr", {"class": re.compile(r"^(wsEven|wsOdd)$")})
            songs = []
            for song in played_songs:
                artist = song.select('td[headers="pltab1artist"]')[
                    0].string.strip().encode('utf-8')
                title = song.select('td[headers="pltab1title"]')[
                    0].string.strip().encode('utf-8')
                time = (date + ", " + song.select('td[headers="pltab1time"]')[0]
                        .string.strip()).encode('utf-8')
                # jeden Song in Liste schreiben:
                songs.append([artist, title, time])
        else:
            return None
    # Return none on IndexError (server gives an invalid response)
    except IndexError:
        return None
    else:
        return songs


def import_1live_data(filename):
    """
    Import the fetched 1live data from a csv file to an OrderedDict sorted by
    date and time

    """
    # Set locale to de_DE to read the 1live data correctly
    locale.setlocale(locale.LC_ALL, "de_DE")
    temp_dic = {}
    # Create a list for the sorted 1live data
    # playlist = []
    # Create a OrderedDict for the sorted 1live date
    playlist_dic = collections.OrderedDict()
    # Read the file
    cr = csv.reader(open(filename, "rb"))
    for song in cr:
        # Split date and time
        split_str = song[0].split(" ")

        for elem in split_str:
            # Search for the time since the input is not consistent
            if ":" in elem:
                day = split_str[0].replace(".", "")
                # Append a zero if the date is smaller then 10
                day = day if int(day) > 9 else "0" + day
                month = split_str[1]
                year = split_str[2].replace(",", "")
                # Create a sortable datetime object
                dt = datetime.strptime("%s%s%s%s" %
                                      (day, month, year, " " + elem),
                                       "%d%B%Y %H:%M:%S")
        # Save in a temporary dictionary
        temp_dic[dt] = [song[1], song[2]]
    # Sort the temporary dictionary and append each item to the OrderedDict
    for key, value in sorted(temp_dic.iteritems(), key=lambda k: k[0]):
        # playlist.append([key, value])
        playlist_dic[key] = value
    # Set locale back to default settings
    locale.setlocale(locale.LC_ALL, "")
    # Return the OrderedDict
    return playlist_dic
    # Return the nested List
    # return playlist


def dic_to_csv(dic, filename):
    """ Write a dictionary with lists as values to a csv-file """
    with open(filename, 'wb') as file_:
        writer = csv.writer(file_)
        for key, value in dic.items():
            writer.writerow([key] + value)

if __name__ == "__main__":
    filename = "playlist.csv"
    # Fetch the 1live radio data ###
    # playlist_dic = {}
    # nested for-loop to fetch all songs for the last year
    # for day in range(0, 361):
    #     for hour in range(1, 24):
    # Add a zero to the hour if it is smaller than 10 (the 1live-server
    # requires this)
    #         if hour < 10:
    #             hour = "0%i" % hour
    #         for minute in range(1, 61, 3):
    # Add a zero if the minute is smaller than 10 (the 1live-server
    # requires this)
    #             if minute < 10:
    #                 minute = "0%i" % minute
    #             url = generate_1live_url(day, hour, minute)
    #             songs = fetch_1live_data(url)
    # Sometimes there are no songs for a specific time
    #             if songs:
    #                 for song in songs:
    #                     playlist_dic[song[2]] = [song[0], song[1]]
    #         dic_to_csv(playlist_dic, filename)

    # Import the fetched data ###
    einslive_data = import_1live_data(filename)

    # Time can be received like this
    print einslive_data.keys()[0].strftime("%d.%B.%Y %H:%M Uhr")

    # Example for all data of a song
    locale.setlocale(locale.LC_ALL, "de_DE")
    print "Datum: ", einslive_data.keys()[0].strftime("%d.%B.%Y %H:%M Uhr")
    print "Interpret: ", einslive_data[einslive_data.keys()[0]][0]
    print "Titel: ", einslive_data[einslive_data.keys()[0]][1]
    locale.setlocale(locale.LC_ALL, "")
