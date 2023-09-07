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
def set_radarr(database, name, prowlarrurl, radarrurl, radarrkey, tag, tagid):
    data = (name, 'Radarr', '{"prowlarrUrl": "' + prowlarrurl + '", "baseUrl": "' + radarrurl + '", "apiKey": "'
            + radarrkey + '", "syncCategories": [2000,2010,2020,2030,2040,2045,2050,2060,2070,2080]}',
            'RadarrSettings', 2, '[' + str(tagid) + ']')
    query = "INSERT INTO Applications (Name,Implementation,Settings,ConfigContract,SyncLevel,Tags) " \
            "VALUES(?, ?, ?, ?, ?, ?)"
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
        return {"prowlarrurl": prowlarrurl, "radarrurl": radarrurl, "radarrkey": radarrkey, "tag": tag, "tagid": tagid}


def update_radarr(database, name, prowlarrurl, radarrurl, radarrkey, tag, tagid):
    data = ('{"prowlarrUrl": "' + prowlarrurl + '", "baseUrl": "' + radarrurl + '", "apiKey": "'
            + radarrkey + '", "syncCategories": [2000,2010,2020,2030,2040,2045,2050,2060,2070,2080]}',
            '[' + str(tagid) + ']', name)
    query = "UPDATE Applications SET Settings = ?, Tags = ? WHERE Name = ?"

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
        return {"prowlarrurl": prowlarrurl, "radarrurl": radarrurl, "radarrkey": radarrkey, "tag": tag, "tagid": tagid}


def get_radarr(database, name, tag):
    # Get Applications from database
    data = (name,)
    query = "SELECT * FROM Applications WHERE Name = ?"

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
        radarr = {"prowlarrurl": "", "radarrurl": "", "radarrkey": "", "tag": "", "tagid": ""}
    else:
        row = json.loads(rows[0][3])
        radarr = {"prowlarrurl": row["prowlarrUrl"], "radarrurl": row["baseUrl"], "radarrkey": row["apiKey"],
                  "tag": "", "tagid": ""}

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
        radarr["tag"] = ""
        radarr["tagid"] = ""
    else:
        radarr["tag"] = rows[0][1]
        radarr["tagid"] = rows[0][0]

    return radarr


###########################################################
# INIT CONFIG
###########################################################
if __name__ == '__main__':
    PROWLARR_URL = os.environ.get('PROWLARR_URL')
    RADARR_URL = os.environ.get('RADARR_URL')
    RADARR_NAME = os.environ.get('RADARR_NAME')
    RADARR_APIKEY = os.environ.get('RADARR_APIKEY')
    PROWLARR_PROXYTAG = os.environ.get('PROWLARR_PROXYTAG')
    if PROWLARR_URL is None or RADARR_URL is None or RADARR_NAME is None or RADARR_APIKEY is None or \
            PROWLARR_PROXYTAG is None:
        logging.warning("PROWLARR_URL, RADARR_URL, RADARR_NAME, RADARR_APIKEY or PROWLARR_PROXYTAG with no "
                        "value, nothing to do")
        sys.exit(0)

    logging.info("Set Radarr Application <%s> with url %s and tag <%s> to application ..." % (
        RADARR_NAME, RADARR_URL, PROWLARR_PROXYTAG))
    message = get_radarr(PROWLARR_DB, RADARR_NAME, PROWLARR_PROXYTAG)
    if message is None:
        sys.exit(1)

    if message["tagid"] == "":
        logging.error("Tag <%s> doesn't exist" % PROWLARR_PROXYTAG)
        sys.exit(1)

    if message["prowlarrurl"] == "" and message["radarrurl"] == "" and message["radarrkey"] == "":
        message = set_radarr(PROWLARR_DB, RADARR_NAME, PROWLARR_URL, RADARR_URL, RADARR_APIKEY, PROWLARR_PROXYTAG,
                             message["tagid"])
        if message is None:
            sys.exit(1)

    if message["prowlarrurl"] != PROWLARR_URL or message["radarrurl"] != RADARR_URL or \
            message["radarrkey"] != RADARR_APIKEY or message["tag"] != PROWLARR_PROXYTAG:
        logging.info("Radarr Application already exist but with another value, update")
        message = update_radarr(PROWLARR_DB, RADARR_NAME, PROWLARR_URL, RADARR_URL, RADARR_APIKEY, PROWLARR_PROXYTAG,
                                message["tagid"])
        if message is None:
            sys.exit(1)
