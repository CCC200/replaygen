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
    replayfiles = [] # 0 = filename, 1 = title, 2 = timestamp
    filters = []
    # scan folder for replay files and build list
    with os.scandir(out_dir) as d:
        for e in d:
            if e.name != 'index.html':
                unix = int(e.name.split('-')[0])
                timestamp = datetime.date.fromtimestamp(unix)
                f = open(e.path, 'r')
                lines = f.readlines()
                f.close()
                title = lines[3].replace("<title>", "").replace("</title>", "")
                replayfiles.append([e.name, title, timestamp])
    # load template
    templatefile = open('index-template.html', 'r')
    html = templatefile.read()
    templatefile.close()
    # add list entries
    listentries = ''
    filterentries = ''
    for r in replayfiles:
        listentries = f'<a href="{r[0]}" target="_blank">{r[1]}<br><small>{r[2]}</small></a>' + listentries
        fname = r[1].split(':')[0]
        if fname not in filters:
            filters.append(fname)
    filters.sort()
    for f in filters:
        filterentries += f'<option value="{f}">{f}</option>'
    html = html.replace('<!-- REPLAY_ENTRIES -->', listentries).replace('<!-- FORMAT_FILTERS -->', filterentries)
    # write file
    indexfile = open(out_dir + '/index.html', 'w')
    indexfile.write(html)
    indexfile.close()
    print('Index updated')
    

def scan_logs(full = False):
    basedirs = []
    if full:
        exclude = ['chat', 'modlog', 'randbats', 'repl', 'tickets']
        with os.scandir(log_dir) as d:
            for e in d:
                if os.path.isdir(e.path) and e.name not in exclude:
                    basedirs.append(e.path)
    else:
        dt = datetime.datetime.now()
        curdir = log_dir + "/" + dt.strftime("%Y-%m")
        if not os.path.isdir(curdir): # no replays to scan
            return
        basedirs.append(curdir)
    topdirs = []
    subdirs = []
    # build list of log directories
    for dir in basedirs:
        with os.scandir(dir) as d:
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
        print(f'{gens} replays generated, rebuilding index...', end=' ')
        build_index()
    elif full:
        print('Rebuilding index...', end=' ')
        build_index()

def scan_full():
    print('Starting full scan...')
    scan_logs(True)

# load config json
if not os.path.isfile('config.json'):
    print('Config does not exist, creating default...', end=' ')
    shutil.copyfile('config-template.json', 'config.json')
configfile = open('config.json', 'r')
configdata = configfile.read()
configfile.close()
config = json.loads(configdata)
print('Config loaded')
# check directories
log_dir = config["log_dir"]
out_dir = config["out_dir"]
if not os.path.isdir(log_dir):
    print('Log directory does not exist! Aborting...')
    sys.exit(1)
if not os.path.isdir(out_dir):
    os.mkdir(out_dir)
if not os.path.isfile(out_dir + '/index.html'):
    print('Index does not exist, creating default...')
    shutil.copyfile('index-template.html', out_dir + '/index.html')
# full scan then loop
scan_full()
print('Scanning for new logs...')
while True:
    scan_logs()
    time.sleep(60)
