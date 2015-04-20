#!/usr/bin/env python2

import json
import os
import subprocess
import sys
import time

from database import MusicFlaskDatabase

def make_youtube_url(youtube_id):
    return 'http://www.youtube.com/watch?v={0}'.format(youtube_id)

def pre_fetch_one(youtube_id):
    youtube_url = make_youtube_url(youtube_id)

    command     = './youtube-dl --list-formats {0}'.format(youtube_url)
    process     = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    stdout, _   = process.communicate()
    format      = stdout.split('\n')[-2].split()[0]

    command     = './youtube-dl --format {0} --skip-download -o %(id)s --write-info-json {1}'.format(format, youtube_url)
    process     = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    stdout, _   = process.communicate()
    info_json   = stdout.strip().split()[-1]
    data        = json.load(open(info_json))

    os.unlink(info_json)

    with MusicFlaskDatabase(writable=True) as db:
        try:
            data['timestamp'] = json.loads(db[youtube_id])['timestamp']
        except KeyError:
            data['timestamp'] = time.time()

        db[youtube_id] = json.dumps(data)

    print youtube_id, data['timestamp']
    return data

def pre_fetch_all():
    song_ids = set()
    for list_name in os.listdir('lists'):
        file_path = os.path.join('lists', list_name)
        for line in open(file_path):
            line = line.strip()
            song_ids.add(line)

    for song_id in song_ids:
        pre_fetch_one(song_id)

def test_prefetch_one():
    with MusicFlaskDatabase(writable=True) as db:
        pre_fetch_one('uXVZhl0Cb9g')
        pre_fetch_one('lLJf9qJHR3E')
        pre_fetch_one('5NV6Rdv1a3I')

if __name__ == '__main__':
    if len(sys.argv) == 1:
        pre_fetch_all()

    for youtube_id in sys.argv[1:]:
        pre_fetch_one(youtube_id)

# vim: set sts=4 sw=4 ts=8 expandtab ft=python:
