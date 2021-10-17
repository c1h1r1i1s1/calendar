import time
import re
import os
import sys

def date_display(entry):
    if len(entry) > 2:
        print("{} : {} : {}".format(entry[0], entry[1], entry[2]))
    else:
        print("{} : {} : ".format(entry[0], entry[1]))

def run():
    # First clear error log:
    err_log = open("/tmp/cald_err.log", "w")
    err_log.close()
    try:
        link = open("/tmp/calendar_link", 'r')
        db_path = link.readline()
        link.close()
        db = open(db_path, "r")
        db_saved = []
        for line in db:
            line = line.rstrip("\n")
            line = line.split(",")
            db_saved.append(line)
        db.close()
    except:
        print("Unable to process calendar database")
        sys.exit()

    if len(sys.argv) >= 2:
        action = sys.argv[1]
    else:
        print("Not enough arguments given")
        sys.exit()
    if action == "GET":
        if len(sys.argv) >= 3:
            option = sys.argv[2]
        else:
            print("Not enough arguments given")
            sys.exit()
        if option == "DATE":
            if len(sys.argv) < 4:
                print("Unable to parse date")
                sys.exit()
            for date_n in sys.argv[3:]:
                date_format = re.compile(r'\d\d-\d\d-\d\d\d\d$')
                date = date_format.search(date_n)
                if date is None:
                    print("Unable to parse date")
                    continue
                date = date[0].split('-')
                year = 2
                month = 1
                day = 0
                for entry in db_saved:
                    if str(date[day]) + "-" + str(date[month]) + "-" + str(date[year]) == entry[0]:
                        date_display(entry)
        elif option == "INTERVAL":
            if len(sys.argv) < 5:
                print("Not enough arguments given")
                sys.exit()
            date_format = re.compile(r'\d\d-\d\d-\d\d\d\d\b')
            date1 = date_format.search(sys.argv[3])
            date2 = date_format.search(sys.argv[4])
            if date1 is None or date2 is None:
                print("Unable to parse date")
                sys.exit()
            date1 = date1[0].split('-')
            date2 = date2[0].split('-')
            if int(str(date1[2])+str(date1[1])+str(date1[0])) > int(str(date2[2])+str(date2[1])+str(date2[0])):
                print("Unable to Process, Start date is after End date")
                sys.exit()
            db_saved = sorted(db_saved, key=lambda k: (k[0][6:10], k[0][3:5], k[0][0:2]))
            for entry in db_saved:
                if int(str(date1[2])+str(date1[1])+str(date1[0])) <= int(str(entry[0][6:10])+str(entry[0][3:5])+str(entry[0][0:2])) <= \
                        int(str(date2[2])+str(date2[1])+str(date2[0])):
                            date_display(entry)
        elif option == "NAME":
            if len(sys.argv) < 4:
                print("Please specify an argument")
                sys.exit()
            for event in db_saved:
                if event[1].startswith(sys.argv[3]):
                    date_display(event)
        else:
            print("Invalid Action", file=sys.stderr)
    elif action in ["ADD", "UPD", "DEL"]:
        command_pass = []
        for item in sys.argv[1:]:
            if ' ' in item:
                item = '"'+item+'"'
            command_pass.append(item)
        command_pass = ' '.join(command_pass)
        if os.path.exists("/tmp/cald_pipe"):
            pipeline = open("/tmp/cald_pipe", "w")
        else:
            print("Pipe does not exist", file=sys.stderr)
            sys.exit()
        pipeline.write(command_pass)
        pipeline.close()
        time.sleep(0.2)
        err_log = open("/tmp/cald_err.log", "r")
        num_lines = sum(1 for line in err_log if line.rstrip())
        if num_lines > 1:
            print("Multiple errors occur", file=sys.stderr)
        elif num_lines == 1:
            err_log.seek(0, 0)
            for line in err_log:
                if len(line) > 1:
                    print(line)
        err_log.close()
    else:
        print("Command not recognised", file=sys.stderr)


if __name__ == '__main__':
    run()

