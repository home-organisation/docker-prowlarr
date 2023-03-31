#!/usr/bin/python3
import sys
import json
import sqlite3
import logging

###########################################################
# SET STATIC CONFIG
###########################################################
logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)
PROWLARR_DB = '/config/prowlarr.db'
PROWLARR_PROXYURL = "http://localhost:8191"
PROWLARR_PROXYNAME = "FlareSolverr"
PROWLARR_PROXYTAG = "flare"


###########################################################
# DEFINE FUNCTION
###########################################################
def set_proxy(database, name, url, tagid):
    data = (name, '{ "host": "' + url + '",  "requestTimeout": 60}', "FlareSolverr", "FlareSolverrSettings",
            '[' + str(tagid) + ']')
    query = "INSERT INTO IndexerProxies (Name,Settings,Implementation,ConfigContract,Tags) VALUES(?, ?, ?, ?, ?)"
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
        return url


def set_tags(database, tag):
    data = (tag,)
    query = "INSERT INTO Tags (Label) VALUES(?)"
    connexion = sqlite3.connect(database)
    db = connexion.cursor()

    try:
        db.execute(query, data)
        tagid = db.lastrowid
        connexion.commit()

        db.close()
        connexion.close()
    except sqlite3.Error as er:
        logging.error('SQLite error: %s' % (' '.join(er.args)))
        return None
    else:
        return tagid


def update_proxy(database, name, url, tagid):
    data = ('{ "host": "' + url + '",  "requestTimeout": 60}', '[' + str(tagid) + ']', name)
    query = "UPDATE IndexerProxies SET Settings = ?, Tags = ? WHERE Name = ?"

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
        return url


def update_tags(database, tag, tagid):
    data = (tag, tagid)
    query = "UPDATE Tags SET Label = ? WHERE Id = ?"

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
        return tag


def get_indexerproxy(database, name):
    # Get URL and Tag ID of IndexerProxies
    data = (name,)
    query = "SELECT * FROM IndexerProxies WHERE Name = ?"

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
        return {"url": "", "tagID": "", "tag": ""}
    else:
        TAGID = rows[0][5].replace('[', '').replace(']', '')
        URL = json.loads(rows[0][2])["host"]

    # Get Tag name associate with this IndexerProxies
    data = (TAGID,)
    query = "SELECT * FROM Tags WHERE Id = ?"

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
        return {"url": URL, "tagID": TAGID, "tag": ""}
    else:
        return {"url": URL, "tagID": TAGID, "tag": rows[0][1]}


###########################################################
# INIT CONFIG
###########################################################
if __name__ == '__main__':
    logging.info("Set Indexer Proxy <%s> with url %s and tag <%s> to application ..." % (
    PROWLARR_PROXYNAME, PROWLARR_PROXYURL, PROWLARR_PROXYTAG))
    message = get_indexerproxy(PROWLARR_DB, PROWLARR_PROXYNAME)
    if message is None:
        sys.exit(1)

    if message["tagID"] == "":
        message["tagID"] = set_tags(PROWLARR_DB, PROWLARR_PROXYTAG)
        message["tag"] = PROWLARR_PROXYTAG
        if message["tagID"] is None:
            sys.exit(1)

    if message["url"] == "":
        message["url"] = set_proxy(PROWLARR_DB, PROWLARR_PROXYNAME, PROWLARR_PROXYURL, message["tagID"])
        if message["url"] is None:
            sys.exit(1)

    if message["url"] != PROWLARR_PROXYURL or message["tag"] != PROWLARR_PROXYTAG:
        logging.info("FlareSolver Indexer Proxy already exist but with another value, update")
        message["url"] = update_proxy(PROWLARR_DB, PROWLARR_PROXYNAME, PROWLARR_PROXYURL, message["tagID"])
        message["tag"] = update_tags(PROWLARR_DB, PROWLARR_PROXYTAG, message["tagID"])
