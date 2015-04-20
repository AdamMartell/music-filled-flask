#!/usr/bin/env python2

from flask import Flask, render_template
from flask.ext.wtf import Form
from wtforms import TextField
from wtforms.validators import DataRequired
from os import listdir
from os.path import isfile, join

app= Flask(__name__)
@app.route("/")
def list():
      onlyfiles = [f for f in listdir("lists/") if isfile(join("lists/",f))]
      sizeof = len(onlyfiles)
      textlist = ""
      for x in range(0, sizeof):
          textlist += "<a href=\"/playlist/" + ''.join(onlyfiles[x]) + "\">" + ''.join(onlyfiles[x]) + "</a><br />"

      return textlist 

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=9467, debug=True)
