import numpy as np
from datetime import datetime
from cloudmesh.mongo.CmDatabase import CmDatabase
from cloudmesh.aws.compute import Provider as awsprv
from cloudmesh.common.console import Console
from cloudmesh.frugal.api import helpers


#########
# AWS
#########

def get_aws_pricing(refresh=False):
    # connect to the db
    cm = CmDatabase()

    # check to see if AWS frugal entries already exist
    awsinfo = cm.collection('aws-frugal')

    if awsinfo.estimated_document_count() > 0 and not refresh:
        # frugal information alredy exists, so return it
        Console.msg(f"Using local db aws flavors...")
        return awsinfo

    # helper function to parse aws info
    def aws_parse(input):
        if ('location' not in x['attributes'] or 'vcpu' not in x[
            'attributes'] or 'price' not in x or x['attributes'][
            'memory'] == 'NA'):
            return
        return np.array(['aws', x['sku'], x['attributes']['location'],
                         float(x['attributes']['vcpu']),
                         float(x['attributes']['memory'][:-4].replace(',', '')),
                         float(x['price']['pricePerUnit']['USD'])])

    # check to see if general flavor entries exist
    awsinfo = cm.collection('aws-flavor')
    aws_list = []

    if awsinfo.estimated_document_count() > 0 and not refresh:
        # can get info directly from db, just need to reshape
        Console.msg(f"Calculating with local db aws flavors...")
        for x in awsinfo.find():
            tempray = aws_parse(x)
            if tempray is not None:
                aws_list.append(aws_parse(x))

    else:
        Console.msg(f"refreshing aws flavors in now ...")
        try:
            awsprovider = awsprv.Provider(
                name='aws',
                configuration="~/.cloudmesh/cloudmesh.yaml")
        except:
            Console.msg("No aws credentials")
            return
        awsinfo = awsprovider.flavors()
        for x in awsinfo:
            tempray = aws_parse(x)
            if tempray is not None:
                aws_list.append(aws_parse(x))

    awsinfo = np.stack(aws_list, axis=0)
    awsinfo = helpers.format_mat(awsinfo)

    # convert to list of dicts
    awsinfo = awsinfo.to_dict('records')

    # write back to cm db
    for entry in awsinfo:
        entry["cm"] = {
            "kind": 'frugal',
            "driver": 'aws',
            "cloud": 'aws',
            "name": str(entry['machine-name'] + '-' + entry['location']),
            "updated": str(datetime.utcnow()),
        }

    Console.msg(f"Writing back to db ...")
    cm.update(awsinfo, progress=True)

    return cm.collection('aws-frugal')
