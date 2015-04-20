#!/bin/sh

export PYTHONPATH=.:$PYTHONPATH

paster serve config.ini
