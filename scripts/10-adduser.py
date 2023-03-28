#!/usr/bin/python3
import sys
import os
import sqlite3
import logging
import xml.etree.ElementTree as ET

###########################################################
# SET STATIC CONFIG
###########################################################
logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)
CONFIG_FILE = '/config/config.xml'
PROWLARR_DB = '/config/prowlarr.db'


###########################################################
# DEFINE FUNCTION
###########################################################
def set_authenticationmethod(file, method):
    # Set Authentication method to xml config files
    try:
        tree = ET.parse(file)
        root = tree.getroot()

        root.find("AuthenticationMethod").text = method
        root.find("AuthenticationRequired").text = "Enabled"
        tree.write(file)
    except FileNotFoundError:
        logging.warning("File %s is not initialized" % file)
        return 1
    except ET.ParseError:
        logging.warning("File %s is not initialized" % file)
        return 1
    else:
        return 0


def set_credential(database, username, password):
    # Create user in database
    adddata = ('652bf21b-fe69-47f7-8e52-80e0572a9025', username, password)
    addquery = "INSERT INTO Users (Identifier,Username,Password) VALUES(?, ?, ?)"
    updatedata = (username, password)
    updatequery = "UPDATE Users SET Password = ? WHERE Username = ?"

    try:
        connexion = sqlite3.connect(database)
        db = connexion.cursor()

        db.execute("CREATE TABLE Users (Id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, Identifier TEXT NOT NULL, Username TEXT NOT NULL, Password TEXT NOT NULL, Salt TEXT, Iterations INTEGER)")
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
    logging.info("Get environment variable")
    PROWLARR_USER = os.environ.get('PROWLARR_USER')
    PROWLARR_PASSWORD = os.environ.get('PROWLARR_PASSWORD')
    PROWLARR_APIKEY = os.environ.get('PROWLARR_APIKEY')

    logging.info("Set Credential to application for user %s ..." % PROWLARR_USER)
    set_credential(PROWLARR_DB, PROWLARR_USER, PROWLARR_PASSWORD)
    set_authenticationmethod(CONFIG_FILE, "Forms")
