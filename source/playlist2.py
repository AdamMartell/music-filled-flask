#!/usr/bin/env python2

from flask import Flask, Response, render_template, request
from flask.ext.wtf import Form
from wtforms import TextField
from wtforms.validators import DataRequired
from urlparse import urlparse, parse_qs
from database import MusicFlaskDatabase

import json
import os
import subprocess

Application = Flask(__name__)

class AddYouTubeStreamForm(Form):
    youtube_url = TextField('Add New YouTube Stream:', validators=[DataRequired()])


@Application.route('/')
def list():
       users = [f for f in os.listdir("lists/") if os.path.isfile(os.path.join("lists/",f))]
       return render_template('users.html', users=users)

@Application.route('/song/<songid>', methods=['GET'])
def song(songid):
    data   = json.loads(MusicFlaskDatabase[songid.encode('utf-8')])
    url    = data['url']
    http   = 'wget -qO- {}'.format(url)
    ffmpeg = 'ffmpeg -loglevel panic -i - -f mp3 -'

    http_process   = subprocess.Popen(http.split(), stdout=subprocess.PIPE)
    ffmpeg_process = subprocess.Popen(ffmpeg.split(), stdin=http_process.stdout, stdout=subprocess.PIPE)

    return Response(ffmpeg_process.stdout,
	    mimetype = 'audio/mpeg',
	    headers  = {
	        'Content-Disposition': 'attachment;filename=' + songid
	    })         

@Application.route('/playlist/<playlistid>', methods=['GET', 'POST'])
def playlist(playlistid):
    playlist_path = './lists/' + playlistid 
    playlist_file = open(playlist_path, 'a+')

    form = AddYouTubeStreamForm(csrf_enabled=False)

    if form.validate_on_submit():
        youtube_url = form.youtube_url.data
        youtube_id  = determine_youtube_id(youtube_url)
        playlist_file.write(youtube_id + '\n')
        playlist_file.seek(0)
    else:
        youtube_url = None

    playlist = dict([(key, json.loads(MusicFlaskDatabase[key])) for key in map(str.strip, playlist_file)])
    
    return render_template('playlist2.html', form=form, playlistid=playlistid, playlist=playlist)

def determine_youtube_id(youtube_url):
    if 'youtu.be' in youtube_url:
        youtube_id = os.path.basename(youtube_url)
    else:
        youtube_id = parse_qs(urlparse(youtube_url).query)['v']
    return youtube_id


if __name__ == '__main__':
    Application.run(host='0.0.0.0', port=9988, debug=True)
