#!/usr/bin/python
# -*- coding: utf-8 -*-
# Quelle website-import: http://answers.oreilly.com/topic/1088-how-to-build-a-simple-web-crawler/

import urllib2, re, csv
from bs4 import BeautifulSoup
website = "http://www.einslive.de/musik/playlists/index.jsp?wday=50&hour=14&minute=20"
filename = "playlist.csv"

c=urllib2.urlopen(website)
contents=c.read()
soup = BeautifulSoup(contents)
# Tabelle mit den Songs holen über Klassennamen:
threetracks = BeautifulSoup(soup.select(".wsPlaylistsEL")[0].prettify())

# Datum steht manchmal in den Einträgen, manchmal nicht (komisch!!), deshalb muss es aus der Tabelle gelesen und später in die Songtabelle eingefügt werden:
table = threetracks.table
summary = table['summary'] # enthält z.B.: Die am Samstag, 11. Januar 2014, 14:20 Uhr gespielten Titel
# nur das Datum rausholen:
date = summary.split(', ')[1]


# es werden drei Songs angezeigt, finde die entsprechenden Tabellenzeilen:
played_songs = threetracks.find_all("tr", { "class" : re.compile(r"^(wsEven|wsOdd)$") })

songs = []
for song in played_songs:
    soup_song = BeautifulSoup(str(song.encode('utf-8')))
    artist = soup_song.select('td[headers="pltab1artist"]')[0].string.strip().encode('utf-8')
    title = soup_song.select('td[headers="pltab1title"]')[0].string.strip().encode('utf-8')
    time = date + ", " + soup_song.select('td[headers="pltab1time"]')[0].string.strip().encode('utf-8')
    # jeden Song in Liste schreiben:
    songs.append([artist,title,time])

# erweitere die CSV mit den Songs:
with open(filename, 'a') as f:
	writer = csv.writer(f)
	writer.writerows(songs)

# CSV ausgeben:
cr = csv.reader(open(filename,"rb"))
for row in cr:
    print row    
