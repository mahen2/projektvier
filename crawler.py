#!/usr/bin/python
# -*- coding: utf-8 -*-
# Quelle website-import:
# http://answers.oreilly.com/topic/1088-how-to-build-a-simple-web-crawler/

import urllib2
import re
import csv
from bs4 import BeautifulSoup


def generate_1live_url(day, hour, minute):
    """
    Simply generate a valid 1live URL
    for the given day (as a number between 1 and 360), hour and minute

    """
    url = "http://www.einslive.de/musik/playlists/index."\
        "jsp?wday=%i&hour=%i&minute=%i"
    return url % (day, hour, minute)


def fetch_1live_data(_1live_website_url):
    """ Fetch data of the songs for the specific 1live-URL
    and return it as a list

    """
    c = urllib2.urlopen(_1live_website_url)
    contents = c.read()
    soup = BeautifulSoup(contents)
    # Tabelle mit den Songs holen über Klassennamen:
    threetracks = BeautifulSoup(soup.select(".wsPlaylistsEL")[0].prettify())
    # Datum steht manchmal in den Einträgen, manchmal nicht (komisch!!),
    # deshalb muss es aus der Tabelle gelesen und später in die Songtabelle
    # eingefügt werden:
    table = threetracks.table
    # enthält z.B.: Die am Samstag, 11. Januar 2014, 14:20 Uhr gespielten Titel
    summary = table['summary']
    # nur das Datum rausholen:
    date = summary.split(', ')[1]

    # es werden drei Songs angezeigt, finde die entsprechenden Tabellenzeilen:
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
    return songs


def dic_to_csv(dic, filename):
    """ Write a dictionary with lists as values to a csv-file """
    with open(filename, 'wb') as file_:
        writer = csv.writer(file_)
        for key, value in dic.items():
            writer.writerow([key] + value)

if __name__ == "__main__":
    playlist_dic = {}
    filename = "playlist.csv"
    # nested for loop to fetch all songs for the last year
    for day in range(1, 361):
        for hour in range(1, 24):
            print hour
            for minute in range(1, 61):
                url = generate_1live_url(day, hour, minute)
                songs = fetch_1live_data(url)
                for song in songs:
                    playlist_dic[song[2]] = [song[0], song[1]]
            # TODO: Save at appropriate time intervals
            dic_to_csv(playlist_dic, filename)
    # CSV ausgeben:
    cr = csv.reader(open(filename, "rb"))
    for row in cr:
        print row
