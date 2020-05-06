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
cloudmesh-installer get aws google frugal
```
For easy use, run command 

``
cms frugal gui
``

Follow prompts to price compare cloud storage and compute instances. 

### Usage

```
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

                frugal benchmark only work on implemented providers. Azure is not supported  by cloudmesh at this time.
```


[![image](https://img.shields.io/travis/TankerHQ/cloudmesh-bar.svg?branch=master)](https://travis-ci.org/TankerHQ/cloudmesn-bar)

[![image](https://img.shields.io/pypi/pyversions/cloudmesh-bar.svg)](https://pypi.org/project/cloudmesh-bar)

[![image](https://img.shields.io/pypi/v/cloudmesh-bar.svg)](https://pypi.org/project/cloudmesh-bar/)

[![image](https://img.shields.io/github/license/TankerHQ/python-cloudmesh-bar.svg)](https://github.com/TankerHQ/python-cloudmesh-bar/blob/master/LICENSE)

see cloudmesh.cmd5

* https://github.com/cloudmesh/cloudmesh.cmd5
