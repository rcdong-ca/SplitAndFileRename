import os
import time
import re
import File_Renaming as FR
from ffcuesplitter.cuesplitter import FFCueSplitter

def SubstringAfter(s: str , delim: str):
    return s.partition(delim)[2]

class TrackData:
    Title = ""
    Performer = ""
    Index00 = "" # Hidden track
    Index01 = "" # Start time of the track

    def __init__(self, title, performer, index00="", index01="") -> None:
        self.Title = title
        self.Performer = performer
        self.Index00 = index00
        self.Index01 = index01
        pass
    
    def setTitle(self, title):
        self.Title = title
    
    def setPerformer(self, performer):
        self.Performer = performer
    

class CueFile:

    AlbumTitle = ""
    FileName = ""
    TrackList = []
    srcPath = ""
    Genre = ""
    Date = ""
    Performer = ""


    def __init__(self, path) -> None:
        srcPath = path

        f = open(srcPath, "r", encoding="utf-8", errors="replace")
        
        line = f.readline()
        # parse the infromation
        self.Genre = SubstringAfter(line, "REM GENRE").lstrip().rstrip()
        
        line = f.readline()
        self.Date = SubstringAfter(line, "REM Date").lstrip().rstrip()

        # get the Performer
        line = f.readline()
        self.Performer = re.findall(r'"([^"]*)"', line)[0]

        # get the Title
        line = f.readline()
        self.AlbumTitle = re.findall(r'"([^"]*)"', line)[0]

        # Next line is the filename of the .flac file this .cue file is associated with
        line = f.readline()
        self.FileName= re.findall(r'"([^"]*)"', line)[0]

        # Obtain information of each track
        line = f.readline()
        while("TRACK" in line):
            line = f.readline()
            trackTitle = re.findall(r'"([^"]*)"', line)[0]
            line = f.readline()
            trackPerformer = re.findall(r'"([^"]*)"', line)[0]
            line = f.readline()
            index00 = ""
            index01 = ""
            if ("INDEX 00" in line):
                index00 = SubstringAfter(line, "INDEX 00").lstrip().rstrip()
                line = f.readline()
                if ("INDEX 01" in line):
                    index01 = SubstringAfter(line, "INDEX 01").lstrip().rstrip()  
            elif ("INDEX 01" in line):
                index01 = SubstringAfter(line, "INDEX 01").lstrip().rstrip()
            
            trackData = TrackData(trackTitle, trackPerformer, index00, index01)
            self.TrackList.append(trackData)
            line = f.readline()
        pass


    # create a new .cue file for 
    def writeToCueFile(self, path) -> None:
        f = open(path, "w+")

        f.write(f"REM GENRE {self.Genre}\n")
        f.write(f"REM DATE {self.Date}\n")
        f.write(f"PERFORMER \"{self.Performer}\"\n")
        f.write(f"TITLE \"{self.AlbumTitle}\"\n")
        f.write(f"FILE \"{self.FileName}\" WAVE\n")
        
        trackId = 1
        for track in self.TrackList:
            f.write(f"  TRACK {trackId:02d} AUDIO\n")
            f.write(f"    TITLE \"{track.Title}\"\n")
            f.write(f"    PERFORMER \"{track.Performer}\"\n")
            if (track.Index00 != ""):
                f.write(f"    INDEX 00 {track.Index00}\n")   
            f.write(f"    INDEX 01 {track.Index01}\n")
            trackId += 1
        f.write("\n")

    
    def setTrackData(self, id, title = "", performer = ""):
        id = id - 1
        if title != "":
            self.TrackList[id].setTitle(title)
        
        if performer != "":
            self.TrackList[id].setPerformer(performer)


if __name__ == "__main__":
    cwd = os.getcwd()

    targetDir = os.path.join(cwd,"群星《2024试听小屋系列(115)》[FLAC]")
    targetFile = os.path.join(targetDir,"群星《2024试听小屋系列(115)》[FLAC].cue")

    targetTXTFile = os.path.join(targetDir, "群星《2024试听小屋系列(115)》[FLAC].txt")

    cueCopy = os.path.join(targetDir, "test_COPY.cue")
    
    cueFile = CueFile(targetFile)
    toc = FR.TableOfContents(targetTXTFile)

    # # update cuefile metadata with what was obtained in TableOfContents

    cueFile.AlbumTitle = toc.albumName
    cueFile.FileName = "群星《2024试听小屋系列(115)》[FLAC].flac"
    cueFile.Performer = toc.albumArtist

    # update the track data
    trackLen = len(cueFile.TrackList)
    for i in range(trackLen):
        cueFile.TrackList[i].setTitle(toc.getTitle(i+1))
        cueFile.TrackList[i].setPerformer(toc.getArtist(i+1))

    cueFile.writeToCueFile(cueCopy)

    getData = FFCueSplitter(filename=cueCopy, dry=True)
    # print(getData.audiotracks())
    