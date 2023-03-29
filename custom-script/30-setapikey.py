#!/usr/bin/python3
import os
import logging
import xml.etree.ElementTree as ET

###########################################################
# SET STATIC CONFIG
###########################################################
logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)
CONFIG_FILE = '/config/config.xml'


###########################################################
# DEFINE FUNCTION
###########################################################
def get_apikey(file):
    # Get ApiKey from xml config files
    try:
        tree = ET.parse(file)
        root = tree.getroot()
        apikey = root.find("ApiKey")

        if apikey is None:
            raise ValueError
    except ValueError:
        logging.warning("ApiKey not found in %s" % file)
        return None
    except FileNotFoundError:
        logging.warning("File %s is not initialized" % file)
        return None
    except ET.ParseError:
        logging.warning("File %s is not initialized" % file)
        return None
    else:
        return apikey.text


def set_apikey(file, apikey):
    # Set ApiKey to xml config files
    try:
        tree = ET.parse(file)
        root = tree.getroot()

        root.find("ApiKey").text = apikey
        tree.write(file)
    except FileNotFoundError:
        logging.warning("File %s is not initialized" % file)
        return 1
    except ET.ParseError:
        logging.warning("File %s is not initialized" % file)
        return 1
    else:
        return 0


###########################################################
# INIT CONFIG
###########################################################
if __name__ == '__main__':
    PROWLARR_APIKEY = os.environ.get('PROWLARR_APIKEY')

    logging.info("Set apikey to application ...")
    set_apikey(CONFIG_FILE, PROWLARR_APIKEY)
