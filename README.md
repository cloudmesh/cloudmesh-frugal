Documentation
=============
### About

Cloudmesh frugal is a cloudmesh commandline API that allows user to find the cheapest virtual machines, as well as compare their performance

### Installation

Cloudmesh frugal was created with Cloudmesh commands. Cloudmesh-installer must be installed to run.
```
source ~/ENV3/bin/activate
mkdir cm
cd cm
pip install cloudmesh-installer
cloudmesh-installer get cms
```

To install cloudmesh frugal, enter the following command. 

```
cloudmesh-installer get azure aws gcp
cloudmesh-installer get frugal
```

### Usage

```
        ::
            Usage:
                frugal list [--benchmark] [--refresh] [--order=ORDER] [--size=SIZE] [--cloud=CLOUD]
                frugal storage [--cloud=CLOUD] [--class=CLASS]
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
              CLASS       Limits the results to specific class of storage
                          including standard (regular access), nearline 
                          (infrequent access), coldline (quartly access 
                          or less), or archive (yearly access or less)
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
```


[![image](https://img.shields.io/travis/TankerHQ/cloudmesh-bar.svg?branch=master)](https://travis-ci.org/TankerHQ/cloudmesn-bar)

[![image](https://img.shields.io/pypi/pyversions/cloudmesh-bar.svg)](https://pypi.org/project/cloudmesh-bar)

[![image](https://img.shields.io/pypi/v/cloudmesh-bar.svg)](https://pypi.org/project/cloudmesh-bar/)

[![image](https://img.shields.io/github/license/TankerHQ/python-cloudmesh-bar.svg)](https://github.com/TankerHQ/python-cloudmesh-bar/blob/master/LICENSE)

see cloudmesh.cmd5

* https://github.com/cloudmesh/cloudmesh.cmd5
