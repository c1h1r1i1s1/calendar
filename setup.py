import sys
import os

action = sys.argv[1]
if action == "build":
    print("Building source files:")
    print("Ensuring init file knows where to find daemon...")
    cald = open("src/cald", 'r')
    lines = []
    for line in cald:
            lines.append(line)
    cald.close()
    lines[1] = "location='{}'\n".format(os.getcwd())
    print(lines[1])
    cald = open("src/cald", "w")
    for line in lines:
        cald.write(line)
    cald.close()
    print("Done!")
    print("Build complete")
    sys.exit()
elif action == "test":
    print("Checking build:")
    if os.path.isfile("/etc/init.d/cald"):
        print("Init file in place")
    else:
        print("Init file not in place! Please package again")
        sys.exit()
    txt = open("/etc/init.d/cald", 'r')
    lines = []
    for line in txt:
            lines.append(line)
    txt.close()
    if len(lines[1]) > 1 and len(lines[1].split("=")[1]) > 1:
        print("Location set in cald file: {}".format(lines[1].split("=")[1]))
    else:
        print("Location not in cald file, please run build and package again")
        sys.exit()
    rc_check = int(os.popen('rc-status | grep cald | wc -l').read())
    if rc_check > 0:
        print("Init file in rc-status")
    else:
        print("Init file not in rc-status, please run package again")
        sys.exit()
    print("Build check succesful")
    sys.exit()
