import os
import MusicDirectory as md
import sys
import utilities as util
import signal
import time

from ffcuesplitter.user_service import FileSystemOperations


if __name__ == "__main__":

    cwd = os.getcwd()
    musicDirectories = []
    
    exitSignal = util.SignalDetect()
    signal.signal(signal.SIGINT, exitSignal.SignalHandler)

    if sys.argv[1] == "batch":
        for dir in os.listdir(cwd):
            try:
                targetDir = os.path.join(cwd, dir)
                if (os.path.isdir(targetDir)) is False:
                    continue
                dirName = dir
                musicDir = md.MusicDir(targetDir, dirName=dirName)
                musicDirectories.append(musicDir)
            except Exception as e:
                print(f"{dir} does not meet the requirement to be split ", e)

    else:
        # single directory process pass as parameter
        targetDir = os.path.join(cwd, sys.argv[1])
        dirName = sys.argv[1].rstrip(" \"/\\").lstrip(".\\/")
        musicDir = md.MusicDir(targetDir, dirName=dirName)
        musicDirectories.append(musicDir)

    # process all the music directories
    for musicDir in musicDirectories:
        if (exitSignal.sigIntFlag is True):
            # detected Ctrl+C previously, exit now
            print("Ctrl + C detected, exiting now")
            exit(0)
        print("\nWorking on ", musicDir.dirName)
        cueFile = md.CueFile(musicDir.cuePath)

        # We should only change cuefile metadata with what was obtained in TableOfContents
        # when the cue file contains data that is not utf-8 encoding
        if util.CheckFileUtf8(cueFile.srcPath) is False:
            toc = md.TableOfContents(musicDir.tableOfContentsPath)
            cueCopy = os.path.join(musicDir.dirPath, "test_COPY.cue")
            cueFile.AlbumTitle = toc.albumName
            cueFile.FileName = musicDir.dirName + ".flac"
            cueFile.Performer = toc.albumArtist

            # update the track data
            trackLen = len(cueFile.TrackList)
            for i in range(trackLen):
                cueFile.TrackList[i].setTitle(toc.getTitle(i+1))
                cueFile.TrackList[i].setPerformer(toc.getArtist(i+1))

            cueFile.writeToCueFile(cueCopy)
            cueFile.srcPath = cueCopy

        # set the cover picture for the major flac file
        try:
            targetFlacFile = md.FLACDataDef(musicDir.majorFlacPath, musicDir.coverPath)
            targetFlacFile.updateMetaData()

        except Exception as msg:
            print("failed to add picture:", msg)

        # split the major flac file into tracks
        split = FileSystemOperations(filename=cueFile.srcPath, outputdir=musicDir.dirPath, outputformat="flac", dry=False, overwrite="ask")
        if split.kwargs['dry']:
            split.dry_run_mode()
        else:
            overwr = split.check_for_overwriting()
            if not overwr:
                split.work_on_temporary_directory()
 
    