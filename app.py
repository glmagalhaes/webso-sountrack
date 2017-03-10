#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import sys
import json
import urllib
import urllib2
from bs4 import BeautifulSoup
from flask_cors import CORS
from flask import Flask
from flask import request
from flask import Response


class Track:
    def __init__(self,title,performers,links=None):
        self.title = title
        #self.composers = composers
        self.performers = performers
        #self.producers = producers
        if(links is None):
            self.links =[]
    
    #def addComposer(self,composer):
        #self.composers += composer
    
    def addPerformer(self,performer):
        self.performers.append(performer)
        
    def addLink(self,link):
        #print(str(self.links))
        self.links.append(link)
    #def addProducers(self,producer):
        #self.producers += producer
    
    def mergePerformers(self):
        return ' and '.join(self.performers)

def parseTitle(trackInfo):
    startIndex = trackInfo.find("\"")
    endIndex = trackInfo.find("\"",startIndex+1)
    title = trackInfo[startIndex+1:endIndex]
    return title.encode(encoding='UTF-8',errors='strict')

def parsePerformers(trackInfo):
    p = []
    trackInfoLow = trackInfo.lower()
    startIndex = endIndex = 0
    #print(trackInfoLow)
    while(startIndex != -1):
        startIndex = trackInfoLow.find("performed by",endIndex)
        if(startIndex != -1):
            startIndex += len("performed by")
        else:
            startIndex = trackInfoLow.find("sung by", endIndex)
            if(startIndex != -1):
                startIndex += len("sung by")
        
        if(startIndex != -1):
            endIndex = trackInfoLow.find("\n",startIndex)
            performersLine = trackInfo[startIndex:endIndex]
            performersLine = performersLine.replace(": ","").replace("'","")
            performersLine = re.sub("[\(\[].*?[\)\]]", "", performersLine)
            majorChunks = performersLine.split(" and ")
            if(len(majorChunks) == 1):
                majorChunks = performersLine.split(" & ")           
            if(len(majorChunks) == 1): #soh tem um performer
                nm = majorChunks[0].strip()
                #print(nm)
                #print(nm.encode(encoding='UTF-8',errors='strict'))
                p.append(nm.encode(encoding='UTF-8',errors='strict'))
            elif (len(majorChunks) == 2 and majorChunks[0].find(",") == -1 ): #tem dois performers
                p.append(majorChunks[0].strip().encode(encoding='UTF-8',errors='strict'))
                p.append(majorChunks[1].strip().encode(encoding='UTF-8',errors='strict'))
            else: #tem tres ou mais performers
                minorChunks = majorChunks[0].split(",")
                for perf in minorChunks:
                    perf = perf.strip()
                    p.append(perf.encode(encoding='UTF-8',errors='strict'))
                p.append(majorChunks[1].strip().encode(encoding='UTF-8',errors='strict'))
                
    
    return p

def searchYoutube(music,track):
    l = []
    textToSearch = music
    query = urllib.quote(textToSearch)
    url = "https://www.youtube.com/results?search_query=" + query
    response = urllib2.urlopen(url)
    html = response.read()
    soup = BeautifulSoup(html, "html5lib")
    for vid in soup.findAll(attrs={'class':'yt-uix-tile-link'},limit=3):   #3 primeiros links
        if not vid['href'].startswith("https://googleads.g.doubleclick.net/"):
            link = 'https://www.youtube.com' + vid['href']
            track.addLink(link.encode(encoding='UTF-8',errors='strict'))
    
    
def parse(data):
    delimiter = "- \""
    num_tracks = data.count(delimiter)
    startIndex = endIndex = cont = 0
    l = []
    for i in range(num_tracks):
        startIndex = data.find(delimiter,endIndex)
        endIndex = data.find(delimiter,startIndex+1)
        if( endIndex != -1 ):
            trackInfo = data[startIndex:endIndex]
        else:
            trackInfo = data[startIndex:]
        trackTitle = parseTitle(trackInfo)
        #print(trackTitle)
        performers = parsePerformers(trackInfo)
        track = Track(trackTitle,performers)
        perfs = track.mergePerformers()
        music = perfs + " " + trackTitle #string pra busca no youtube formato: performerA and performerB musicTitle
        #searchYoutube(music,track)
        l.append(track)
        #print("#######")
        cont += 1
    
    return l    

app = Flask(__name__)
CORS(app)

@app.route('/')
def server_ok():
    return Response('<h1>Server OK<h1>')

@app.route('/request', methods = ['GET', 'OPTIONS'])
def get_tracks():
    try:
        title = request.args['title']
        year = request.args['year']
    except:
        return Response("Year ou Title Não informado")
    formattedMovie = "# %s (%s)" % (title, year)
    formattedMovie = formattedMovie.encode(encoding='UTF-8',errors='strict')
    tracks = []
    soundtracks = open("soundtracks_utf8.list").read()
    
    startIndex = soundtracks.lower().find(formattedMovie.lower())
    endIndex = soundtracks.find("#",startIndex+1)
    movieData = soundtracks[startIndex:endIndex]
    newTracks = parse(movieData)
    tracks = tracks + newTracks

    json_string = json.dumps([ob.__dict__ for ob in tracks])
    return Response(json.dumps([ob.__dict__ for ob in tracks]),  mimetype='application/json',)

reload(sys)  
sys.setdefaultencoding('utf8')
app.run(host=os.getenv('IP', '0.0.0.0'),port=int(os.getenv('PORT', 8080)))
