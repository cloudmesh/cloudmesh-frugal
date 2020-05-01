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


class FrugalCommand(PluginCommand):

    # noinspection PyUnusedLocal
    @command
    def do_frugal(self, args, arguments):
        """
        ::

            Usage:
                frugal list [--benchmark] [--refresh] [--order=ORDER] [--size=SIZE] [--cloud=CLOUD]
                frugal boot [--refresh] [--order=ORDER] [--cloud=CLOUD]
                frugal benchmark
                frugal storage
                frugal gui

            Arguments:
              ORDER       sorting hierarchy, either price, cores, or
                          memory
              SIZE        number of results to be printed to the
                          console. Default is 25, can be changed with
                          cms set frugal.size = SIZE
              CLOUD       Limits the frugal method to a specific cloud
                          instead of all supported providers

            Options:
               --refresh         forces a refresh on all entries for
                                 all supported providers
               --order=ORDER     sets the sorting on the results list
               --size=SIZE       sets the number of results returned
                                 to the console
               --benchmark       prints the benchmark results instead
                                 of flavors

            Description:
                frugal list
                    lists cheapest flavors for aws, azure, and gcp
                    in a sorted table by default, if --benchmark is
                    used then it lists benchmark results stored in
                    the db

                frugal boot
                    boots the cheapest bootable vm from the frugal
                    list.

                frugal benchmark
                    executes a benchmarking command on the newest
                    available vm on the current cloud

            Examples:


                 cms frugal list --refresh --order=price --size=150
                 cms frugal list --benchmark
                 cms frugal boot --order=memory
                 cms frugal benchmark

                 ...and so on

            Tips:
                frugal benchmark will stall the command line after
                the user enters their ssh key. This means the benchmark
                is running


            Limitations:

                frugal boot and benchmark only work on implemented providers



        """
        arguments.REFRESH = arguments['--refresh'] or None
        arguments.SIZE = arguments['--size'] or None
        arguments.ORDER = arguments['--order'] or None
        arguments.BENCHMARK = arguments['--benchmark'] or None
        arguments.CLOUD = arguments['--cloud'] or None

        var_list = Variables(filename="~/.cloudmesh/cms burn")
        if var_list['frugal.size'] is None:
            var_list['frugal.size'] = 25
        var_size = var_list['frugal.size']

        if arguments.ORDER is None:
            arguments.ORDER = 'price'

        if arguments.REFRESH is None:
            arguments.REFRESH = False
        else:
            arguments.REFRESH = True

        if arguments.BENCHMARK is None:
            arguments.BENCHMARK = False
        else:
            arguments.BENCHMARK = True

        if arguments.SIZE is None:
            arguments.SIZE = var_size

        if arguments.list:
            self.list(order=arguments.ORDER, refresh=bool(arguments.REFRESH),
                      resultssize=int(arguments.SIZE),
                      benchmark=arguments.BENCHMARK, cloud=arguments.CLOUD)
        elif arguments.boot:
            self.boot(order=arguments.ORDER, refresh=bool(arguments.REFRESH),
                      cloud=arguments.CLOUD)
        elif arguments.storage:
            self.storage()
        else:
            return ""

        return ""



    def list(self, order='price', resultssize=25, refresh=False, printit=True,
             benchmark=False, cloud=None):

        clouds = ['aws', 'azure', 'gcp']
        if cloud in clouds:
            clouds = [cloud]

        if benchmark:
            # get benchmarks
            cm = CmDatabase()
            benchmarks = []
            for cloud in clouds:
                print("searching " + cloud)
                benchmarktemp = list(
                    cm.collection(cloud + '-frugal-benchmark').find())
                benchmarks = benchmarks + benchmarktemp

            print(Printer.write(benchmarks,
                                order=['cloud', 'name', 'region', 'ImageId',
                                       'flavor', 'updated', 'BenchmarkTime']))
            return
        else:
            # check to make sure that order is either price, cores, or memory
            if order not in ['price', 'cores', 'memory']:
                Console.error(f'order argument must be price, cores, or memory')
                return

            printlist = []

            if 'aws' in clouds:
                # get aws pricing info
                awsframe = aws_frugal.get_aws_pricing(refresh=refresh)
                if awsframe is not None:
                    printlist = printlist + list(awsframe.find())

            if 'gcp' in clouds:
                # get gcp pricing info
                gcpframe = gcp_frugal.get_google_pricing(refresh=refresh)
                if gcpframe is not None:
                    printlist = printlist + list(gcpframe.find())

            # if 'azure' in clouds:
            #     # get azure pricing info
            #     azureframe = azure_frugal.get_azure_pricing(refresh=refresh)
            #     if azureframe is not None:
            #         printlist = printlist + list(azureframe.find())

            if len(printlist) == 0:
                Console.error('no flavors available...')
                return

            # turn numpy array into a pandas dataframe, assign column names,
            # and remove na values
            flavor_frame = pd.DataFrame(printlist)[
                ['provider', 'machine-name', 'location', 'cores', 'core/price',
                 'memory', 'memory/price', 'price']]
            flavor_frame = flavor_frame.replace([np.inf, -np.inf],
                                                np.nan).dropna()

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

            # print out the dataframe if printit, print results limited by
            # resultssize
            if printit:
                print(Printer.write(
                    flavor_frame.head(resultssize).to_dict('records'),
                    order=['provider', 'machine-name', 'location', 'cores',
                           'core/price', 'memory',

                           'memory/price', 'price']))
            # return the final sorted data frame
            return flavor_frame

    def boot(self, order='price', refresh=False, cloud=None):
        # clouds = ['aws', 'azure', 'gcp']
        # if cloud in clouds:
        #     clouds = [cloud]
        #
        # Console.msg(f"Checking to see which providers are bootable ...")
        # reachdict = {}
        #
        # for cloudoption in clouds:
        #     try:
        #         tempProv = Provider(name=cloudoption,
        #                             configuration="~/.cloudmesh/cloudmesh.yaml")
        #         Console.msg(cloudoption + " reachable ...")
        #         reachdict[cloudoption] = tempProv
        #     except:
        #         Console.msg(cloudoption + " not available ...")
        #
        # flavorframe = self.list(order, 10000000, refresh, printit=False,
        #                         cloud=clouds)
        # if flavorframe is None:
        #     Console.error("cannot boot vm, check credentials")
        #     return
        # keysya = list(reachdict.keys())
        # flavorframe = flavorframe[flavorframe['provider'].isin(keysya)]
        # Console.msg(f"Showing top 5 options, booting first option now...")
        # print(flavorframe.head(5))
        # converted = flavorframe.head(5).to_dict('records')
        # print(Printer.write(converted))
        # cheapest = converted[0]
        # var_list = Variables(filename="~/.cloudmesh/cms burn")
        # var_list['cloud'] = cheapest['provider']
        # Console.msg(f'new cloud is ' + var_list[
        #     'cloud'] + ', booting up the vm with flavor ' + cheapest[
        #                 'machine-name'])
        # vmcom = VmCommand()
        # vmcom.do_vm('boot --flavor=' + cheapest['machine-name'])
        # return ""
        raise NotImplemented


    def storage(self):

        gui.theme('SystemDefault1')

        gui_enabled = True
        layout = [[gui.Text(text='Storage Type', size=(30,1))],
                  [gui.Combo(['Standard', 'Infrequent', 'Coldline', 'Archive'])],
                  [gui.Frame(layout=[
                      [gui.Checkbox('AWS', size=(10, 1)), gui.Checkbox('GCP', default=False)]], title='Cloud Platform',
                      relief=gui.RELIEF_FLAT, tooltip='Use these to set Clouds to Search')],
                  [gui.Frame(layout=[
                      [gui.Checkbox('US East', size=(10, 1)), gui.Checkbox('US Central', default=False),
                       gui.Checkbox('US West', size=(10, 1))]], title='Cloud Platform',
                      relief=gui.RELIEF_FLAT, tooltip='Use these to set Clouds to Search')],
                  [gui.Button('Ok'), gui.Button('Cancel')]]
        window = gui.Window('Cloud Storage Price Comparison', layout)
        while True:
            event, values = window.read()
            if event in (None, 'Cancel'):  # if user closes window or clicks cancel
                break
            elif event in('Ok'):
                storage_type = values
                break
        clouds=[]
        locations=[]
        cloud_dict={1:'aws', 2:'gcp'}
        loc_dict={3:'US East', 4:'US Central', 5:'US West'}
        for i in [1,2]:
            if values[i]:
                clouds.append(cloud_dict[i])
        for i in range(3, len(values)):
            if values[i]:
                locations.append(loc_dict[i])
        window.close()
        print('Searching for', values[0], ' storage in', ", ".join([str(item) for item in clouds]))
        list = storage.get_storage_pricing(values[0], clouds, locations)
        if values[0] != 'Archive':
            print(Printer.write(list.to_dict('records'),order=['Cloud', 'Name', 'Storage Class', 'PricePerUnit', 'Unit', 'StartingRange', 'EndingRange',
                     'Location', 'Location Code']))
