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
        return 0
    html = Download.create_replay(r)
    rfile = open(p, 'w')
    rfile.write(html)
    rfile.close()
    print(f'Generated {n}')
    return 1
    

def build_index():
    replayfiles = [] # 0 = filename, 1 = title
    # scan folder for replay files and build list
    with os.scandir(out_dir) as d:
        for e in d:
            if e.name != 'index.html':
                f = open(e.path, 'r')
                lines = f.readlines()
                f.close()
                title = lines[3].replace("<title>", "").replace("</title>", "")
                replayfiles.append([e.name, title])
    # load template
    templatefile = open('index-template.html', 'r')
    html = templatefile.read()
    templatefile.close()
    # add list entries
    listentries = ''
    for r in replayfiles:
        listentries = f'<a href="{r[0]}" target="_blank">{r[1]}</a>' + listentries
    html = html.replace('<!-- REPLAY_ENTRIES -->', listentries)
    # write file
    indexfile = open(out_dir + '/index.html', 'w')
    indexfile.write(html)
    indexfile.close()
    print('Index file updated')
    

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
    gens = 0
    for dir in subdirs:
        with os.scandir(dir) as d:
            for e in d:
                if e.is_file() and e.name.find('.log.json') > -1:
                    gens += convert_log(e.path)
    if gens > 0:
        print(f'{gens} replays generated, rebuilding index...')
        build_index()
    
    


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
