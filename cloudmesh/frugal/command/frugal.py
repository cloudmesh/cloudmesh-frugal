from __future__ import print_function
from cloudmesh.shell.command import command
from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.shell import Shell
from cloudmesh.common.console import Console
from cloudmesh.compute.vm.Provider import Provider
import pandas as pd
import numpy as np
from cloudmesh.common.Printer import Printer
from cloudmesh.frugal.api import aws_frugal, gcp_frugal, azure_frugal
from datetime import datetime
from cloudmesh.common.variables import Variables
from cloudmesh.vm.command.vm import VmCommand
from cloudmesh.mongo.CmDatabase import CmDatabase
from os import path

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

                frugal benchmark is dependent on the vm put command.
                this may need to be manually added to the vm command
                file.


            Limitations:

                frugal boot and benchmark only work on implemented providers



        """
        arguments.REFRESH = arguments['--refresh'] or None
        arguments.SIZE = arguments['--size'] or None
        arguments.ORDER = arguments['--order'] or None
        arguments.BENCHMARK = arguments['--benchmark'] or None
        arguments.CLOUD = arguments['--cloud'] or None

        var_list = Variables(filename="~/.cloudmesh/var-data")
        var_size = var_list['frugal.size']

        if arguments.ORDER is None:
            arguments.ORDER='price'

        if arguments.REFRESH is None:
            arguments.REFRESH=False
        else:
            arguments.REFRESH=True

        if arguments.BENCHMARK is None:
            arguments.BENCHMARK=False
        else:
            arguments.BENCHMARK=True

        if arguments.SIZE is None:
            arguments.SIZE=var_size


        if arguments.list:
            self.list(order = arguments.ORDER,refresh=bool(arguments.REFRESH), resultssize= int(arguments.SIZE), benchmark=arguments.BENCHMARK, cloud=arguments.CLOUD)
        elif arguments.boot:
            self.boot(order = arguments.ORDER,refresh=bool(arguments.REFRESH), cloud=arguments.CLOUD)
        elif arguments.benchmark:
            self.benchmark()
        else:
            return ""

        return ""

    def list(self,order='price', resultssize=25, refresh=False, printit = True, benchmark=False, cloud=None):

        clouds = ['aws', 'azure', 'gcp']
        if cloud in clouds:
            clouds = [cloud]

        if benchmark:
            # get benchmarks
            cm = CmDatabase();
            benchmarks = []
            for cloud in clouds:
                print("searching " + cloud)
                benchmarktemp = list(cm.collection(cloud + '-frugal-benchmark').find())
                benchmarks = benchmarks+benchmarktemp

            print(Printer.write(benchmarks, order=['cloud', 'name', 'region', 'ImageId', 'flavor', 'updated', 'BenchmarkTime']))
            return
        else:
            #check to make sure that order is either price, cores, or memory
            if order not in ['price', 'cores', 'memory']:
                Console.error(f'order argument must be price, cores, or memory')
                return

            printlist=[]

            if 'aws' in clouds:
                # get aws pricing info
                printlist = printlist + list(aws_frugal.get_aws_pricing(refresh=refresh).find())

            if 'gcp' in clouds:
                # get gcp pricing info
                printlist = printlist + list(gcp_frugal.get_google_pricing(refresh=refresh).find())

            if 'azure' in clouds:
                # get azure pricing info
                printlist = printlist + list(azure_frugal.get_azure_pricing(refresh=refresh).find())

            # turn numpy array into a pandas dataframe, assign column names, and remove na values
            flavor_frame = pd.DataFrame(printlist)[
                ['provider', 'machine-name', 'location', 'cores', 'core/price', 'memory', 'memory/price', 'price']]
            flavor_frame = flavor_frame.replace([np.inf, -np.inf], np.nan).dropna()

            # sort the dataframe by order
            if order == 'cores':
                flavor_frame = flavor_frame.sort_values(by=['core/price'], ascending=False)
            elif order == 'memory':
                flavor_frame = flavor_frame.sort_values(by=['memory/price'], ascending=False)
            else:
                flavor_frame = flavor_frame.sort_values(by=['price'], ascending=True)

            # print out the dataframe if printit, print results limited by resultssize
            if printit:
                print(Printer.write(flavor_frame.head(resultssize).to_dict('records'),
                                    order=['provider', 'machine-name', 'location', 'cores', 'core/price', 'memory',

                                           'memory/price', 'price']))
            # return the final sorted data frame
            return flavor_frame

    def boot(self,order='price', refresh=False, cloud=None):

        clouds = ['aws', 'azure', 'gcp']
        if cloud in clouds:
            clouds = [cloud]

        Console.msg(f"Checking to see which providers are bootable ...")
        reachdict = {}

        for cloud in clouds:
            try:
                tempProv = Provider(name=cloud, configuration="~/.cloudmesh/cloudmesh.yaml")
                Console.msg(cloud +" reachable ...")
                reachdict[cloud] = tempProv
            except:
                Console.msg(cloud + " not available ...")

        flavorframe = self.list(order, 10000000, refresh, printit=False)
        keysya = list(reachdict.keys())
        flavorframe = flavorframe[flavorframe['provider'].isin(keysya)]
        Console.msg(f"Showing top 5 options, booting first option now...")
        converted = flavorframe.head(5).to_dict('records')
        print(Printer.write(converted))
        cheapest = converted[0]
        var_list = Variables(filename="~/.cloudmesh/var-data")
        var_list['cloud'] = cheapest['provider']
        Console.msg(f'new cloud is ' + var_list['cloud'] + ', booting up the vm with flavor ' + cheapest['machine-name'])
        vmcom = VmCommand()
        vmcom.do_vm('boot --flavor=' + cheapest['machine-name'])
        return ""

    def benchmark(self):
        #get current cloud and create provider
        var_list = Variables(filename="~/.cloudmesh/var-data")
        cloud = var_list['cloud']
        name = var_list['vm']
        newProvider = Provider(name=cloud)

        #get vm
        cm = CmDatabase()
        try:
            vm = cm.find_name(name, "vm")[0]
        except IndexError:
            Console.error(f"could not find vm {name}")

        # get file path of the benchmark
        filepath = path.dirname(path.dirname(path.abspath(__file__))) + '/api/benchmark.py'
        filepath = filepath.replace('\\', '/')

        # prepare command to run the file
        vmcom = VmCommand()
        try:
            Console.msg('waiting for vm to be reachable...')
            Console.msg('wait')
            newProvider.wait(vm=vm)
        except:
            Console.msg('could not reach vm for benchmark')
            return
        try:
            Console.msg(f'moving benchmark file to vm...')
            Console.msg(f'put ' + filepath + ' /home/ubuntu')
            vmcom.do_vm('put ' + filepath + ' /home/ubuntu')
        except:
            Console.msg(f'could not ssh into vm, make sure one is running and reachable')
            return
        try:
            Console.msg(f'executing the benchmark...')
            Console.msg('ssh --command=\"chmod +x benchmark.py;./benchmark.py;rm benchmark.py;exit\"')
            benchtime = newProvider.ssh(vm=vm,command="chmod +x benchmark.py;./benchmark.py;rm benchmark.py;exit")
        except:
            Console.msg(f'could not ssh into vm, make sure one is running and reachable')
            return
        print("successfully benchmarked")
        benchtime = float(benchtime.strip())

        #add the benchmark, cloud, vm, and time to db
        benchdict = {}
        benchdict['cloud'] = cloud
        benchdict['name'] = name
        benchdict['ImageId'] = vm['ImageId']
        benchdict['flavor'] = vm['InstanceType']
        benchdict['region'] = vm['Placement']['AvailabilityZone']
        benchdict['BenchmarkTime'] = benchtime
        benchdict['updated'] = str(datetime.utcnow())
        benchdict["cm"] = {
            "kind": 'frugal-benchmark',
            "driver": cloud,
            "cloud": cloud,
            "name": name,
            "updated": str(datetime.utcnow()),
        }

        cm.update(benchdict, progress=True)
        return ""
