import requests
import numpy as np
from datetime import datetime
from cloudmesh.mongo.CmDatabase import CmDatabase
from cloudmesh.common.console import Console
from cloudmesh.frugal.api import helpers


############
# GOOGLE###
############

def get_google_pricing(refresh=False):
    # connect to cm db and check for Google info
    cm = CmDatabase()
    googleinfo = cm.collection('gcp-frugal')

    if googleinfo.estimated_document_count() > 0 and not refresh:
        Console.msg(f"Using local db gcp flavors...")
        return googleinfo
    else:
        Console.msg(f"Pulling gcp flavor price information...")
        googleinfo = requests.get(
            'https://cloudpricingcalculator.appspot.com/static/data/pricelist.json?v=1570117883807').json()[
            'gcp_price_list']
        google_list = []
        for machine, locations in googleinfo.items():
            if type(
                locations) is dict and 'cores' in locations and 'memory' in locations:
                cores = locations['cores']
                if cores == 'shared':
                    continue
                memory = locations['memory']
                for location in locations:
                    # 'cores' is end of regions, so stop if found
                    if location == 'cores':
                        break
                    else:
                        if type(locations[location]) is str:
                            print(locations[location])
                        google_list.append(np.array(
                            ['gcp', machine, location, float(cores),
                             float(memory), float(locations[location])]))
        googleinforeturn = np.stack(google_list, axis=0)

    googleinfo = np.stack(googleinforeturn, axis=0)
    googleinfo = helpers.format_mat(googleinfo)

    # convert to list of dicts
    googleinfo = googleinfo.to_dict('records')

    # write back to cm db
    for entry in googleinfo:
        entry["cm"] = {
            "kind": 'frugal',
            "driver": 'gcp',
            "cloud": 'gcp',
            "name": str(entry['machine-name'] + '-' + entry['location']),
            "updated": str(datetime.utcnow()),
        }

    Console.msg(f"Writing back to db ...")
    cm.update(googleinfo, progress=True)

    return cm.collection('gcp-frugal')
