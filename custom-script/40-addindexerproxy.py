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
def set_proxy(database, name, url, tag):
    data = (name, '{ "host": "' + url + '",  "requestTimeout": 60}', "FlareSolverr", "FlareSolverrSettings", tag)
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
        return name


def get_proxy(database, name):
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
        return ""
    else:
        TAG = rows[0][5]
        URL = json.loads(rows[0][2])["host"]
        return {"url": URL, "tag": TAG}


def update_proxy(database, name, url, tag):
    data = ('{ "host": "' + url + '",  "requestTimeout": 60}', tag, name)
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
        return name


###########################################################
# INIT CONFIG
###########################################################
if __name__ == '__main__':
    logging.info("Set Indexer Proxy <%s> with url %s to application ..." % (PROWLARR_PROXYNAME, PROWLARR_PROXYURL))
    message = get_proxy(PROWLARR_DB, PROWLARR_PROXYNAME)
    if message is None:
        sys.exit(1)
    elif message == "":
        message = set_proxy(PROWLARR_DB, PROWLARR_PROXYNAME, PROWLARR_PROXYURL, PROWLARR_PROXYTAG)
        if message is None:
            sys.exit(1)
    elif message["url"] != PROWLARR_PROXYURL or message["tag"] != PROWLARR_PROXYTAG:
        logging.info("FlareSolver Indexer Proxy already exist but with another value, update")
        message = update_proxy(PROWLARR_DB, PROWLARR_PROXYNAME, PROWLARR_PROXYURL, PROWLARR_PROXYTAG)
        if message is None:
            sys.exit(1)
