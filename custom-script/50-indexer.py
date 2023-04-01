#!/usr/bin/python3
import sys
import json
import os
import sqlite3
import logging

###########################################################
# SET STATIC CONFIG
###########################################################
logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)
PROWLARR_DB = '/config/prowlarr.db'


###########################################################
# DEFINE FUNCTION
###########################################################
def set_indexer(database, name, url, user, password, tag, tagid):
    data = (name, 'Cardigann', '{"definitionFile": "yggtorrent", "extraFieldData": '
            '{"username": "' + user + '", "password": "' + password + '", "category": 6, "filter_title": false, '
            '"multilang": false, "multilanguage": 1, "vostfr": false, "enhancedAnime": false, "enhancedAnime4": false, '
            '"sort": 1, "type": 1 }, "baseUrl": "' + url + '", "baseSettings": {}, '
            '"torrentBaseSettings": {}}',
            'CardigannSettings', 1, 25, '2023-04-01 22:05:12.6172687Z', 0, 1, '[' + str(tagid) + ']')
    query = "INSERT INTO Indexers (Name,Implementation,Settings,ConfigContract,Enable,Priority,Added,Redirect," \
            "AppProfileId,Tags) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
    connexion = sqlite3.connect(database)
    db = connexion.cursor()

    try:
        db.execute(query, data)
        connexion.commit()

        db.close()
        connexion.close()
    except sqlite3.Error as er:
        logging.error('SQLite error: %s' % (' '.join(er.args)))
        return None
    else:
        return {"url": url, "user": user, "password": password, "tag": tag, "tagid": tagid}


def update_indexer(database, name, url, user, password, tag, tagid):
    data = ('{"definitionFile": "yggtorrent", "extraFieldData": '
            '{"username": "' + user + '", "password": "' + password + '", "category": 6, "filter_title": false, '
            '"multilang": false, "multilanguage": 1, "vostfr": false, "enhancedAnime": false, "enhancedAnime4": false,'
            '"sort": 1, "type": 1 }, "baseUrl": "' + url + '", "baseSettings": {}, "torrentBaseSettings": {}}',
            '[' + str(tagid) + ']', name)
    query = "UPDATE Indexers SET Settings = ?, Tags = ? WHERE Name = ?"

    connexion = sqlite3.connect(database)
    db = connexion.cursor()

    try:
        db.execute(query, data)
        connexion.commit()

        db.close()
        connexion.close()
    except sqlite3.Error as er:
        logging.error('SQLite error: %s' % (' '.join(er.args)))
        return None
    else:
        return {"url": url, "user": user, "password": password, "tag": tag, "tagid": tagid}


def get_indexer(database, name, tag):
    # Get indexer URL, User, Password from database
    data = (name,)
    query = "SELECT * FROM Indexers WHERE Name = ?"

    connexion = sqlite3.connect(database)
    db = connexion.cursor()

    try:
        db.execute(query, data)
        rows = db.fetchall()

        db.close()
        connexion.close()

        if not rows:
            raise ValueError
    except sqlite3.Error as er:
        logging.error('SQLite error: %s' % (' '.join(er.args)))
        return None
    except ValueError:
        indexer = {"url": "", "user": "", "password": "", "tag": "", "tagid": ""}
    else:
        row = json.loads(rows[0][3])
        indexer = {"url": row["baseUrl"], "user": row["extraFieldData"]["username"],
                   "password": row["extraFieldData"]["password"], "tag": "", "tagid": ""}

    # Get Tag id from name from database
    data = (tag,)
    query = "SELECT * FROM Tags WHERE Label = ?"

    connexion = sqlite3.connect(database)
    db = connexion.cursor()

    try:
        db.execute(query, data)
        rows = db.fetchall()

        db.close()
        connexion.close()

        if not rows:
            raise ValueError
    except sqlite3.Error as er:
        logging.error('SQLite error: %s' % (' '.join(er.args)))
        return None
    except ValueError:
        indexer["tag"] = ""
        indexer["tagid"] = ""
    else:
        indexer["tag"] = rows[0][1]
        indexer["tagid"] = rows[0][0]

    return indexer


###########################################################
# INIT CONFIG
###########################################################
if __name__ == '__main__':
    INDEXER_URL = os.environ.get('INDEXER_URL')
    INDEXER_NAME = os.environ.get('INDEXER_NAME')
    INDEXER_USER = os.environ.get('INDEXER_USER')
    INDEXER_PASSWORD = os.environ.get('INDEXER_PASSWORD')
    PROWLARR_PROXYTAG = os.environ.get('PROWLARR_PROXYTAG')
    if INDEXER_URL is None or INDEXER_NAME is None or INDEXER_USER is None or INDEXER_PASSWORD is None or \
            PROWLARR_PROXYTAG is None:
        logging.warning("INDEXER_URL, INDEXER_NAME, INDEXER_USER, INDEXER_PASSWORD or PROWLARR_PROXYTAG with no "
                        "value, nothing to do")
        sys.exit(0)

    logging.info("Set Indexer <%s> with url %s and tag <%s> to application ..." % (
        INDEXER_NAME, INDEXER_URL, PROWLARR_PROXYTAG))
    message = get_indexer(PROWLARR_DB, INDEXER_NAME, PROWLARR_PROXYTAG)
    if message is None:
        sys.exit(1)

    if message["tagid"] == "":
        logging.error("Tag <%s> doesn't exist" % PROWLARR_PROXYTAG)
        sys.exit(1)

    if message["url"] == "" and message["user"] == "" and message["password"] == "":
        message = set_indexer(PROWLARR_DB, INDEXER_NAME, INDEXER_URL, INDEXER_USER, INDEXER_PASSWORD, PROWLARR_PROXYTAG,
                              message["tagid"])
        if message is None:
            sys.exit(1)

    if message["url"] != INDEXER_URL or message["user"] != INDEXER_USER or message["password"] != INDEXER_PASSWORD or \
            message["tag"] != PROWLARR_PROXYTAG:
        logging.info("YGGTorrent Indexer already exist but with another value, update")
        message = update_indexer(PROWLARR_DB, INDEXER_NAME, INDEXER_URL, INDEXER_USER, INDEXER_PASSWORD,
                                 PROWLARR_PROXYTAG,
                                 message["tagid"])
        if message is None:
            sys.exit(1)
