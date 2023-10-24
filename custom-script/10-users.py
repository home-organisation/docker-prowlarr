#!/usr/bin/python3
import sys
import os
import sqlite3
import logging
import hashlib

###########################################################
# SET STATIC CONFIG
###########################################################
logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)
PROWLARR_DB = '/config/prowlarr.db'


###########################################################
# DEFINE FUNCTION
###########################################################
def set_credential(database, username, password):
    # Create user in database
    data = ('652bf21b-fe69-47f7-8e52-80e0572a9025', username, password)
    query = "INSERT INTO Users (Identifier,Username,Password) VALUES(?, ?, ?)"
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
        return password


def get_credential(database, username):
    data = (username,)
    query = "SELECT Password FROM Users WHERE Username = ?"

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
        return rows[0][0]


def update_credential(database, username, password):
    data = (password, username)
    query = "UPDATE Users SET Password = ? WHERE Username = ?"

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
        return password


###########################################################
# INIT CONFIG
###########################################################
if __name__ == '__main__':
    PROWLARR_USER = os.environ.get('PROWLARR_USER')
    PROWLARR_PASSWORD = os.environ.get('PROWLARR_PASSWORD')
    if PROWLARR_USER is None or PROWLARR_PASSWORD is None:
        logging.warning("PROWLARR_USER or PROWLARR_PASSWORD with no value, nothing to do")
        sys.exit(0)

    logging.info("Set Credential to application for user %s ..." % PROWLARR_USER)
    PROWLARR_ENCRYPT = hashlib.sha256(PROWLARR_PASSWORD.encode('utf-8')).hexdigest()
    PASSWORD = get_credential(PROWLARR_DB, PROWLARR_USER)
    if PASSWORD is None:
        sys.exit(1)
    elif PASSWORD == "":
        PASSWORD = set_credential(PROWLARR_DB, PROWLARR_USER, PROWLARR_ENCRYPT)
        if PASSWORD is None:
            sys.exit(1)
    elif PASSWORD != PROWLARR_ENCRYPT:
        logging.info("User %s already exist but with an other password, update ..." % PROWLARR_USER)
        PASSWORD = update_credential(PROWLARR_DB, PROWLARR_USER, PROWLARR_ENCRYPT)
        if PASSWORD is None:
            sys.exit(1)
