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
def set_sonarr(database, name, prowlarrurl, sonarrurl, sonarrkey, tag, tagid):
    data = (name, 'Sonarr', '{"prowlarrUrl": "' + prowlarrurl + '", "baseUrl": "' + sonarrurl + '", "apiKey": "'
            + sonarrkey + '", "syncCategories": [5000,5010,5020,5030,5040,5045,5050], "animeSyncCategories": [5070]}',
            'SonarrSettings', 2, '[' + str(tagid) + ']')
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
        return {"prowlarrurl": prowlarrurl, "sonarrurl": sonarrurl, "sonarrkey": sonarrkey, "tag": tag, "tagid": tagid}


def update_sonarr(database, name, prowlarrurl, sonarrurl, sonarrkey, tag, tagid):
    data = ('{"prowlarrUrl": "' + prowlarrurl + '", "baseUrl": "' + sonarrurl + '", "apiKey": "'
            + sonarrkey + '", "syncCategories": [5000,5010,5020,5030,5040,5045,5050], "animeSyncCategories": [5070]}',
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
        return {"prowlarrurl": prowlarrurl, "sonarrurl": sonarrurl, "sonarrkey": sonarrkey, "tag": tag, "tagid": tagid}


def get_sonarr(database, name, tag):
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
        sonarr = {"prowlarrurl": "", "sonarrurl": "", "sonarrkey": "", "tag": "", "tagid": ""}
    else:
        row = json.loads(rows[0][3])
        sonarr = {"prowlarrurl": row["prowlarrUrl"], "sonarrurl": row["baseUrl"], "sonarrkey": row["apiKey"],
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
        sonarr["tag"] = ""
        sonarr["tagid"] = ""
    else:
        sonarr["tag"] = rows[0][1]
        sonarr["tagid"] = rows[0][0]

    return sonarr


###########################################################
# INIT CONFIG
###########################################################
if __name__ == '__main__':
    PROWLARR_URL = os.environ.get('PROWLARR_URL')
    SONARR_URL = os.environ.get('SONARR_URL')
    SONARR_NAME = os.environ.get('SONARR_NAME')
    SONARR_APIKEY = os.environ.get('SONARR_APIKEY')
    PROWLARR_PROXYTAG = os.environ.get('PROWLARR_PROXYTAG')
    if PROWLARR_URL is None or SONARR_URL is None or SONARR_NAME is None or SONARR_APIKEY is None or \
            PROWLARR_PROXYTAG is None:
        logging.warning("PROWLARR_URL, SONARR_URL, SONARR_NAME, SONARR_APIKEY or PROWLARR_PROXYTAG with no "
                        "value, nothing to do")
        sys.exit(0)

    logging.info("Set Sonarr Application <%s> with url %s and tag <%s> to application ..." % (
        SONARR_NAME, SONARR_URL, PROWLARR_PROXYTAG))
    message = get_sonarr(PROWLARR_DB, SONARR_NAME, PROWLARR_PROXYTAG)
    if message is None:
        sys.exit(1)

    if message["tagid"] == "":
        logging.error("Tag <%s> doesn't exist" % PROWLARR_PROXYTAG)
        sys.exit(1)

    if message["prowlarrurl"] == "" and message["sonarrurl"] == "" and message["sonarrkey"] == "":
        message = set_sonarr(PROWLARR_DB, SONARR_NAME, PROWLARR_URL, SONARR_URL, SONARR_APIKEY, PROWLARR_PROXYTAG,
                             message["tagid"])
        if message is None:
            sys.exit(1)

    if message["prowlarrurl"] != PROWLARR_URL or message["sonarrurl"] != SONARR_URL or \
            message["sonarrkey"] != SONARR_APIKEY or message["tag"] != PROWLARR_PROXYTAG:
        logging.info("Sonarr Application already exist but with another value, update")
        message = update_sonarr(PROWLARR_DB, SONARR_NAME, PROWLARR_URL, SONARR_URL, SONARR_APIKEY, PROWLARR_PROXYTAG,
                                message["tagid"])
        if message is None:
            sys.exit(1)
