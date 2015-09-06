import sys
import csv
from subprocess import call, DEVNULL

from os.path import join
from pprint import pprint
from datetime import datetime


ISO_8601 = '%Y-%m-%dT%H:%M:%S'
F_TIME = 'ISO time'
F_ARTIST = 'artist name'
F_TRACK = 'track name'


class LastFMCSV:
    delimiter = '\t'
    quotechar = '"'
    quoting = csv.QUOTE_MINIMAL


class Scrobble:
    def __init__(self, data):
        self.time = datetime.strptime(data[F_TIME], ISO_8601)
        self.artist = data[F_ARTIST]
        self.track = data[F_TRACK]

    def __str__(self):
        return "Scrobble<%s %s - %s>" % (
            self.get_time(), self.artist, self.track)

    def as_track(self):
        return "%s - %s" % (self.artist, self.track)

    def get_time(self):
        return self.time.isoformat()


def read_scrobbles(scrobble_file):
    fields = None
    scrobbles = []
    for row in csv.reader(scrobble_file, dialect=LastFMCSV):
        if fields is None:
            fields = row
            continue
        item = dict(zip(fields, row))
        scrobbles.append(Scrobble(item))
    return scrobbles


def scrobble(gitdir, item):
    with open(join(gitdir, 'last_played'), 'w') as f:
        f.write(item.as_track() + '\n')
    call(['git', 'add', '-Av'], cwd=gitdir, stdout=DEVNULL, stderr=DEVNULL)
    message = "Played: %s" % item.as_track()
    cmd = ['git', 'commit', '--message', message, '--date', item.get_time()]
    call(cmd, cwd=gitdir, stdout=DEVNULL, stderr=DEVNULL)


def main():
    _, gitdir, datadir = sys.argv
    scrobbles_file = join(datadir, 'scrobbles.tsv')
    with open(scrobbles_file, 'r') as f:
        scrobbles = read_scrobbles(f)
    
    for count, item in enumerate(scrobbles, start=1):
        if count % 100 == 0: print(item)
        scrobble(gitdir, item)
    

if __name__ == '__main__':
    main()
