from pokemon_showdown_replays import Replay, Download
import json, os, shutil, sys, datetime, time

log_dir = ''
out_dir = ''

def convert_log(f):
    # f = filepath
    # get battle log as json
    logfile = open(f, 'r')
    logdata = logfile.read()
    logfile.close()
    log = json.loads(logdata)
    # build replay file
    r = Replay.create_replay_object(log)
    n = str(r["timestamp"]) + '-' + r["id"].split('battle-')[1] + '.html'
    p = out_dir + '/' + n
    if os.path.isfile(p): # log already converted
        return
    html = Download.create_replay(r)
    rfile = open(p, 'w')
    rfile.write(html)
    rfile.close()
    print('Generated ' + n)
    

def scan_logs():
    dt = datetime.datetime.now()
    curdir = log_dir + "/" + dt.strftime("%Y-%m")
    topdirs = []
    subdirs = []
    # build list of log directories
    with os.scandir(curdir) as d:
        for e in d:
            topdirs.append(e.path)
    for dir in topdirs:
        with os.scandir(dir) as d:
            for e in d:
                subdirs.append(e.path)
    # scan for logs and convert
    for dir in subdirs:
        with os.scandir(dir) as d:
            for e in d:
                if e.is_file() and e.name.find('.log.json') > -1:
                    convert_log(e.path)
    
    


# load config json
if not os.path.isfile('config.json'):
    print('config.json does not exist, creating default...')
    shutil.copyfile('config-template.json', 'config.json')
configfile = open('config.json', 'r')
configdata = configfile.read()
configfile.close()
config = json.loads(configdata)
print('config.json loaded')
# check directories
log_dir = config["log_dir"]
out_dir = config["out_dir"]
if not os.path.isdir(log_dir):
    print('Log directory does not exist! Aborting...')
    sys.exit(1)
if not os.path.isdir(out_dir):
    os.mkdir(out_dir)
# scan current folder
print('Scanning for logs...')
while True:
    scan_logs()
    time.sleep(60)
