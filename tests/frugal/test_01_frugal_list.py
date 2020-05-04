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


    def compute_list(self):
        HEADING()

        Benchmark.Start()
        result = Shell.execute("cms frugal compute", shell=True)
        Benchmark.Stop()

        VERBOSE('frugal storage complete')
        VERBOSE(result)

    def storage_list(self):
        HEADING()

        Benchmark.Start()
        result = Shell.execute("cms frugal storage", shell=True)
        Benchmark.Stop()

        VERBOSE('frugal storage complete')
        VERBOSE(result)

    def gui_list(self):
        HEADING()

        Benchmark.Start()
        result = Shell.execute("cms frugal gui", shell=True)
        Benchmark.Stop()

        VERBOSE('frugal storage complete')
        VERBOSE(result)


