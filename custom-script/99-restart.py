#!/usr/bin/python3
import requests
import os
import logging

###########################################################
# SET STATIC CONFIG
###########################################################
logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)
PROWLARR_URL = 'http://localhost:9696'


###########################################################
# DEFINE FUNCTION
###########################################################
def restart(url, apikey):
    api_url = url + "/api/v3/system/restart"
    api_header = {'accept': '*/*', 'X-Api-Key': apikey}

    try:
        response = requests.post(api_url, headers=api_header)
        response.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        logging.error(errh)
    except requests.exceptions.ConnectionError as errc:
        logging.error(errc)
    except requests.exceptions.Timeout as errt:
        logging.error(errt)
    except requests.exceptions.RequestException as err:
        logging.error(err)

    return response.status_code


###########################################################
# INIT CONFIG
###########################################################
if __name__ == '__main__':
    PROWLARR_APIKEY = os.environ.get('PROWLARR_APIKEY')

    logging.info("Restart application %s ..." % PROWLARR_URL)
    restart(PROWLARR_URL, PROWLARR_APIKEY)
