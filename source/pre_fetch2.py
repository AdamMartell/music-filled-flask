#!/usr/bin/env python2

import json
import os
import subprocess

def make_youtube_url(youtube_id):
    return 'http://youtu.be/{}'.format(youtube_id)

def pre_fetch_one(youtube_id):
    # TODO: Figure out a way to get lowest quality file
    # --max-quality flv gets the best flv, which tends to be smaller than other formats
    youtube_url = make_youtube_url(youtube_id)

    command     = './youtube-dl --list-formats {}'.format(youtube_url)
    process     = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    stdout, _   = process.communicate()
    format      = stdout.split('\n')[-2].split()[0]

    command     = './youtube-dl --format {} --skip-download -o %(id)s --write-info-json {}'.format(format, youtube_url)
    process     = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    stdout, _   = process.communicate()
    info_json   = stdout.strip().split()[-1]
    data        = json.load(open(info_json))

    os.unlink(info_json)

    return data

def test_prefetch_one():
    # TODO: Move these imports to the top
    from database import MusicFlaskDatabase
    
    print pre_fetch_one('uXVZhl0Cb9g')
    MusicFlaskDatabase['uXVZhl0Cb9g'] = json.dumps(pre_fetch_one('uXVZhl0Cb9g'))
    MusicFlaskDatabase['lLJf9qJHR3E'] = json.dumps(pre_fetch_one('lLJf9qJHR3E'))
    MusicFlaskDatabase['5NV6Rdv1a3I'] = json.dumps(pre_fetch_one('5NV6Rdv1a3I'))
    MusicFlaskDatabase.sync()

if __name__ == '__main__':
    test_prefetch_one()

# vim: set sts=4 sw=4 ts=8 expandtab ft=python:
