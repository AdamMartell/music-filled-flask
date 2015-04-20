#!/usr/bin/env python2

import bsddb
import contextlib
import json

DATABASE_PATH = 'metadata.db'

@contextlib.contextmanager
def MusicFlaskDatabase(db_path=None, writable=False):
    db_path = db_path = DATABASE_PATH

    if writable:
        database = bsddb.btopen(db_path, 'c')
    else:
        database = bsddb.btopen(db_path, 'r')
    yield database
    database.close()

def get_songs(key=None, reverse=False):
    with MusicFlaskDatabase() as db:
        return sorted(map(json.loads, db.values()), key=key, reverse=reverse)

def get_recent_songs(limit=None):
    return get_songs(key=lambda s: s.get('timestamp', 0), reverse=True)[:limit]

# vim: set sts=4 sw=4 ts=8 expandtab ft=python:
