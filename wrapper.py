import sys
import mainscript

part1Cache = None
if __name__ == "__main__":
    while True:
        if not part1Cache:
            part1Cache = mainscript.parseData()
        mainscript.main(part1Cache)
        print "Press enter to re-run the script, CTRL-C to exit"
        sys.stdin.readline()
        reload(mainscript)