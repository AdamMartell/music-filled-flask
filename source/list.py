#!/usr/bin/env python2

from flask import Flask

class videolist():

def init():
	urls = [ ]

def add_video(url):
	urls.append(url)

def get_next():
	return urls.pop()

def toString():
	return urls
