import requests
import io
import pandas as pd
import numpy as np


def get_storage_pricing(tier, clouds, locations):
    aws_tiers={'Standard': {'class': 'AmazonS3'},
               'Infrequent': {'class': 'Infrequent Access'},
               'Coldline': {'class': 'Archive'},
               'Archive': {'class':'AWSStorageGatewayDeepArchive'}}
    gcp_tiers={'Standard':{'class':'CP-BIGSTORE-STORAGE'},
               'Infrequent': {'class': 'CP-NEARLINE-STORAGE'},
               'Coldline': {'class': 'CP-BIGSTORE-STORAGE-COLDLINE'},
               'Archive': {'class':'CP-BIGSTORE-STORAGE-ARCHIVE'}}
    gcp_locales={
        'asia-east1': 'Changhua County, Taiwan',
        'asia-east2': 'Hong Kong',
        'asia-northeast1': 'Tokyo, Japan',
        'asia-northeast2': 'Osaka, Japan',
        'asia-northeast3': 'Seoul, South Korea',
        'asia-south1': 'Mumbai, India',
        'asia-southeast1': 'Jurong West, Singapore',
        'australia-southeast': 'Sydney, Australia',
        'europe-north1': 'Hamina, Finland',
        'europe-west1': 'St. Ghislain, Belgium',
        'europe-west2': 'London, England, UK',
        'europe-west3': 'Frankfurt, Germany',
        'europe-west4': 'Eemshaven, Netherlands',
        'europe-west6': 'Zürich, Switzerland',
        'northamerica-northeast1': 'Montréal, Québec, Canada',
        'southamerica-east1': 'Osasco (São Paulo), Brazil',
        'us-central1': 'Council Bluffs, Iowa, USA',
        'us-east1': 'Moncks Corner, South Carolina, USA',
        'us-east4': 'Ashburn, Northern Virginia, USA',
        'us-west1': 'The Dalles, Oregon, USA',
        'us-west2': 'Los Angeles, California, USA',
        'us-west3': 'Salt Lake City, Utah, USA',
        'us-west4': 'Las Vegas, Nevada, USA'}

    aws_locales={
        'us-east-2': 'Ohio',
        'us-east-1': 'N. Virginia',
        'us-west-1': 'N. California',
        'us-west-2': 'Oregon',
        'af-south-1': 'Cape Town',
        'ap-east-1': 'Hong Kong',
        'ap-south-1': 'Mumbai',
        'ap-northeast-3': 'Osaka-Local',
        'ap-northeast-2': 'Seoul',
        'ap-southeast-1': 'Singapore',
        'ap-southeast-2': 'Sydney',
        'ap-northeast-1': 'Tokyo',
        'ca-central-1': 'Central',
        'eu-central-1': 'Frankfurt',
        'eu-west-1': 'Ireland',
        'eu-west-2': 'London',
        'eu-south-1': 'Milan',
        'eu-west-3': 'Paris',
        'eu-north-1': 'Stockholm',
        'me-south-1': 'Bahrain',
        'sa-east-1': 'São Paulo',
    }


    locdict={'US East':{'gcp':['us-east1','us-east4'],
                          'aws':['us-east-1']},
               'US Central':{'gcp':['us-central1'],
                             'aws':['us-east-2']},
               'US West': {'gcp':['us-west1','us-west2','us-west3','us-west4'],
                              'aws':['us-west-1','us-west-2']},
               }
    if 'aws' in clouds:
        for location in locations:
            for loc in locdict[location]['aws']:
                if tier == 'Archive':
                    stor = "https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AWSStorageGatewayDeepArchive/current/{}/index.csv".format(loc,loc)
                    s = requests.get(stor).content
                    s3 = pd.read_csv(io.StringIO(s.decode('utf-8')), skiprows=lambda x: x in [0, 4], header=3)
                    AWStemp=s3[['PricePerUnit', 'Fee Code']].T
                    AWStemp.columns = AWStemp.iloc[1]
                    AWStemp= AWStemp.drop(AWStemp.index[1])
                    AWStemp=AWStemp.rename(columns={np.nan:'Storage'})
                    AWStemp['Location Code']= loc
                    AWStemp['Location']=aws_locales[loc]

                else:
                    stor = "https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonS3/current/{}/index.csv".format(loc,loc)
                    s = requests.get(stor).content
                    s3 = pd.read_csv(io.StringIO(s.decode('utf-8')), skiprows=lambda x: x in [0, 4], header=3)
                    if tier == 'Standard':
                        AWStemp= s3[s3['Storage Class'].isin(['Non-Critical Data', 'General Purpose'])]
                        AWStemp= AWStemp[['SKU','Storage Class','StartingRange','EndingRange','Unit','PricePerUnit']]
                    else:
                        AWStemp= s3[s3['Storage Class']==aws_tiers[tier]['class']]
                        AWStemp = AWStemp[['SKU','Storage Class', 'StartingRange', 'EndingRange', 'Unit', 'PricePerUnit']]
                    AWStemp['Location Code']= loc
                    AWStemp['Location']=aws_locales[loc]
                    AWStemp['Cloud'] = 'AWS'
                    AWStemp = AWStemp.rename(columns={'SKU': 'Name'})
                    columnsTitles = ['Cloud', 'Name', 'Storage Class', 'PricePerUnit', 'Unit', 'StartingRange', 'EndingRange',
                                     'Location', 'Location Code']
                    AWStemp = AWStemp.reindex(columns=columnsTitles)
                try:
                    AWS= pd.concat([AWS,AWStemp])
                except NameError:
                    AWS=AWStemp



        try:
            storage=pd.concat([storage, AWS])
        except NameError:
            storage=AWS
    if 'gcp' in clouds:
        googleinfo = requests.get(
            'https://cloudpricingcalculator.appspot.com/static/data/pricelist.json?v=1570117883807').json()[
            'gcp_price_list']
        gcp = pd.DataFrame(googleinfo[gcp_tiers[tier]['class']], index=[0]).T
        gcp = gcp.reset_index()
        gcp=gcp.rename(columns={'index':'Location Code', 0:'PricePerUnit'})
        gcp['Location']= gcp['Location Code'].apply(lambda x: gcp_locales.get(x))
        gcp['StorageClass']= tier
        gcp['StartingRange']=0
        gcp['EndingRange']=np.inf
        gcp['Unit']= 'GB-Mo'
        locs= []
        for loc in locations:
            for i in locdict[loc]['gcp']:
                locs.append(i)
        gcp = gcp[gcp['Location Code'].isin(locs)]
        gcp['Name']= gcp['StorageClass']
        gcp['Cloud']= 'GCP'
        columnsTitles = ['Cloud', 'Name', 'Storage Class', 'PricePerUnit', 'Unit', 'StartingRange', 'EndingRange', 'Location', 'Location Code']
        gcp = gcp.reindex(columns=columnsTitles)
        try:
            storage=pd.concat([storage, gcp])
        except NameError:
            storage=gcp
    columnsTitles = ['Cloud', 'Name', 'Storage Class', 'PricePerUnit', 'Unit', 'StartingRange', 'EndingRange',
                     'Location', 'Location Code']
    storage = storage.reindex(columns=columnsTitles)
    return storage
'''
https://cloud.google.com/storage/pricing#operations-pricing
'''
'''
Currently the Azure does not support pulling prices for those without enterprise accounts. If you find that this has
changed, please contribute to this project. 
'''
    # if 'azure' in clouds:
    #     print('Cloudmesh does not currently support Azure, we are working to fix this issue')
    #     raise NotImplemented
