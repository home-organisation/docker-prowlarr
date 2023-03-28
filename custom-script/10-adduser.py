#!/usr/bin/python3
import sys
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
def set_credential(database, username, password):
    # Create user in database
    adddata = ('652bf21b-fe69-47f7-8e52-80e0572a9025', username, password)
    addquery = "INSERT INTO Users (Identifier,Username,Password) VALUES(?, ?, ?)"
    updatedata = (username, password)
    updatequery = "UPDATE Users SET Password = ? WHERE Username = ?"

    try:
        connexion = sqlite3.connect(database)
        db = connexion.cursor()

        db.execute(addquery, adddata)
        connexion.commit()
    except sqlite3.Error as er:
        if (' '.join(er.args)) == "UNIQUE constraint failed: Users.Username":
            logging.warning("User %s already exist, update password to match" % username)
            db.execute(updatequery, updatedata)

            connexion.commit()
        elif (' '.join(er.args)) == "unable to open database file":
            logging.error("Unable to open database file %s" % database)
            sys.exit(1)
        else:
            logging.error('SQLite error: %s' % (' '.join(er.args)))
    finally:
        db.close()
        connexion.close()


###########################################################
# INIT CONFIG
###########################################################
if __name__ == '__main__':
    PROWLARR_USER = os.environ.get('PROWLARR_USER')
    PROWLARR_PASSWORD = os.environ.get('PROWLARR_PASSWORD')

    logging.info("Set Credential to application for user %s ..." % PROWLARR_USER)
    set_credential(PROWLARR_DB, PROWLARR_USER, PROWLARR_PASSWORD)
