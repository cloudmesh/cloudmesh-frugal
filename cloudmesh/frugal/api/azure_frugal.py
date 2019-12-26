import requests
import numpy as np
from cloudmesh.mongo.CmDatabase import CmDatabase
from cloudmesh.compute.azure import Provider as azureprv
from cloudmesh.common.console import Console
from datetime import datetime
from cloudmesh.frugal.api import helpers

###########
# AZURE###
###########

# dictionary to convert regions from flavors to pricing...Microsoft is
# inconsistent...
location_conv_dict = {
    'eastasia': 'asia-pacific-east',
    'southeastasia': 'asia-pacific-southeast',
    'centralus': 'us-central',
    'eastus': 'us-east',
    'eastus2': 'us-east-2',
    'westus': 'us-west',
    'northcentralus': 'us-north-central',
    'southcentralus': 'us-south-central',
    'northeurope': 'europe-north',
    'westeurope': 'europe-west',
    'japanwest': 'japan-west',
    'japaneast': 'japan-east',
    'brazilsouth': 'brazil-south',
    'australiaeast': 'australia-east',
    'australiasoutheast': 'australia-southeast',
    'southindia': 'south-india',
    'centralindia': 'central-india',
    'westindia': 'west-india',
    'canadacentral': 'canada-central',
    'canadaeast': 'canada-east',
    'uksouth': 'united-kingdom-south',
    'ukwest': 'united-kingdom-west',
    'westcentralus': 'us-west-central',
    'westus2': 'us-west-2',
    'koreacentral': 'korea-central',
    'koreasouth': 'korea-south',
    'francecentral': 'france-central',
    'francesouth': 'france-south',
    'australiacentral': 'australia-central',
    'australiacentral2': 'australia-central-2',
    'uaecentral': 'uae-central',
    'uaenorth': 'uae-north',
    'southafricanorth': 'south-africa-north',
    'southafricawest': 'south-africa-west',
    'switzerlandnorth': 'switzerland-north',
    'switzerlandwest': 'switzerland-west',
    'germanynorth': 'germany-north',
    'germanywestcentral': 'germany-west-central',
    'norwaywest': 'norway-west',
    'norwayeast': 'norway-east'
}


def get_azure_pricing(refresh=False):
    cm = CmDatabase()
    azureinfo = cm.collection('azure-frugal')

    # check to see if azure-frugal already exists in db
    if azureinfo.estimated_document_count() > 0 and not refresh:
        Console.msg(f"Using local db azure flavors...")
        return azureinfo

    # get local db azure flavors (empty if it does not exist yet)
    azureinfo = cm.collection('azure-flavor')

    # create provider to get region
    try:
        azureprovider = azureprv.Provider(
            name='azure',
            configuration="~/.cloudmesh/cloudmesh.yaml")
    except:
        Console.msg("No azure credentials")
        return
    region = azureprovider.LOCATION
    priceregion = location_conv_dict[region]

    if azureinfo.estimated_document_count() == 0 or refresh:
        # use provider to fetch info
        Console.msg(f"Pulling azure flavors...")
        azureinfo = azureprovider.flavors()
    else:
        # use local, just turn it into a list for matching iteration use
        azureinfo = list(azureinfo.find())

    # get pricing and limit to what is needed
    Console.msg(f"Pulling azure flavor price information...")
    pricing = requests.get(
        'https://azure.microsoft.com/api/v3/pricing/virtual-machines/calculator/?culture=en-us&discount=mosp&v=20191002-1500-96990').json()
    offers = pricing['offers']
    modoffers = {}
    for key, val in offers.items():
        newkey = key.replace('_', '').replace('-', '')
        modoffers[newkey] = val

    azure_list = []
    for flavor in azureinfo:
        key = flavor['name'].lower()
        if key[0] is 'b':
            # basic
            search = 'linux' + key[6:].replace('_', '').replace('-',
                                                                '').replace(
                'promo', '') + 'basic'
        elif key[0] is 's':
            # standard
            search = 'linux' + key[9:].replace('_', '').replace('-',
                                                                '').replace(
                'promo', '') + 'standard'
        elif key[0] is 'l':
            # low_priority
            search = 'linux' + key[13:].replace('_', '').replace('-',
                                                                 '').replace(
                'promo', '') + 'standard'
        else:
            print('no matches on key')
            continue
        try:
            found = modoffers[search]
        except:
            # print('machine match failure on ' + search)
            continue
        # now to fit it into the frame
        azure_list.append(np.array(
            ['azure', flavor['name'], region, found['cores'], found['ram'],
             found['prices']['perhour'][priceregion]['value']]))

    azureinfo = np.stack(azure_list, axis=0)
    azureinfo = helpers.format_mat(azureinfo)

    # convert to list of dicts
    azureinfo = azureinfo.to_dict('records')

    # write back to cm db
    for entry in azureinfo:
        entry["cm"] = {
            "kind": 'frugal',
            "driver": 'azure',
            "cloud": 'azure',
            "name": str(entry['machine-name'] + '-' + entry['location']),
            "updated": str(datetime.utcnow()),
        }

    Console.msg(f"Writing back to db ...")
    cm.update(azureinfo)

    return cm.collection('azure-frugal')
