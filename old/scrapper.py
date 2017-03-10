import re
import sys

class Track:
    def __init__(self,title,performers,composers,producers):
        self.title = title
        self.composers = composers
        self.performers = performers
        self.producers = producers
    
    def addComposer(self,composer):
        self.composers += composer
    
    def addPerformer(self,performer):
        self.performers += performer
        
    def addProducers(self,producer):
        self.producers += producer

def parseTitle(trackInfo):
    startIndex = trackInfo.find("\"")
    endIndex = trackInfo.find("\"",startIndex+1)
    title = trackInfo[startIndex+1:endIndex]
    return title

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
                p.append(majorChunks[0].strip())
            elif (len(majorChunks) == 2 and majorChunks[0].find(",") == -1 ): #tem dois performers
                p.append(majorChunks[0].strip())
                p.append(majorChunks[1].strip())
            else: #tem tres ou mais performers
                minorChunks = majorChunks[0].split(",")
                for perf in minorChunks:
                    perf = perf.strip()
                    p.append(perf)
                p.append(majorChunks[1].strip())
                
    
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
        print(trackTitle)
        performers = parsePerformers(trackInfo)
        print(str(performers))
        composers = "tenho q fazer isso"
        producers = "isso tbm"
        track = Track(trackTitle,performers,composers,producers)
        l.append(track)
        print("#######")
        cont += 1
    
    return l    

def main():
    soundtracks = open("soundtracks_utf8.list").read()
    movies = open("movies.list").read().splitlines()
    tracks = []
    for movie in movies:
        title,year = movie.split("#")
        formattedMovie = "# "+title+" ("+year+")"
        startIndex = soundtracks.find(formattedMovie)
        print(startIndex)
        endIndex = soundtracks.find("#",startIndex+1)
        movieData = soundtracks[startIndex+len(formattedMovie):endIndex]
        print(formattedMovie)
        newTracks = parse(movieData)
        tracks = tracks + newTracks
        print("%%%%%%%%%%%%%%%")

if __name__ == '__main__':
    # x = "This is a sentence. (once a day) [twice a day]"
    # x = re.sub("[\(\[].*?[\)\]]", "", x)
    # print(x)
    # x = "maria e jose"
    # x = x.split(" e ")
    # print(len(x))
    # print(str(x))
    reload(sys)  
    sys.setdefaultencoding('utf8')
    main()