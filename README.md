# SplitAndFileRename

TODO:: add the executable for windows...

## Objective: 
The goal of this project is to automate Cue split operation and adjust broken meta data with known data in .txt File when I download music. Often times the foreign music I have utilizes an unknown encoding for the meta data, so after splitting, I am left with a bunch of garbage texts. Luckily the downloads carry a .txt file that contains the utf-8 version of the meta data. These scripts essentially parses the .txt file and gathers the information and changes the .flac file meta data accordingly. Here is an example of what I am talking about

<table>
<tr>
<th>SampleTXT.txt</th>
<th>SmapleCUE.cue</th>
</tr>
<tr>
<td>

```SampleTxt.txt
                          群星《2024试听小屋系列(115)》[FLAC]



专辑名称:2024试听小屋系列(115)
专辑艺人:群星
合集制作:重庆钩住你
平面设计:冬雪育春
制作时间:2024-02-18
CQGZN:202402180757
资源类型:FLAC+CUE
介绍

     试听小屋是新的系列，将一年收藏的新歌曲归纳在试听小屋。分集发布，

创建原版营地，新歌尽在试听小屋！更多新歌原版首发QQ:512173646《重庆钩住你原版单曲》


曲目

01.白水寒--我问
02.陈亦洺vs尚辰--向春风
...
```

</td>
<td>

```SampleCUE.cue
REM GENRE A Cappella
REM DATE 2024-02-18
PERFORMER "Ⱥ��"
TITLE "2024����С��ϵ��(115)"
FILE "Ⱥ�ǡ�2024����С��ϵ��(115)��[FLAC].flac" WAVE
  TRACK 01 AUDIO
    TITLE "01.����"
    PERFORMER "��ˮ��"
    INDEX 01 00:00:00
  TRACK 02 AUDIO
    TITLE "02.�򴺷�(δ������/���÷�����ʹ��)"
    PERFORMER "������vs�г�"
    INDEX 01 02:31:66
  ...
```

</td>
</tr>
</table>

---

## FileRenaming.py
This script is primarily used for existing music files that has already been split before adjusting the meta data. This script will work on all subdirectories within the current working directory. Note, this script will only change the .flac files that has an index in its name. Ex. "01 - SOngTitle"
If it doesn't, nothing will be changed. As this is a batch process, it will also generate a json file ```checkedDir.json.``` This file is to track which directories has already been processed. So if one adds more directories that need their files renamed, it will only process the NEW directories added.

This will also ***attach a jpeg file named Cover.jpg**** onto all the flac files. (Perhaps I will add other image extension support too in the future). However, if the picture is larger than 5MB, it will use binary search to compress the image (no write) and attach it to the file . 
Note: (**Too large of an image will fail** to attach to the flac file, currently the reason is unkown)

To use it:
```python3 FileRenaming.py```

To exit the application, please use ```Ctrl + C```. This will stop after the current directory is done processing.


## CueSplit.py
This is a Standard Cue splitter tool that uses a module done by JeanSlack (credits to him) which uses ffmpeg to split it. The additional feature I added, once again, will handle the imporper encoding problem. As one can see previously in SampleCue.cue the metadata has garbaged characters. Once again we will utilize the .txt file to change the metadata. The changes will be written to a new .cue file named test_COPY.cue. This new cue file will be used to split the large .flac file into its tracks. 

Once again, for batch processing, it also includes a checkedDir for the same reason previously mentioned. Cover.jpg attachment will also be done. Directories that do not have a .cue file or large .flac (main flac file) will not be affected.
To use it:
  ```
  # single directory processing
  python3 CueSplit.py "targetDirectoryName"

  # multiple directory processing
  python3 Cuesplit.py batch
  ```
  To exit the application, please use ```Ctrl + C```. This will stop after the current directory is done processing.

---

## Requires If you want do not want to use the provided executables...
1. ffpmeg  https://ffmpeg.org/download.html
2. https://github.com/jeanslack/FFcuesplitter (python3 -m pip install ffcuesplitter)
   
