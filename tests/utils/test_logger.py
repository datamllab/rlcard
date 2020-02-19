import unittest
import os
import shutil

from rlcard.utils.logger import Logger

class TestLogger(unittest.TestCase):

    def test_log(self):
        log_dir = "./newtest/test_log.txt"
        if os.path.exists(log_dir):
            shutil.rmtree(log_dir)
        logger = Logger(log_dir)
        logger.log("test text")
        logger.log_performance(1, 1)
        logger.log_performance(2, 2)
        logger.log_performance(3, 3)
        logger.close_files()
        logger.plot('aaa')

if __name__ == '__main__':
    unittest.main()
