import pandas as pd
import requests
import io
import os
#########
# AWS
#########

def get_aws_pricing(regions, refresh =False):

    from pathlib import Path
    path = str(Path.home())+('/cm/cloudmesh-frugal/cloudmesh/frugal/aws-data')
    from os import listdir
    from os.path import isfile, join
    data_dir = [f for f in listdir(path) if isfile(join(path, f))]

    if refresh:
        for loc in regions:
            comp = "https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonEC2/current/{}/index.csv".format(loc)
            s = requests.get(comp).content
            ec2 = pd.read_csv(io.StringIO(s.decode('utf-8')), skiprows=lambda x: x in [0, 4], header=3)
            AWStemp= ec2[['SKU','vCPU','Memory','PricePerUnit']]
            del ec2
            AWStemp = AWStemp.dropna(axis=0)
            AWStemp=AWStemp.rename(columns={'SKU':'machine-name', 'vCPU':'cores', 'PricePerUnit':'price', 'Memory': 'memory'})
            AWStemp['location'] = loc
            AWStemp['memory'] = AWStemp['memory'].str.replace(r'\D', '').astype(int)
            AWStemp['core/price'] = AWStemp['cores']/AWStemp['price']
            AWStemp['memory/price'] = AWStemp['memory'] / AWStemp['price']

            AWStemp['provider'] = 'aws'
            columnsTitles = ['provider','machine-name','location','cores','core/price','memory','memory/price','price']
            AWStemp = AWStemp.reindex(columns=columnsTitles)
            AWStemp.to_csv(join(path,'{}.csv'.format(loc)))
            try:
                AWS = pd.concat([AWS, AWStemp])
            except NameError:
                AWS = AWStemp
    else:
        for loc in regions:
            if '{}.csv'.format(loc) not in data_dir:
                get_aws_pricing(refresh=True, regions=[loc])
            AWStemp=pd.read_csv(join(path,'{}.csv'.format(loc)))
            try:
                AWS = pd.concat([AWS, AWStemp])
            except NameError:
                AWS = AWStemp
    return AWS
