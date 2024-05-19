from flask.sessions import SessionInterface
from pymongo import MongoClient

class CustomSessionInterface(SessionInterface):
    def __init__(self, uri, db, collection):
        self.client = MongoClient(uri)
        self.store = self.client[db][collection]

    def save_session(self, app, session, response):
        store_id = session.get('id')
        if store_id:
            self.store.delete_one({'id': store_id})
