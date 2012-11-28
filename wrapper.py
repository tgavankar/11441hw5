import sys
import mainscript

parseCache = None
if __name__ == "__main__":
    while True:
        if not parseCache:
            parseCache = mainscript.parseData()
        mainscript.main(parseCache)
        print "Press enter to re-run the script, CTRL-C to exit"
        sys.stdin.readline()
        reload(mainscript)