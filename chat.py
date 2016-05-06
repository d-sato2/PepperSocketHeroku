# -*- coding: utf-8 -*-

"""
Chat Server
===========

This simple application uses WebSockets to run a primitive chat server.

initialize the database with this command:

flask --app=chat initdb
"""

import os
import redis
import gevent
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, jsonify
from flask_sockets import Sockets
from sqlite3 import dbapi2 as sqlite3
from datetime import datetime

'''
if os.environ['REDIS_URL']!=None:
    REDIS_URL = os.environ['REDIS_URL']
    redis = redis.from_url(REDIS_URL)
else:
    HOST='localhost'
    PORT=6379
    DB=0
    redis = redis.Redis(host=HOST, port=PORT, db=DB)
'''

HOST='localhost'
PORT=6379
DB=0
redis = redis.Redis(host=HOST, port=PORT, db=DB)
REDIS_CHAN = 'chat'
app = Flask(__name__)
app.debug = 'DEBUG' in os.environ
sockets = Sockets(app)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    DEBUG=True,
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

class ChatBackend(object):
    """Interface for registering and updating WebSocket clients."""

    def __init__(self):
        self.clients = list()
        self.pubsub = redis.pubsub()
        self.pubsub.subscribe(REDIS_CHAN)

    def __iter_data(self):
        for message in self.pubsub.listen():
            data = message.get('data')
            if message['type'] == 'message':
                data = data.decode('utf-8')
                app.logger.info(u'Sending message: {}'.format(data))
                yield data

    def register(self, client):
        """Register a WebSocket connection for Redis updates."""
        self.clients.append(client)

    def connect_db(self):
        """Connects to the specific database."""
        rv = sqlite3.connect(app.config['DATABASE'])
        rv.row_factory = sqlite3.Row
        return rv

    def init_db(self):
        """Initializes the database."""
        db = chats.get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

    @app.cli.command('initdb')
    def initdb_command():
        """Creates the database tables."""
        chats.init_db()
        print('Initialized the database.')

    def get_db(self):
        """Opens a new database connection if there is none yet for the
        current application context.
        """
        if not hasattr(g, 'sqlite_db'):
            g.sqlite_db = chats.connect_db()
        return g.sqlite_db

    def send(self, client, data):
        """Send given data to the registered client.
        Automatically discards invalid connections."""
        try:
            client.send(data)
        except Exception:
            self.clients.remove(client)

    def run(self):
        """Listens for new messages in Redis, and sends them to clients."""
        for data in self.__iter_data():
            for client in self.clients:
                gevent.spawn(self.send, client, data)

    def start(self):
        """Maintains Redis subscription in the background."""
        gevent.spawn(self.run)

chats = ChatBackend()
chats.start()

@app.route('/')
def show_entries():
    db = chats.get_db()
    cur = db.execute('select id, qr, name, lang, memo, start from entries order by id desc')
    entries = cur.fetchall()
    return render_template('show_entries.html', entries=entries)

@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    db = chats.get_db()
    db.execute('insert into entries (qr, name, lang, memo, start) values (?, ?, ?, ?, ?)',
               [request.form['qr'], request.form['name'], request.form['lang'], request.form['memo'], datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))

@app.route('/show/<int:entry_id>', methods=['GET'])
def show_entry(entry_id):
    db = chats.get_db()
    cur = db.execute('select id, qr, name, lang, memo, start from entries where id = ?', [entry_id])
    entry = cur.fetchone()
    return render_template('show.html', entry=entry)


@app.route('/json/<int:entry_qr>', methods=['GET'])
def json_entry(entry_qr):
    db = chats.get_db()
    cur = db.execute('select id, qr, name, lang, memo, start from entries where qr = ?', [entry_qr])
    entry = cur.fetchone()
    if entry is None:
        return 'There is no data. Please check QR code number.'
    else:
        entry_json ={
               'id': entry[0],
               'qr': entry[1],
               'name': entry[2],
               'lang': entry[3],
               'memo': entry[4],
               'start': entry[5],
           }
        return jsonify(entry_json)

@app.route('/edit/<int:entry_id>', methods=['GET', 'POST'])
def edit_entry(entry_id):
    error = None
    if not session.get('logged_in'):
        abort(401)
    if request.method == 'GET':
        db = chats.get_db()
        cur = db.execute('select id, qr, name, lang, memo, start from entries where id = ?', [entry_id])
        entry = cur.fetchone()
        return render_template('edit.html', error=error, entry=entry)
    elif request.method == 'POST':
        db = chats.get_db()
        db.execute('update entries set qr = ?, name = ?, lang = ?, memo = ? where id = ?',
                   [request.form['qr'], request.form['name'], request.form['lang'], request.form['memo'], entry_id])
        db.commit()
        flash('The entry was successfully updated')
        return redirect(url_for('show_entries'))

@app.route('/delete/<int:entry_id>', methods=['GET'])
def delete_entry(entry_id):
    if not session.get('logged_in'):
        abort(401)
    db = chats.get_db()
    cur = db.execute('delete from entries where id = ?', [entry_id])
    db.commit()
    return render_template('delete.html', entry_id = entry_id)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))

@app.route('/chat')
def hello():
    return render_template('index.html')

@sockets.route('/submit')
def inbox(ws):
    """Receives incoming chat messages, inserts them into Redis."""
    while not ws.closed:
        # Sleep to prevent *constant* context-switches.
        gevent.sleep(0.1)
        message = ws.receive()

        if message:
            message = message.decode('utf-8')
            app.logger.info(u'Inserting message: {}'.format(message))
            redis.publish(REDIS_CHAN, message)

@sockets.route('/receive')
def outbox(ws):
    """Sends outgoing chat messages, via `ChatBackend`."""
    chats.register(ws)

    while not ws.closed:
        # Context switch while `ChatBackend.start` is running in the background.
        gevent.sleep(0.1)

