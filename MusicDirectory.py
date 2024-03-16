import os
import re
import sys
import io
import math
import utilities as util
from mutagen.flac import FLAC
from mutagen.flac import Picture
from PIL import Image



"""
Class that represents the target directory. It will hold all paths of important files we will need
to Perform things like cue split, file renames, etc.
"""
class MusicDir:
    dirName = None              # name of directory
    dirPath = None              # the directory path
    coverPath = None            # the path of the cover used for the album
    majorFlacPath = None        # path of flac file that will be split
    cuePath = None              # path of the cue file
    tableOfContentsPath = None      # path of the associated text file that contains track artist and name information
    flacDict = {}               # tracks split from major flac

    def __init__(self, path, dirName = "") -> None:
        self.dirPath = path
        self.dirName = dirName
        # find the desired text that contains table of contents
        try:
            
            # assumption that there is only one txt and one cue file
            for file in os.listdir(path):
                if file.endswith(".txt") and "~$" not in file:
                    self.tableOfContentsPath = os.path.join(path, file) 
                elif file.endswith(".cue"):
                    self.cuePath = os.path.join(path, file)

            assert self.cuePath is not None or self.tableOfContentsPath is not None, ".cue and .txt file was not detected. This file must exist"

            # create the flacList if it is split
            for file in os.listdir(path):
                if file.endswith(".flac"):
                    flacSrcPath = os.path.join(path, file)

                    # get the already split flac files
                    id = util.getFirstNumSeqFromStr(file)
                    if id != -1:
                        self.flacDict[id] = FLACDataDef(flacSrcPath)
                    else:
                        #get the major flac file path
                        self.majorFlacPath = flacSrcPath

                # check if the cover is within the current directory
                elif (file.endswith(".jpg") is True or file.endswith(".png")) and (file.lower()=="cover.jpg" or file.lower() == "cover.png"):
                    self.coverPath = os.path.join(self.dirPath, file)

            # check if the cover is in subdirectory
            if (self.coverPath is None):
                for root, dirs, files in os.walk(self.dirPath):
                    for file in files:
                        if (file.endswith(".jpg") is True or file.endswith(".png")) and (file.lower()=="cover.jpg" or file.lower() == "cover.png"):
                            self.coverPath = os.path.join(root, file)
                            # print(self.coverPath)
                            return

        except Exception as e:
            raise ValueError("Music Dir init fail:", e)

"""
Representation of the .txt file that contains utf-8 metadata that many not be viewable in the .cue file
This class will be primarily used fill in the missing information of .flac file and .cue file
"""
class TableOfContents:

    filePath = None
    artist = {}
    title = {}
    fileName = {}
    albumName = ""
    albumArtist = ""

    def __init__(self, path) -> None:
        self.filePath = path
        # parse the txt file for album fileName and name. These are sequentially stored
        txtFile = open(self.filePath, "r", encoding="utf-8")
        for line in txtFile:
            if "专辑名称"in line:
                l = line.split(":")
                self.albumName = l[1].rstrip("\n")
            elif "专辑艺人" in line:
                l = line.split(":")
                self.albumArtist = l[1].rstrip("\n")
                break

        # get the song name
        for line in txtFile:
            l = line.split(".")
            if (l[0].isnumeric() == True):
                id = int(l[0])
                fileName = line.rstrip("\n") + ".flac"
                self.fileName[id] = fileName
                artistTitle = line[line.find(".")+1:].rstrip("\n")
                artist = ""
                title = ""
                words = re.split(r'-+', artistTitle)
                if (len(words) > 1):
                    artist = words[0]
                    title = words[1]
                else:
                    words = re.split(r'–+', artistTitle)
                    if (len(words) > 1):
                        artist = words[0]
                        title = words[1]

                self.artist[id] = artist
                self.title[id] = title
    
    def getTitle(self, id):
        return self.title.get(id, "")
    
    def getFileName(self, id):
        return self.fileName.get(id, "")
    
    def getArtist(self, id):
        return self.artist.get(id, "")

    def getAlbumName(self):
        return self.albumName

    def getAlbumArtist(self):
        return self.albumArtist

class FLACDataDef:
    srcPath = None
    coverPath = None
    title = ""
    artist=""
    albumArtist=""
    albumName=""
    pictSize = 500000 # 500,000 bytes will be the max picture size. It will be compressed otherwise

    def __init__(self, path, coverPath = None) -> None:
        self.srcPath = path
        self.coverPath = coverPath
    
    def setPictSize(self, pictSize):
        if (pictSize < 1):
            raise ValueError(f"{pictSize} is not an acceptable picture size")
        self.pictSize = pictSize

    def updateMetaData(self):
        audioFile = FLAC(self.srcPath)

        if self.title != "":
            audioFile["TITLE"] = self.title
        if self.artist != "":
            audioFile["ARTIST"] = self.artist
        if self.albumArtist != "":
            audioFile["ALBUMARTIST"] = self.albumArtist
        if self.albumName != "":
            audioFile["ALBUM"] = self.albumName

        if self.coverPath is not None:
            buffer, width, height = self.JPEGSaveWithTargetSize(self.coverPath, self.pictSize)
            assert buffer is not None
            p = Picture()
            p.data = buffer.getvalue()
            p.height = height
            p.width = width
            p.depth = 16
            p.mime = u"image/jpg"
            audioFile.add_picture(p)
        
        audioFile.save()

    def renameFile(self, filePath):
        """
        renames the flac file. filePath must have the complete path of the new file
        """
        if ".flac" not in filePath:
            return
        os.rename(src=self.srcPath, dst=filePath)
        self.srcPath = filePath

    def JPEGSaveWithTargetSize(self, filePath, target=500000):
        """Save the image as JPEG with the given name at best quality that makes less than "target" bytes.
        Thanks to March Setchell for provided answer
        https://stackoverflow.com/questions/52259476/how-to-reduce-a-jpeg-size-to-a-desired-size

        Input:
            filePath (str): full path of picture file
            target (int): desired size of file in bytes
        
        Return:
            buffer
        """
        myImage = Image.open(filePath)
        # Min and Max quality
        Qmin, Qmax = 25, 96
        # Highest acceptable quality found
        Qacc = -1
        while Qmin <= Qmax:
            m = math.floor((Qmin + Qmax) / 2)

            # Encode into memory and get size
            buffer = io.BytesIO()
            myImage.save(buffer, format="JPEG", quality=m)
            s = buffer.getbuffer().nbytes

            if s <= target:
                Qacc = m
                Qmin = m + 1
            elif s > target:
                Qmax = m - 1

        # Write to disk at the defined quality
        if Qacc > -1:
            buffer = io.BytesIO()
            width, height = myImage.size
            myImage.save(buffer, format="JPEG", quality=Qacc)
            return buffer, width, height
            
        else:
            print("ERROR: No acceptble quality factor found", file=sys.stderr)
            return None, 0, 0


"""Following classes will used for cue splitting"""

"""
Represents necessary track information found in the .cue file
"""
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
    
"""
Represents the .cue file, as it will hold the required information to split the target .flac file
into its tracks
"""
class CueFile:
    AlbumTitle = ""
    FileName = ""
    TrackList = []      # holds TrackData, which carries the metadata of each track
    srcPath = ""
    Genre = ""
    Date = ""
    Performer = ""


    def __init__(self, path) -> None:
        srcPath = path
        f = open(srcPath, "r", encoding="utf-8", errors="replace")
        line = f.readline()

        # parse the cue file for metadata
        self.Genre = util.SubstringAfter(line, "REM GENRE").lstrip().rstrip()
        line = f.readline()
        self.Date = util.SubstringAfter(line, "REM DATE").lstrip().rstrip()

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
                index00 = util.SubstringAfter(line, "INDEX 00").lstrip().rstrip()
                line = f.readline()
                if ("INDEX 01" in line):
                    index01 = util.SubstringAfter(line, "INDEX 01").lstrip().rstrip()  
            elif ("INDEX 01" in line):
                index01 = util.SubstringAfter(line, "INDEX 01").lstrip().rstrip()
            
            trackData = TrackData(trackTitle, trackPerformer, index00, index01)
            self.TrackList.append(trackData)
            line = f.readline()

    def writeToCueFile(self, path) -> None:
        """
        Write CueFile data to file pointed by path
        Input:
            path (str): target .cue file path
        """
        f = open(path, "w+", encoding="utf-8")

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
        """
        Set track information
        Input:
            id (int): track id we want to change
            title (str): new title we want to set for track
            performer(str): new performer we want to set for track
        """
        id = id - 1
        if title != "":
            self.TrackList[id].setTitle(title)
        
        if performer != "":
            self.TrackList[id].setPerformer(performer)
