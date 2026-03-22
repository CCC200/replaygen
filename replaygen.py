from pokemon_showdown_replays import Replay, Download
import json, os, shutil, sys, datetime, time

log_dir = ''
out_dir = ''
client_url = 'https://play.pokemonshowdown.com'
formats = []
rated = []

def is_format(n):
    if 'all' in formats or n in formats:
        return True
    else:
        return False
    
def is_rated(log):
    for r in rated:
        if f'rated|{r}' in log:
            return True
    return False

def convert_log(f):
    # f = filepath
    # get battle log as json
    logfile = open(f, 'r', encoding='utf-8')
    logdata = logfile.read()
    logfile.close()
    log = json.loads(logdata)
    # build replay file
    r = Replay.create_replay_object(log)
    r_id = r["id"].split('battle-')[1]
    r_format = r_id.split('-')[0]
    if not is_format(r_format) and not is_rated(r["log"]): # match conditions
        return 0
    n = str(r["timestamp"]) + '-' + r_id
    p = out_dir + '/' + n
    if os.path.isdir(p): # log already converted
        return 0
    else:
        os.mkdir(p)
    html = Download.create_replay(r, client_url + '/js/replay-embed.js')
    # custom inject
    cssfile = open('html/custom.css', 'r')
    css = cssfile.read()
    cssfile.close()
    html = html.replace('<!-- version 1 -->', '<meta name="viewport" content="width=device-width, initial-scale=1.0" />\n<!-- version 1 -->')
    html = html.replace('</style>', f'{css}</style>')
    html = html.replace('<div class="wrapper replay-wrapper" style="max-width:1180px;margin:0 auto">', '<div class="wrapper replay-wrapper">')
    # write files
    rfile = open(p + '/index.html', 'w', encoding='utf-8')
    rfile.write(html)
    rfile.close()
    r_api = r
    r_api['players'] = [r_api.pop('p1'), r_api.pop('p2')]
    jfile = open(f'{out_dir}/{n}.json', 'w', encoding='utf-8')
    jfile.write(json.dumps(r_api, indent=4))
    jfile.close()
    print(f'Generated {n}')
    return 1
    

def build_index():
    replayfiles = [] # 0 = filename, 1 = title, 2 = timestamp
    filters = []
    # scan folder for replay files and build list
    with os.scandir(out_dir) as d:
        for e in d:
            if e.name != 'index.html' and not e.name.endswith('.json'):
                unix = int(e.name.split('-')[0])
                timestamp = datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%d %H:%M:%S')
                f = open(e.path + '/index.html', 'r', encoding='utf-8')
                lines = f.readlines()
                f.close()
                title = lines[4].replace("<title>", "").replace("</title>", "")
                replayfiles.append([e.name, title, timestamp])
    # load template
    templatefile = open('html/index-template.html', 'r')
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
                if e.is_file() and '.log.json' in e.name:
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
# optional params
if "client_url" in config:
    client_url = config["client_url"]
if "formats" in config:
    formats = config["formats"]
if "rated" in config:
    rated = config["rated"]
# check directories
log_dir = config["log_dir"]
out_dir = config["out_dir"]
if not os.path.isdir(log_dir):
    print('Log directory does not exist! Aborting...')
    sys.exit(1)
if '-clean' in sys.argv and os.path.isdir(out_dir):
    shutil.rmtree(out_dir)
if not os.path.isdir(out_dir):
    os.mkdir(out_dir)
if not os.path.isfile(out_dir + '/index.html'):
    print('Index does not exist, creating default...')
    shutil.copyfile('html/index-template.html', out_dir + '/index.html')
# full scan then loop
scan_full()
print('Scanning for new logs...')
while True:
    scan_logs()
    time.sleep(60)
