import datetime
import os


def log(logpath, logstatus):

    daytime = datetime.datetime.now().strftime('%Y%m%d %I:%M %p')
    f = open(os.path.join(logpath, "run_log.txt"), "r+")
    newline = "{} {}\n".format(daytime, logstatus)
    oline = f.readlines()
    oline.insert(0, newline)
    f.close()

    f = open(os.path.join(logpath, "run_log.txt"), "w")
    f.writelines(oline)
    f.close()
             
    return
