#!/usr/bin/env python2

from flask import Flask, Response, render_template, request
from flask.ext.wtf import Form
from wtforms import TextField
from wtforms.validators import DataRequired
from urlparse import urlparse, parse_qs
from database import MusicFlaskDatabase, get_recent_songs

import json
import os
import subprocess

app = Flask(__name__)

class AddYouTubeStreamForm(Form):
    youtube_url = TextField('Add new stream:', validators=[DataRequired()])


@app.route("/")
def list():
       users = [f for f in os.listdir("lists/") if os.path.isfile(os.path.join("lists/",f))]
       songs = get_recent_songs(10)
       return render_template('users.html', users=users, songs=songs)

@app.route("/song/<songid>", methods=['GET'])
def audio(songid):
    with MusicFlaskDatabase() as db:
        data = json.loads(db[songid.encode('utf-8')])
    url = data['url']
    http = 'wget -qO- {}'.format(url)
    ffmpeg = 'ffmpeg -loglevel panic -i - -f mp3 -'

    http_process = subprocess.Popen(http.split(), stdout=subprocess.PIPE)
    ffmpeg_process = subprocess.Popen(ffmpeg.split(), stdin=http_process.stdout, stdout=subprocess.PIPE)

    return Response(ffmpeg_process.stdout, mimetype = 'audio/mpeg', headers = {
               'Content-Disposition': 'attachment;fileneme=' + songid })

def stream_file(file_path):
    file_id = os.path.basename(file_path)
    data = open(file_path)
    return Response(data,
	    mimetype = 'audio/mpeg',
	    headers  = {
	        'Content-Disposition': 'attachment;filename=' + file_id
	    })         

@app.route("/playlist/<playlistid>", methods = ['GET', 'POST'])
def playlist(playlistid):
    playlist_path = './lists/' + playlistid
    playlist_file = open(playlist_path, 'a+')
    songs = get_recent_songs(10)
    form = AddYouTubeStreamForm(csrf_enabled=False)

    if form.validate_on_submit():
        youtube_url = form.youtube_url.data
        youtube_id = determine_youtube_id(youtube_url)
        playlist_file.write(youtube_id + '\n')
        playlist_file.seek(0)
        os.system('python pre_fetch.py {}'.format(youtube_id))
    else:
        youtube_url = None

    with MusicFlaskDatabase() as db:
        playlist = dict([(key, json.loads(db.get(key, '{}'))) for key in map(str.strip, playlist_file)])

    return render_template('playlist.html', form=form, playlistid=playlistid, playlist=playlist, songs=songs)

def determine_youtube_id(youtube_url):
    if 'youtu.be' in youtube_url:
        youtube_id = os.path.basename(youtube_url)
    else:
        youtube_id = parse_qs(urlparse(youtube_url).query)['v'][0]
    return youtube_id

@app.route('/m3u/<playlistid>')
def m3u(playlistid):
    playlist_path = './lists/' + playlistid
    playlist_file = open(playlist_path, 'r')
    with MusicFlaskDatabase() as db:
        playlist = dict([(key, json.loads(db.get(key, '{}'))) for key in map(str.strip, playlist_file)])
    return Response(render_template('m3u.html', playlistid=playlistid, playlist=playlist), mimetype = 'audio/x-mpegurl')

if __name__ == "__main__":
    os.umask(002)   # Group Read/Write
    app.run(host='0.0.0.0', port=9898, debug=True)
