
import signal
import sys
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
        f = open(path, mode="r")
        data = f.read()
        return True
    except UnicodeDecodeError:
        return False


class SignalDetect:
    """
    If Signal is detected, signalFlag will be set to true. This allows us to exit after we are processing a directory.
    As our changes can affect disk, we do not want to stop the process halfway.
    """
    sigIntFlag = False

    def __init__(self) -> None:
        pass

    def SignalHandler(self, signalNum, frame):
        """
        If signal is received, this method will be triggered.

        Input:
          signalNum (constant): a signal. Ex SIGINT
        """
        if signalNum == signal.SIGINT:
            print("Ctrl+C detected, will exit shortly...")
            self.sigIntFlag = True

