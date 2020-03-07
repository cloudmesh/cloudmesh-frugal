###############################################################
# pytest -v --capture=no tests/frugal/test_01_frugal_list.py
# pytest -v  tests/frugal/test_01_frugal_list.py
# pytest -v --capture=no -v --nocapture tests/frugal/test_01_frugal_list..py::frugal.<METHIDNAME>
###############################################################
import pytest
from cloudmesh.mongo.CmDatabase import CmDatabase
from cloudmesh.common.util import HEADING
from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.Shell import Shell
from cloudmesh.common.Benchmark import Benchmark
Benchmark.debug()

@pytest.mark.incremental
class TestFrugalList:

    def test_list_refresh(self):
        HEADING()

        Benchmark.Start()
        result = Shell.execute("cms frugal list --refresh", shell=True)
        Benchmark.Stop()

        cm = CmDatabase()

        # shoudl we have frugal beeing first??? gregor is not sure
        # is is asw-frugal or frugal-aws based on local-key it may be
        # frugal second just as you have.

        #^ Collection names are created using the cm dictionary

        assert cm.collection('aws-frugal').estimated_document_count() > 0
        assert cm.collection('gcp-frugal').estimated_document_count() > 0
        assert cm.collection('azure-frugal').estimated_document_count() > 0

        VERBOSE('frugal list refresh complete')
        VERBOSE(result)


    def test_list_size(self):
        HEADING()

        Benchmark.Start()
        result = Shell.execute("cms frugal list --size=500", shell=True)
        Benchmark.Stop()

        VERBOSE('frugal list size complete')
        VERBOSE(result)

    def test_help_order(self):
        HEADING()

        Benchmark.Start()
        result = Shell.execute("cms frugal list --order=memory", shell=True)
        Benchmark.Stop()

        VERBOSE('frugal list order complete')
        VERBOSE(result)

    # comparision between differnt clouds missing. introduce a new test 03 in
    # which you measure for each cloud you supportedthe benchmark and compare with a fgrep script

    def test_benchmark(self):
        Benchmark.print()