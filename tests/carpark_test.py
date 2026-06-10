import unittest
import sys,os
from pathlib import Path


#Add project root to path so smartpark package can be found
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from smartpark.mocks import MockCarparkManager

class TestConfigParsing(unittest.TestCase):

    def test_fresh_carpark(self):
        # arrange
        # act
        carpark = MockCarparkManager()
        # assert
        self.assertEqual(1000,carpark.available_spaces)

if __name__=="__main__":
#    print("cwd: " + parent + "/smartpark")
    unittest.main()
