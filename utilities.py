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
