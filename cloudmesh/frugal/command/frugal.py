from __future__ import print_function
from cloudmesh.shell.command import command
from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.shell import Shell
from cloudmesh.common.console import Console
from cloudmesh.compute.vm.Provider import Provider
import pandas as pd
import numpy as np
from cloudmesh.common.Printer import Printer
from cloudmesh.frugal.api import aws_frugal, gcp_frugal, azure_frugal, storage
from datetime import datetime
from cloudmesh.common.variables import Variables
from cloudmesh.vm.command.vm import VmCommand
from cloudmesh.mongo.CmDatabase import CmDatabase
from os import path
import PySimpleGUI as gui
from time import time


class FrugalCommand(PluginCommand):

    # noinspection PyUnusedLocal
    @command
    def do_frugal(self, args, arguments):
        """
        ::

            Usage:
                frugal compute [--refresh] [--order=ORDER] [--size=SIZE] [--cloud=CLOUD] [--region=REGION] [--benchmark] [--output=FORMAT]
                frugal storage [--type=TYPE] [--region=REGION] [--cloud=CLOUD] [--benchmark] [--output=FORMAT]
                frugal gui [--benchmark]

            Arguments:
              ORDER       sorting hierarchy, either price, cores, or
                          memory
              SIZE        number of results to be printed to the
                          console. Default is 25, can be changed with
                          cms set frugal.size = SIZE
              CLOUD       Limits the frugal method to a specific cloud
                          instead of all supported providers. Works with AWS and GCP
              REGION      Limits the frugal method to a specific region

              TYPE        Storage type for frugal storage. Options include
                          standard, nearline, coldline and archive. These
                          types are determine by the intended access frequency

            Options:
               --refresh         forces a refresh on all entries for
                                 all supported providers
               --order=ORDER     sets the sorting on the results list
               --size=SIZE       sets the number of results returned
                                 to the console
               --output=FORMAT   Output format such as csv, json, table
                                 [default: table]


            Description:
                frugal compute
                    lists cheapest flavors of compute instances for aws and gcp
                    in a sorted table by default

                frugal storage
                    lists cheapest instances of object storage for aws and gcp
                    in a sorted table by default

                frugal gui
                    graphical interface for both compute and storage fuctions.

            Examples:

            Tips:
                frugal gui provides lists the available options for regions and types of storage


            Limitations:

                frugal benchmark only work on implemented providers



        """
        arguments.OUTPUT = arguments['--output'] or None
        arguments.REFRESH = arguments['--refresh'] or None
        arguments.SIZE = arguments['--size'] or None
        arguments.ORDER = arguments['--order'] or None
        arguments.CLOUD = arguments['--cloud'] or None
        arguments.TYPE = arguments['--type'] or None
        arguments.REGION= arguments['--region'] or None
        arguments.BENCHMARK= arguments['--benchmark'] or None
        var_list = Variables(filename="~/.cloudmesh/cms burn")
        if var_list['frugal.size'] is None:
            var_list['frugal.size'] = 25
        var_size = var_list['frugal.size']
        if arguments.OUTPUT is None:
            arguments.OUTPUT = 'table'
        if arguments.TYPE is None:
            arguments.TYPE = 'Standard'
        if arguments.REGION is None:
            arguments.REGION = ['US_East', 'US_Central', 'US_West', 'UK', 'Europe', 'Asia', 'Australia', 'Africa', 'S_America']
        else:
            arguments.REGION = [arguments.REGION]
        if arguments.ORDER is None:
            arguments.ORDER = 'price'

        if arguments.REFRESH is None:
            arguments.REFRESH = False
        else:
            arguments.REFRESH = True
        if arguments.BENCHMARK is None:
            arguments.BENCHMARK=False
        else:
            arguments.BENCHMARK=True
        if arguments.SIZE is None:
            arguments.SIZE = var_size

        if arguments.compute:
            self.list(order=arguments.ORDER, refresh=bool(arguments.REFRESH),
                      resultssize=int(arguments.SIZE), cloud=arguments.CLOUD,
                      region=arguments.REGION, benchmark=arguments.BENCHMARK,
                      output=arguments.OUTPUT)
        # elif arguments.boot:
        #     self.boot(order=arguments.ORDER, refresh=bool(arguments.REFRESH),cloud=arguments.CLOUD,
        #               region=arguments.REGION, benchmark=arguments.BENCHMARKD)
        elif arguments.storage:
            self.storage(type=arguments.TYPE, regions=arguments.REGION, cloud=arguments.CLOUD,
                         benchmark=arguments.BENCHMARK, output=arguments.OUTPUT)

        elif arguments.gui:
            self.gui()
        else:
            return ""

        return ""



    def list(self, region, order='price', resultssize=25, refresh=False, printit=True, cloud=None, benchmark=False, output='table'):
        if benchmark:
            t = time()
        locdict = {'US_East': {'gcp': ['us-east1', 'us-east4', 'northamerica-northeast1'],
                               'aws': ['us-east-1']},
                   'US_Central': {'gcp': ['us-central1'],
                                  'aws': ['us-east-2']},
                   'US_West': {'gcp': ['us-west1', 'us-west2', 'us-west3', 'us-west4'],
                               'aws': ['us-west-1', 'us-west-2']},
                   'UK': {'gcp': ['europe-west1'],
                          'aws': ['eu-west-2', 'eu-west-1']},
                   'Europe': {'gcp': ['europe-north1', 'europe-west1', 'europe-west4', 'europe-west3', 'europe-west6'],
                              'aws': ['eu-south-1', 'eu-west-3', 'eu-north-1', 'eu-central-1']},
                   'Asia': {'gcp': ['asia-east1', 'asia-east2', 'asia-northeast1', 'asia-northeast2', 'asia-northeast3',
                                    'asia-south1', 'asia-southeast1'],
                            'aws': ['ap-east-1', 'ap-south-1', 'ap-northeast-3', 'ap-northeast-2', 'ap-southeast-1',
                                    'ap-southeast-2', 'ap-northeast-1', 'me-south-1']},
                   'Australia': {'gcp': ['australia-southeast'],
                                 'aws': ['ap-southeast-2']},
                   'Africa': {'gcp': [],
                              'aws': ['af-south-1']},
                   'S_America': {'gcp': ['southamerica-east1'],
                                  'aws': ['sa-east-1', 'ca-central-1']}
                   }
        clouds = ['aws', 'azure', 'gcp']
        if cloud in clouds:
            clouds = [cloud]


            # check to make sure that order is either price, cores, or memory
        if order not in ['price', 'cores', 'memory']:
            Console.error(f'order argument must be price, cores, or memory')
            return

        printlist = []

        locs = []
        for loc in region:

            for i in locdict[loc]['aws']:
                locs.append(i)

        if 'aws' in clouds:
            # get aws pricing info
            awsframe = aws_frugal.get_aws_pricing(regions=locs, refresh=refresh)


        for loc in region:

            for i in locdict[loc]['gcp']:
                locs.append(i)
        if 'gcp' in clouds:
            # get gcp pricing info
            gcpframe = gcp_frugal.get_google_pricing(refresh=refresh)
            if gcpframe is not None:
                printlist = printlist + list(gcpframe.find())
            flavor_frame = pd.DataFrame(printlist)[
                ['provider', 'machine-name', 'location', 'cores', 'core/price',
                 'memory', 'memory/price', 'price']]

        if 'aws' in clouds and 'gcp' in clouds:
            flavor_frame= pd.concat([awsframe, flavor_frame])
        elif 'gcp' in clouds:
            flavor_frame=flavor_frame
        else:
            flavor_frame=awsframe
        flavor_frame = flavor_frame.replace([np.inf, -np.inf], np.nan).dropna()

        # sort the dataframe by order
        if order == 'cores':
            flavor_frame = flavor_frame.sort_values(by=['core/price'],
                                                    ascending=False)
        elif order == 'memory':
            flavor_frame = flavor_frame.sort_values(by=['memory/price'],
                                                    ascending=False)
        else:
            flavor_frame = flavor_frame.sort_values(by=['price'],
                                                    ascending=True)
        flavor_frame=flavor_frame[flavor_frame['location'].isin(locs)]

        # print out the dataframe if printit, print results limited by
        # resultssize
        if benchmark:
            delta=time()-t
            print(delta)
            return delta

        if printit:
            print(Printer.write(
                flavor_frame.head(resultssize).to_dict('records'),
                order=['provider', 'machine-name', 'location', 'cores',
                       'core/price', 'memory',
                       'memory/price', 'price'], output=output))
        # return the final sorted data frame
        return flavor_frame

    def storage(self, type, regions, cloud, benchmark=False, output='table', resultssize=25):
        if benchmark:
            t= time()
        clouds = ['aws', 'gcp']
        if cloud in clouds:
            clouds = [cloud]
        if regions != None:
            region = regions
        else:
            regions = ['US_East', 'US_Central', 'US_West', 'UK', 'Europe', 'Asia', 'Australia', 'Africa', 'S_America']
        type =type if type else 'Standard'
        list = storage.get_storage_pricing(type, clouds, regions)
        if benchmark:
            delta= time()-t
            print(delta)
            return delta
        print(output)
        print(Printer.write(list.to_dict('records'),order=['Cloud', 'Name', 'Storage Class', 'PricePerUnit', 'Unit', 'StartingRange', 'EndingRange',
                 'Location', 'Location Code'], output=output))
        return list
    def gui(self):
        gui.theme('SystemDefault1')
        gui_enabled = True
        layout = [
            [gui.Radio('Compute', "RADIO1", default=True),
             gui.Radio('Storage', "RADIO1")],
            [gui.Button('Ok'), gui.Button('Cancel')]
        ]
        window = gui.Window('Price Comparison Selection', layout)
        while True:
            event, values = window.read()
            if event in (None, 'Cancel'):  # if user closes window or clicks cancel
                break

            elif event in('Ok'):
                window.close
                if values[1]:
                    layout = [[gui.Text(text='Storage Type', size=(30,1))],
                              [gui.Combo(['Standard', 'Infrequent', 'Coldline', 'Archive'])],
                              [gui.Frame(layout=[
                                  [gui.Checkbox('AWS', size=(10, 1)), gui.Checkbox('GCP', default=False)]], title='Cloud Platform',
                                  relief=gui.RELIEF_FLAT, tooltip='Use these to set Clouds to Search')],
                              [gui.Frame(layout=[
                                  [gui.Checkbox('US East', size=(10, 1)), gui.Checkbox('US Central', default=False),
                                   gui.Checkbox('US West', size=(10, 1))]], title='Region',
                                  relief=gui.RELIEF_FLAT, tooltip='Use these to set Clouds to Search')],
                              [gui.Frame(layout=[
                                  [gui.Checkbox('UK', size=(10, 1)),
                                   gui.Checkbox('Europe', size=(10, 1)),gui.Checkbox('Asia', size=(10, 1))]], title='',
                                  relief=gui.RELIEF_FLAT, tooltip='Use these to set Clouds to Search')],
                              [gui.Frame(layout=[
                                  [gui.Checkbox('Australia', size=(10, 1)), gui.Checkbox('Africa', default=False),
                                   gui.Checkbox('S. America', size=(10, 1))]], title='',
                                  relief=gui.RELIEF_FLAT, tooltip='Use these to set Clouds to Search')],
                              [gui.Button('Ok'), gui.Button('Cancel')]]
                    window1 = gui.Window('Cloud Storage Price Comparison', layout)
                    while True:
                        event, values = window1.read()
                        if event in (None, 'Cancel'):  # if user closes window or clicks cancel
                            break
                        elif event in('Ok'):
                            storage_type = values
                            break
                    clouds=[]
                    locations=[]
                    cloud_dict={1:'aws', 2:'gcp'}
                    loc_dict={3:'US_East', 4:'US_Central', 5:'US_West', 6:'UK', 7:'Europe', 8:'Asia', 9:'Australia', 10:'Africa', 11:'S_America'}
                    for i in [1,2]:
                        if values[i]:
                            clouds.append(cloud_dict[i])
                    for i in range(3, len(values)):
                        if values[i]:
                            locations.append(loc_dict[i])
                    window1.close()
                    print('Searching for', values[0], ' storage in', ", ".join([str(item) for item in clouds]))
                    list = storage.get_storage_pricing(values[0], clouds, locations)
                    # Uses the first row (which should be column names) as columns names
                    header_list = list.columns.tolist()
                    # Drops the first row in the table (otherwise the header names and the first row will be the same)
                    data = list.values.tolist()
                    layout = [
                        [gui.Table(values=data,
                                  headings=header_list,
                                  display_row_numbers=False,
                                  auto_size_columns=True,
                                  num_rows=min(25, len(data)))]
                    ]
                    window2 = gui.Window('Table', layout, grab_anywhere=False)
                    event, values = window2.read()
                    window2.close()
                    break
                if values[0]:
                    layout = [[gui.Text(text='Sort By', size=(30, 1))],
                              [gui.Combo(['price', 'cores', 'memory'])],
                              [gui.Frame(layout=[
                                  [gui.Checkbox('Refresh', size=(10, 1))]],
                                  title='Refresh List',
                                  relief=gui.RELIEF_FLAT, tooltip='Use this if you think your data is outdated.')],
                              [gui.Frame(layout=[
                                  [gui.Checkbox('AWS', size=(10, 1)), gui.Checkbox('GCP', default=False)]],
                                  title='Cloud Platform',
                                  relief=gui.RELIEF_FLAT, tooltip='Use these to set Clouds to Search')],
                              [gui.Frame(layout=[
                                  [gui.Checkbox('US East', size=(10, 1)), gui.Checkbox('US Central', default=False),
                                   gui.Checkbox('US West', size=(10, 1))]], title='Region',
                                  relief=gui.RELIEF_FLAT, tooltip='Use these to set Clouds to Search')],
                              [gui.Frame(layout=[
                                  [gui.Checkbox('UK', size=(10, 1)),
                                   gui.Checkbox('Europe', size=(10, 1)), gui.Checkbox('Asia', size=(10, 1))]], title='',
                                  relief=gui.RELIEF_FLAT, tooltip='Use these to set Clouds to Search')],
                              [gui.Frame(layout=[
                                  [gui.Checkbox('Australia', size=(10, 1)), gui.Checkbox('Africa', default=False),
                                   gui.Checkbox('S. America', size=(10, 1))]], title='',
                                  relief=gui.RELIEF_FLAT, tooltip='Use these to set Clouds to Search')],
                              [gui.Button('Ok'), gui.Button('Cancel')]]
                    window1 = gui.Window('Cloud Vompute Price Comparison', layout)
                    while True:
                        event, values = window1.read()
                        if event in (None, 'Cancel'):  # if user closes window or clicks cancel
                            break
                        elif event in ('Ok'):
                            storage_type = values
                            break
                    window1.close
                    # list=values
                    # print(list)
                    if values[2] and values[3]:
                        cloud=None
                    elif values[2]:
                        cloud= 'aws'
                    elif values[3]:
                        cloud = 'gcp'
                    loc_dict = {4: 'US_East', 5: 'US_Central', 6: 'US_West', 7: 'UK', 8: 'Europe', 9: 'Asia',
                                10: 'Australia', 11: 'Africa', 12: 'S_America'}
                    locations=[]
                    for i in range(4, len(values)):
                        if values[i]:
                            locations.append(loc_dict[i])
                    list= self.list(order=values[0], refresh=values[1] ,
                      resultssize=100, cloud=cloud, region=locations, printit=False)
                    # Uses the first row (which should be column names) as columns names
                    header_list = list.columns.tolist()
                    # Drops the first row in the table (otherwise the header names and the first row will be the same)
                    data = list.values.tolist()
                    layout = [
                        [gui.Table(values=data,
                                   headings=header_list,
                                   display_row_numbers=False,
                                   auto_size_columns=True,
                                   num_rows=min(25, len(data)))]
                    ]
                    window2 = gui.Window('Table', layout, grab_anywhere=False)
                    event, values = window2.read()
                    window2.close()
                    break

        return list
