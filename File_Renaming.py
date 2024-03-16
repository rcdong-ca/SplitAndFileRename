import os
import time
import json
import MusicDirectory as md
    
if __name__ == "__main__":

    # Get the current working directory
    path = os.getcwd()
    # Print the current working directory

    checkedDir = {}
    failedMessage = {}
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
            print(f"working on {dir}...")
            musicDir = md.MusicDir(os.path.join(path, dir) )
            
            # update flac data based off table of contents information
            toc = md.TableOfContents(musicDir.tableOfContentsPath)
            for key, flac in musicDir.flacDict.items():
                # print(key)
                # print(toc.getTitle(key))
                # print(toc.getAlbumArtist())
                # print(toc.getAlbumName())
                # print(toc.getArtist(key))
                flac.albumArtist = toc.getAlbumArtist()
                flac.albumName = toc.getAlbumName()
                flac.title = toc.getTitle(key)
                flac.artist = toc.getArtist(key)
                flac.updateMetaData()

                # change file name
                newFlacName = str(key) + " - " + flac.title + ".flac"
                newFlacPath = os.path.join(musicDir.dirPath, newFlacName)
                flac.renameFile(newFlacPath)
            # mark this dir as complete
            checkedDir[dir] = True

            end = time.time()
            print("Time taken: ", round(end-start, 2) ,"seconds...\n")
        except Exception as e:
            print("failed: ", e, "\n")
            checkedDir[dir] = False
            failedMessage[dir] = e


    for key, val in checkedDir.items():
        if val is False:
            print(key, "Failed to have metadata updated")
            print(failedMessage.get(key),"\n")

    # dump collected data
    with open(jsonPath, "w", encoding="utf-8") as f:
        json.dump(checkedDir, f, ensure_ascii=False)