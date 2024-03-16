import os
import MusicDirectory as md
import sys

from ffcuesplitter.cuesplitter import FFCueSplitter
from ffcuesplitter.user_service import FileSystemOperations


if __name__ == "__main__":

    cwd = os.getcwd()
    targetDir = os.path.join(cwd, sys.argv[1])
    dirName = sys.argv[1].rstrip(" \"/\\").lstrip(".\\/")

    # check if targetDir is legitimate
    assert os.path.exists(targetDir) == True

    musicDir = md.MusicDir(targetDir, dirName=dirName)
    cueCopy = os.path.join(targetDir, "test_COPY.cue")

    cueFile = md.CueFile(musicDir.cuePath)
    toc = md.TableOfContents(musicDir.tableOfContentsPath)

    # We should only change cuefile metadata with what was obtained in TableOfContents
    # when the cue file contains data that is not utf-8 encoding

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
        targetFlacFile = md.FLACDataDef(musicDir.majorFlacPath, musicDir.coverPath)
        targetFlacFile.updateMetaData()

    except AssertionError as msg:
        print(msg)

    # split the major flac file into tracks
    split = FileSystemOperations(filename=cueCopy, outputdir=targetDir, outputformat="flac", dry=False, overwrite="ask")
    if split.kwargs['dry']:
        split.dry_run_mode()
    else:
        overwr = split.check_for_overwriting()
        if not overwr:
            split.work_on_temporary_directory()
 
    