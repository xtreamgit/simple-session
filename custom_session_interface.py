from flask.sessions import SessionInterface, SessionMixin
from pymongo import MongoClient
import pickle
from uuid import uuid4
from datetime import datetime, timedelta

class CustomSessionInterface(SessionInterface):
    def __init__(self, uri, db, collection):
        self.client = MongoClient(uri)
        self.store = self.client[db][collection]

    def open_session(self, app, request):
        session_id = request.cookies.get(app.config['SESSION_COOKIE_NAME'])
        if session_id:
            stored_session = self.store.find_one({'id': session_id})
            if stored_session:
                data = pickle.loads(stored_session['data'])
                return Session(data, sid=session_id)
        return Session(sid=None)

    def save_session(self, app, session, response):
        if not session:
            self.store.delete_one({'id': session.sid})
            response.delete_cookie(app.config['SESSION_COOKIE_NAME'])
            return

        session_data = dict(session)
        store_id = session.sid or str(uuid4())
        expires = datetime.utcnow() + timedelta(days=app.permanent_session_lifetime.days)

        self.store.update_one(
            {'id': store_id},
            {'$set': {
                'data': pickle.dumps(session_data),
                'expires': expires
            }},
            upsert=True
        )

        response.set_cookie(app.config['SESSION_COOKIE_NAME'], store_id, expires=expires)

class Session(dict, SessionMixin):
    def __init__(self, initial=None, sid=None):
        super().__init__(initial or {})
        self.sid = sid
        self.modified = False
