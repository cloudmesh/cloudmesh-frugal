import requests
import numpy as np
from cloudmesh.common.console import Console
from cloudmesh.frugal.api import helpers
import pandas as pd


############
# GOOGLE###
############

def get_google_pricing(refresh=False):
    # connect to cm db and check for Google info

    from pathlib import Path
    path = str(Path.home())+('/cm/cloudmesh-frugal/cloudmesh/frugal/gcp-data')
    from os import listdir
    from os.path import isfile, join
    data_dir = [f for f in listdir(path) if isfile(join(path, f))]

    # if googleinfo.estimated_document_count() > 0 and not refresh:
    #     Console.msg(f"Using local db gcp flavors...")
    #     return googleinfo
    if refresh:
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


        flavor_frame = pd.DataFrame(googleinfo)[
            ['provider', 'machine-name', 'location', 'cores', 'core/price',
             'memory', 'memory/price', 'price']]
        flavor_frame.to_csv(join(path, 'gcp.csv'))
    else:
        flavor_frame = pd.read_csv(join(path, 'gcp.csv'))


    return flavor_frame
