###############################################################
# pytest -v --capture=no tests/frugal/test_03_frugal_benchmark.py
# pytest -v  tests/frugal/test_03_frugal_benchmark.py
# pytest -v --capture=no -v --nocapture tests/frugal/test_03_frugal_benchmark..py::frugal.<METHIDNAME>
###############################################################
import pytest
from cloudmesh.mongo.CmDatabase import CmDatabase
from cloudmesh.common.util import HEADING
from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.Shell import Shell
from cloudmesh.common.Benchmark import Benchmark

Benchmark.debug()

@pytest.mark.incremental
class TestFrugalBenchmark:

    def test_frugal_aws(self):
        HEADING()

        Benchmark.Start()
        result = Shell.execute("cms frugal boot --cloud=aws", shell=True)
        VERBOSE(result)
        result = Shell.execute("cms frugal benchmark", shell=True)
        Benchmark.Stop()

        VERBOSE('frugal benchmark aws complete')
        VERBOSE(result)

    def test_frugal_azure(self):
        HEADING()

        Benchmark.Start()
        result = Shell.execute("cms frugal boot --cloud=azure", shell=True)
        VERBOSE(result)
        result = Shell.execute("cms frugal benchmark", shell=True)
        Benchmark.Stop()

        VERBOSE('frugal benchmark aws complete')
        VERBOSE(result)

    def test_benchmark(self):
        Benchmark.print()