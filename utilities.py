"""
General Helper functions
"""

def SubstringAfter(s: str , delim: str):
    return s.partition(delim)[2]

def getFirstNumSeqFromStr(fileName: str) -> int:

    s = ""
    for c in fileName:
        if c.isdigit():
            s = s + c
        else:
            break
    if s == "":
        return -1
    return int(s)

def CheckFileUtf8(path):
    try:
        print("path: ", path)
        f = open(path, mode="r")
        data = f.read()
        print("data: ", data)
        return True
    except UnicodeDecodeError:
        return False