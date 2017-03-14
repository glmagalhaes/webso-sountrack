#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import sys
import json
import urllib
import urllib2
from urlparse import urlparse
from bs4 import BeautifulSoup
from flask_cors import CORS
from flask import Flask
from flask import request
from flask import Response


#Classe que define cada música
class Track:
    def __init__(self,title,performers,link=None):
        self.title = title
        self.performers = performers
    
    def addPerformer(self,performer):
        self.performers.append(performer)
        
    def addLink(self,link):
        self.link = link
    def getLink(self):
        return self.link
    
    def mergePerformers(self):
        return ' and '.join(self.performers)

def searchCache(music,track):
    cache = open("youtube.cache").read()
    delimiter = music+" # "
    startIndex = cache.find(delimiter)
    if(startIndex==-1):
        return False
    else:
        endIndex = cache.find("|",startIndex+1)
        link = cache[startIndex+len(delimiter):endIndex]
        track.addLink(link)
        return True

def fillCache(music,link):
    with open("youtube.cache", "a") as myCache:
        myCache.write(music+" # "+link+"|\n")

def searchYoutube(music,track):
    l = []
    textToSearch = music
    query = urllib.quote(textToSearch)
    url = "https://www.youtube.com/results?search_query=" + query
    response = urllib2.urlopen(url)
    html = response.read()
    soup = BeautifulSoup(html, "html5lib")
    for vid in soup.findAll(attrs={'class':'yt-uix-tile-link'},limit=1):   #3 primeiros links
        if not vid['href'].startswith("https://googleads.g.doubleclick.net/"):
            link = 'https://www.youtube.com' + vid['href']
            track.addLink(link.encode(encoding='UTF-8',errors='strict'))

def searchYoutube2(music,track):  #essa busca parece ser mais rapida.....
    query_string = urllib.urlencode({"search_query" : music})
    html_content = urllib.urlopen("http://www.youtube.com/results?" + query_string)
    search_results = re.findall(r'href=\"\/watch\?v=(.{11})', html_content.read().decode())
    track.addLink("http://www.youtube.com/watch?v=" + search_results[0])

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
            else:
                startIndex = trackInfoLow.find("music by", endIndex)
                if(startIndex != -1):
                    startIndex += len("music by")
                else:
                    startIndex = trackInfoLow.find("written by", endIndex)
                    if(startIndex != -1):
                        startIndex += len("written by")
                    else:
                        startIndex = trackInfoLow.find("composed by", endIndex)
                        if(startIndex != -1):
                            startIndex += len("composed by")
                        
        
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
        if(not searchCache(music,track)):    #caso não queira link do youtube, comentar daqui ate linha 144
            searchYoutube2(music,track)
            fillCache(music,track.getLink())
        l.append(track)
        #print("#######")
        cont += 1
    
    return l    

app = Flask(__name__)

# Para poder ser acessado por serviços externos
CORS(app)

# URL de teste, caso consiga ver essa mensagem o Flask iniciou normalmente
@app.route('/')
def server_ok():
    return Response('<h1>Server OK<h1>')

# Recebe as informações de filme e ano e procura pelo filme
@app.route('/request', methods = ['GET', 'OPTIONS'])
def get_tracks():
    try:
        title = request.args['title']
        year = request.args['year']
    except:
        return Response("Year ou Title Não informado")
    title = title.strip()
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

#Para Rodar em uma maquina local troque o ip por 127.0.0.1
app.run(host=os.getenv('IP', '0.0.0.0'),port=int(os.getenv('PORT', 8080)))
