# SplitAndFileRename

NOTE:: STILL IN PROGRESS
GOAL: All in one packaged executable that splits and renames my flac files. Also provide executable for users so you don't need to build it

There are two scripts: CueSplit.py and FileRenaming.py

1. FileRenaming.py
To use it:
  python3 FileRenaming.py

The music files downloaded sometimes have an unkown encoding (not utf-8), so the metadata that comesout is gibberish. However, they provide a seperate .txt file that contains the relevent information in utf-8 encoding. This script parses the information and applies it on
to the already split flac files.

Before writing this script, I have hundereds of directories filled with this, and I am too lazy to change it manually, so this automates it.

2. CueSplit.py
Standard Cue splitter tool that uses a module done by JeanSlack (credits to him)
To use it:
  python3 CueSplit.py "targetDirectoryName"

This will split the flac file based off .cue file (must exist) provided in the directory. As mentioned, the flac and .cue files uses some unknown encoding. This also include funcionality of parsing the .txt file to update the cue file data
So when the flac file is split, everthing is in utf-8 encoding.


#Required packages:
1. ffpmeg  https://ffmpeg.org/download.html
2. https://github.com/jeanslack/FFcuesplitter (python3 -m pip install ffcuesplitter)
   
