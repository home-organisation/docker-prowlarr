#!/usr/bin/python3
import os
import logging
import sqlite3

###########################################################
# SET STATIC CONFIG
###########################################################
logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)
PROWLARR_DB = 'config/prowlarr.db'


###########################################################
# DEFINE FUNCTION
###########################################################
def restart():
    os.popen('s6-svc -r /var/run/s6-rc/servicedirs/svc-prowlarr/')


def reset_task(database):
    query = "UPDATE ScheduledTasks SET LastExecution = '0001-01-01 00:00:00Z', LastStartTime = null " \
            "WHERE TypeName = 'NzbDrone.Core.Applications.ApplicationIndexerSyncCommand'"

    connexion = sqlite3.connect(database)
    db = connexion.cursor()

    try:
        db.execute(query)
        connexion.commit()

        db.close()
        connexion.close()
    except sqlite3.Error as er:
        logging.error('SQLite error: %s' % (' '.join(er.args)))
        return None
    else:
        return True


###########################################################
# INIT CONFIG
###########################################################
if __name__ == '__main__':
    logging.info("Restart application ...")
    reset_task(PROWLARR_DB)
    restart()
