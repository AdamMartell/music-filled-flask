#!/usr/bin/env python2

import subprocess
import sys

def stream(youtube_id):
    from database import MusicFlaskDatabase
    import json

    data   = json.loads(MusicFlaskDatabase[youtube_id])
    url    = data['url']
    curl   = 'curl --silent {}'.format(url)
    ffmpeg = 'ffmpeg -loglevel panic -i - -f mp3 -'

    curl_process   = subprocess.Popen(curl.split(), stdout=subprocess.PIPE)
    ffmpeg_process = subprocess.Popen(ffmpeg.split(), stdin=curl_process.stdout)

    ffmpeg_process.communicate()

if __name__ == '__main__':
    stream(sys.argv[1])

# vim: set sts=4 sw=4 ts=8 expandtab ft=python:
