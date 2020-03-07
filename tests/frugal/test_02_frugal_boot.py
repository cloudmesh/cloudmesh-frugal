###############################################################
# pytest -v --capture=no tests/frugal/test_02_frugal_boot.py
# pytest -v  tests/frugal/test_02_frugal_boot.py
# pytest -v --capture=no -v --nocapture tests/frugal/test_02_frugal_boot..py::frugal.<METHIDNAME>
###############################################################
import pytest
from cloudmesh.mongo.CmDatabase import CmDatabase
from cloudmesh.common.util import HEADING
from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.Shell import Shell
from cloudmesh.common.Benchmark import Benchmark
Benchmark.debug()
from cloudmesh.common.StopWatch import StopWatch

@pytest.mark.incremental
class TestFrugalBoot:

    def test_boot(self):
        HEADING()

        Benchmark.Start()
        result = Shell.execute("cms frugal boot", shell=True)
        Benchmark.Stop()

        VERBOSE('frugal boot test complete')
        VERBOSE(result)

    def test_benchmark(self):
        Benchmark.print()