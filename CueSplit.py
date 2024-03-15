import os
import re
import utilities as util
import File_Renaming as fr
import sys
from mutagen.flac import Picture
from mutagen.flac import FLAC
from ffcuesplitter.cuesplitter import FFCueSplitter
from ffcuesplitter.user_service import FileSystemOperations


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

    # create a new .cue file for 
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


# TODO:: include batch processing
if __name__ == "__main__":

    cwd = os.getcwd()
    targetDir = os.path.join(cwd, sys.argv[1])
    dirName = sys.argv[1].rstrip(" \"/\\").lstrip(".\\/")

    # check if targetDir is legitimate
    assert os.path.exists(targetDir) == True

    musicDir = fr.MusicDir(targetDir, dirName=dirName)
    cueCopy = os.path.join(targetDir, "test_COPY.cue")

    cueFile = CueFile(musicDir.cuePath)
    toc = fr.TableOfContents(musicDir.tableOfContentsPath)

    # update cuefile metadata with what was obtained in TableOfContents

    cueFile.AlbumTitle = toc.albumName
    cueFile.FileName = musicDir.dirName + ".flac"
    cueFile.Performer = toc.albumArtist

    # update the track data
    trackLen = len(cueFile.TrackList)
    for i in range(trackLen):
        cueFile.TrackList[i].setTitle(toc.getTitle(i+1))
        cueFile.TrackList[i].setPerformer(toc.getArtist(i+1))

    cueFile.writeToCueFile(cueCopy)

    # set the cover picture for the major flac file
    try:
        targetFlacFile = fr.FLACDataDef(musicDir.majorFlacPath, musicDir.coverPath)
        targetFlacFile.updateMetaData()

    except AssertionError as msg:
        print(msg)



    # obtain data of flac file
    # getData = FFCueSplitter(filename=cueCopy, outputdir=targetDir, outputformat="flac", dry=True)
    # l = getData.audiotracks
    # print(l)

    # split the data
    # split = FileSystemOperations(filename=cueCopy, outputdir=targetDir, outputformat="flac", dry=False)
    # if split.kwargs['dry']:
    #     split.dry_run_mode()
    # else:
    #     overwr = split.check_for_overwriting()
    #     if not overwr:
    #         split.work_on_temporary_directory()
 
    