import os
import re
import sys
import io
import math
import time
import json

from pathlib import Path
from mutagen.flac import FLAC
from mutagen.flac import Picture
from PIL import Image


"""
meta data of flac files are located in  .txt file as cuesheet uses unknown encoding
Parse the file
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
            # must start with numeral
            if l[0].isnumeric() is True and len(l) > 1:
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
                    words.re.split(r'–+', artistTitle)
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
    pictSize = 500000 # 200,000 bytes will be the max picture size. It will be compressed otherwise

    def __init__(self, path) -> None:
        self.srcPath = path
        pass
    def setAlbumArtist(self, name):
        if name == "":
            return
        self.albumArtist = name
    
    def setAlbumName(self, name):
        if name == "":
            return
        self.albumName = name
        
    def setArtist(self, name):
        if name == "":
            return
        self.artist = name
    
    def setSrcPath(self, path):
        if path is None:
            return
        self.srcPath = path
    
    def setTitle(self, title):
        if title == "":
            return
        self.title = title

    def setCover(self, coverPath):
        if coverPath is None:
            return
        self.coverPath = coverPath

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
            if (os.path.getsize(self.coverPath) > self.pictSize):
                # print("image original size: ",os.path.getsize(self.coverPath))
                self.JPEGSaveWithTargetSize(self.coverPath, self.pictSize)
                # print("image after compress: ", os.path.getsize(self.coverPath))

            if (os.path.getsize(self.coverPath) <= self.pictSize):
                p = Picture()
                with open(self.coverPath, "rb") as f:
                    p.data = f.read()

                # check if data is within acceptable size
                audioFile.add_picture(p)
        audioFile.save()

    def JPEGSaveWithTargetSize(self, filename, target):
        """Save the image as JPEG with the given name at best quality that makes less than "target" bytes.
        Thanks to March Setchell for provided answer
        https://stackoverflow.com/questions/52259476/how-to-reduce-a-jpeg-size-to-a-desired-size
        """
        myImage = Image.open(filename)
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
            myImage.save(buffer, format="JPEG", quality=Qacc)
            return myImage.open(buffer)
        else:
            print("ERROR: No acceptble quality factor found", file=sys.stderr)
            


class MusicDir:
    dirPath = None
    coverPath = None
    tableOfContents = None
    flacDict = {}

    def __init__(self, path) -> None:
        self.dirPath = path

        # check if it is a valid path

        # find the desired text that contains table of contents
        try:
            for file in os.listdir(self.dirPath):
                if file.endswith(".txt") and "~$" not in file:
                    # print(f"current dir: {self.dirPath}. \nCurrent File: {os.path.join(self.dirPath, file)}")
                    self.tableOfContents = TableOfContents(os.path.join(self.dirPath, file))
                    break
            
            if self.tableOfContents is None:
                raise ValueError(".txt for table of contents was not found")
        
            # create the flacList
            for file in os.listdir(self.dirPath):
                if file.endswith(".flac"):
                    flacSrcPath = os.path.join(self.dirPath, file)
                    # parse out the id
                    idStr = file.split(".")[0]
                    if idStr.isnumeric() is True:
                        id = int(idStr)
                        self.flacDict[id] = FLACDataDef(flacSrcPath)

                # check if the cover is within the current directory
                elif (file.endswith(".jpg") is True or file.endswith(".png")) and (file.lower()=="cover.jpg" or file.lower() == "cover.png"):
                    self.coverPath = os.path.join(self.dirPath, file)

            # print(self.dirPath)
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
    Update flac file meta data based of the tableOfContents information we have
    """
    def updateFLACMetaData(self):
        if self.tableOfContents is None:
            raise ValueError("You cannot change flac meta data with no txt file")
        
        for key, val in self.flacDict.items():
            try:
                val.setAlbumName(self.tableOfContents.getAlbumName())
                val.setAlbumArtist(self.tableOfContents.getAlbumArtist())
                val.setArtist(self.tableOfContents.getArtist(key))
                val.setTitle(self.tableOfContents.getTitle(key))
                val.setCover(self.coverPath)

            except Exception as e:
                print("Set FlacMeta Data, key: {key}: {e}")
            
            try:
                val.updateMetaData()
            except Exception as e:
                print("Update metadata: ", e)

                        
    def renameFlacFiles(self, fileName, newName = None):
        if fileName.endswith(".flac") is False and newName.endswith(".flac") is False:
            raise ValueError("you are not renaming a flac file or new name does not have .flac tag")
        
        l = fileName.split(".")
        # update the FlacData associated with this file
        if l[0].isnumeric():
            id = int(l[0])
            if (self.flacDict.get(id, None) is not None):
                self.flacDict[id].setSrcPath(os.path.join(self.dirPath, self.tableOfContents.getFileName(id)))

                os.rename(src=os.path.join(self.dirPath, fileName), dst=os.path.join(self.dirPath, self.tableOfContents.getFileName(id) ))


    
if __name__ == "__main__":
    
    # Get the current working directory
    path = os.getcwd()
    # Print the current working directory

    checkedDir = {}
    # obtain checkedDir data if it exists
    jsonPath = os.path.join(path, "checkedDir.json")
    if os.path.isfile(jsonPath) is True:
        with open(jsonPath, encoding="utf-8") as f:
            checkedDir = json.load(f)

    for dir in os.listdir(path):
        try:
            if os.path.isdir(os.path.join(path,dir) ) is False:
                continue
            # directory has been visited before
            if checkedDir.get(dir, False) == True:
                print(dir, " has already been worked on")
                continue

            start = time.time()
            # check if this txt file has been completed before
            print(f"working on {dir}")
            myDir = MusicDir(os.path.join(path, dir) )
            start1 = time.time()
            myDir.updateFLACMetaData()
            end1 = time.time()

            for file in os.listdir(myDir.dirPath):
                l = file.split(".")
                if (l[0].isnumeric() == True):
                    myDir.renameFlacFiles(file)

            # mark this dir as complete
            checkedDir[dir] = True
            end = time.time()
            print("Metadata time take: ", round(end1-start1,2))
            print("Time taken: ", round(end-start, 2) )
            # dirpath = os.path.join(path, dir)
            # for file in os.listdir(dirpath):
            #     l = file.split(".")
            #     if (l[0].isnumeric() == True):
            #         newFileName = os.path.join(dirpath, file) + ".flac"
            #         os.rename(src=os.path.join(dirpath, file), dst=newFileName)
        except Exception as e:
            print("failed: ", e)
            checkedDir[dir] = False


    for key, val in checkedDir.items():
        if val is False:
            print(key, "was unsucessful") 

    # dump collected data
    with open(jsonPath, "w", encoding="utf-8") as f:
        json.dump(checkedDir, f, ensure_ascii=False)