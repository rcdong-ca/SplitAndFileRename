import os
import time
import re
import File_Renaming as FR
from ffcuesplitter.cuesplitter import FFCueSplitter


class TrackData:
    Title = ""
    Performer = ""
    Index00 = None # Hidden track
    Index01 = None # Start time of the track

    def __init__(self, title, performer, index00=None, index01=None) -> None:
        self.Title = title
        self.Performer = performer
        self.Index00 = index00
        self.Index01 = index01
        pass

def SubstringAfter(s: str , delim: str):
    return s.partition(delim)[2]


class CueFile:

    AlbumTitle = ""
    FileName = ""
    TrackList = [TrackData]
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

            print(f"trackTitle: {trackTitle}\ntrackPerformer: {trackPerformer}")
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
            f.write(f"\tTRACK {trackId:02d} AUDIO\n")
            f.write(f"\t\tTITLE \"{track.Title}\"\n")
            f.write(f"\t\tPERFORMER \"{track.Performer}\"\n")
            if (track.Index00 != None):
                f.write(f"\t\tINDEX 00 {track.Index00}\n")   
            f.write(f"\t\tINDEX 01 {track.Index01}\n")
        f.write("\n")
    
    
    


if __name__ == "__main__":
    cwd = os.getcwd()
    testDir = os.path.join(cwd, "test")
    cuePath = ""
    for file in os.listdir(testDir):
        cuePath = os.path.join(testDir, file)
        break
    
    cf = CueFile(cuePath)

    
    # s = ""
    # with open(cuePath, encoding='utf-8', errors='replace') as f:
    #    for line in f:
    #        print(line)

    # getData = FFCueSplitter(filename=cuePath, dry=True)
    