#!/usr/bin/python
# -*- coding: utf-8 -*-
# Quelle website-import: http://answers.oreilly.com/topic/1088-how-to-build-a-simple-web-crawler/
import urllib2, re, csv
from bs4 import BeautifulSoup
website = "http://www.einslive.de/musik/playlists/index.jsp?wday=0&hour=14&minute=20"
c=urllib2.urlopen(website)
contents=c.read()
soup = BeautifulSoup(contents)
threetracks = BeautifulSoup(soup.select(".wsPlaylistsEL")[0].prettify())
played_songs = threetracks.find_all("tr", { "class" : re.compile(r"^(wsEven|wsOdd)$") })
songs = []
for song in played_songs:
    soup_song = BeautifulSoup(str(song.encode('utf-8')))
    artist = soup_song.select('td[headers="pltab1artist"]')[0].string.strip().encode('utf-8')
    title = soup_song.select('td[headers="pltab1title"]')[0].string.strip().encode('utf-8')
    time = soup_song.select('td[headers="pltab1time"]')[0].string.strip().encode('utf-8')
    songs.append([artist,title,time])


with open('playlist.csv', 'a') as f:
	writer = csv.writer(f)
	writer.writerows(songs)

print songs

    