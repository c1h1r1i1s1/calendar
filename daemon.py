#!/bin/python

import time
import re
import signal
import os
import sys

#Use this variable for your loop
daemon_quit = False

#Do not modify or remove this handler
def quit_gracefully(signum, frame):
    global daemon_quit
    daemon_quit = True

def csv_writer(db_saved):
    global db_path
    db = open(db_path, "w")
    for element in db_saved:
        element = ','.join([str(i) if i != None else '' for i in element])
        db.write(element + "\n")
    db.close()

def reader(line, db_saved, db_path):
    line = re.split(''' (?=(?:[^'"]|'[^']*'|"[^"]*")*$)''', line)
    if len(line) >= 2:
        date_format = re.compile(r'\d\d-\d\d-\d\d\d\d\b')
        date = date_format.search(line[1])
        if date is None:
            raise ValueError("Unable to parse date")
        else:
            date = date[0].split('-')
            year = 2
            month = 1
            day = 0
    else:
        raise ValueError("Unable to parse date")
    if line[0] == "ADD":
        if len(line) < 3:
            raise ValueError("Missing event name")
        event = 2
        description = 3
        line[event] = line[event].strip("\n")
        if len(line) > 3:
            line[description] = line[description].strip("\n")
        if line[event][0] in ('"', "'") and line[event][-1] in ('"', "'"):
            line[event] = line[event][1:-1]
        if len(line) > 3 and line[description][0] in ('"', "'") and line[description][-1] in ('"', "'"):
            line[description] = line[description][1:-1]
        for entry in db_saved:
            if entry[0:2] == [str(date[day]) + "-" + str(date[month]) + "-" + str(date[year]),line[event]]:
                raise ValueError("Event already exists")
        if len(line) > 3:
            db_saved.append([str(date[day]) + "-" + str(date[month]) + "-" + str(date[year]),line[event],line[description]])
        else:
            db_saved.append([str(date[day]) + "-" + str(date[month]) + "-" + str(date[year]),line[event], None])
        csv_writer(db_saved)
    elif line[0] == "DEL":
        if len(line) < 3:
            raise ValueError("Missing event name")
        event = 2
        line[event] = line[event].strip("\n")
        if line[event][0] in ('"', "'") and line[event][-1] in ('"', "'"):
            line[event] = line[event][1:-1]
        i = 0
        while i < len(db_saved):
            if db_saved[i][0:2] == [str(date[day]) + "-" + str(date[month]) + "-" + str(date[year]), line[2]]:
                db_saved.pop(i)
            else:
                i += 1
        csv_writer(db_saved)
    elif line[0] == "UPD":
        if len(line) < 4:
            raise ValueError("Not enough arguments given")
        event = 2
        new_event = 3
        description = 4
        line[event] = line[event].strip("\n")
        if len(line) > 4:
            line[description] = line[description].strip("\n")
        if line[new_event][0] in ('"', "'") and line[new_event][-1] in ('"', "'"):
            line[new_event] = line[new_event][1:-1]
        if line[event][0] in ('"', "'") and line[event][-1] in ('"', "'"):
            line[event] = line[event][1:-1]
        if len(line) > 4 and line[description][0] in ('"', "'") and line[description][-1] in ('"', "'"):
            line[description] = line[description][1:-1]
        i = 0
        found = False
        while i < len(db_saved):
            if db_saved[i][0:2] == [str(date[day]) + "-" + str(date[month]) + "-" + str(date[year]), line[event]]:
                found = True
                for entry in db_saved:
                    if entry[0:2] == [str(date[day]) + "-" + str(date[month]) + "-" + str(date[year]),line[new_event]]:
                        raise ValueError("Event already exists")
                if len(line) > 4:
                    db_saved[i][0:3] = [str(date[day]) + "-" + str(date[month]) + "-" + str(date[year]), line[new_event], line[description]]
                else:
                    db_saved[i][0:3] = [str(date[day]) + "-" + str(date[month]) + "-" + str(date[year]), line[new_event], None]
            i += 1
        if not found:
            raise ValueError("Unable to update, event does not exist")
        csv_writer(db_saved)
    else:
        raise ValueError("Command not recognised")

def run():
    #Do not modify or remove this function call
    signal.signal(signal.SIGINT, quit_gracefully)

    global db_path
    err_file = open("/tmp/cald_err.log", "w")
    try:
        if len(sys.argv) > 1:
            if sys.argv[1].endswith(".csv"):
                if sys.argv[1].startswith("/"):
                    db_path = ['/' + '/'.join(sys.argv[1].split("/")[0:-1]).strip('/'), sys.argv[1].split("/")[-1]]
                else:
                    if '/' in sys.argv[1]:
                        db_path = [os.getcwd(), '/'.join(sys.argv[1].split("/")[0:-1]).strip('/'), sys.argv[1].split("/")[-1]]
                    else:
                        db_path = [os.getcwd(), sys.argv[1]]
            else:
                if sys.argv[1].startswith("/"):
                    db_path = ['/' + sys.argv[1].strip('/'), "cald_db.csv"]
                else:
                    db_path = [os.getcwd(), sys.argv[1].strip('/'), "cald_db.csv"]
        else:
            db_path = [os.getcwd(), "cald_db.csv"]
        path = '/'.join(db_path[0:-1])
        db_path = '/'.join(db_path)
        if not os.path.isfile(db_path):
            if not os.path.isdir(path):
                os.makedirs(path)
            db = open(db_path, "w")
            db.close()
        temp_file = open("/tmp/calendar_link", "w")
        temp_file.write(db_path)
        temp_file.close()
        pipe_loc = "/tmp/cald_pipe"
        if not os.path.exists(pipe_loc):
            os.mkfifo(pipe_loc) # Start the named pipe
    except Exception as err:
        err_file.write(str(err))
        err_file.close()
        sys.exit()
    err_file.close()
    
    while not daemon_quit: # Start main loop
        try:
            db = open(db_path, "r")
            db_saved = []
            for line in db:
                line = line.rstrip("\n")
                line = line.split(",")
                db_saved.append(line)
            db.close()
            command_input = os.open(pipe_loc, os.O_RDONLY | os.O_NONBLOCK)
            grace = True
            while True:
                try:
                    buf = os.read(command_input, 1000)
                    if not buf and not daemon_quit:
                        time.sleep(0.1)
                        continue
                    elif daemon_quit:
                        break
                    else:
                        line = buf.decode("utf-8")
                        break
                except OSError as e:
                    if e.errno == 11 and grace:
                        time.sleep(0.1)
                        grace = False
                    else:
                        break
            error_written = False
            try:
                reader(line, db_saved, db_path)
            except ValueError as err:
                err_file = open("/tmp/cald_err.log", "a")
                err_file.write("\n")
                err_file.write(str(err))
                err_file.close()
                error_written = True
            except Exception as err:
                err_file = open("/tmp/cald_err.log", "a")
                err_file.write("\n")
                err_file.write("Multiple errors occur")
                err_file.close()
                error_written = True
            if not error_written:
                err_file = open("/tmp/cald_err.log", "w")
                err_file.close()
        except ValueError as err:
            err_file = open("/tmp/cald_err.log", "a")
            err_file.write("\n")
            err_file.write(str(err))
            err_file.close()

    try:
        os.unlink("/tmp/cald_pipe")
    except Exception as err:
        err_file = open("/tmp/cald_err.log", "w")
        err_file.write(str(err))
        err_file.close()
    try:
        db.close()
    except Exception as err:
        err_file = open("/tmp/cald_err.log", "w")
        err_file.write(str(err))
        err_file.close()

if __name__ == '__main__':
    run()
