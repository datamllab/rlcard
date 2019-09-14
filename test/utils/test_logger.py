import unittest
from rlcard.utils.logger import Logger
import os

class TestLoggerMethos(unittest.TestCase):

    def test_log(self):
        logger = Logger(xlabel="x", ylabel="y", legend="test", log_path="./newtest/test_log.txt")
        logger.log("test text")
        f = open("./newtest/test_log.txt", "r")
        contents = f.read()
        self.assertEqual(contents, "test text\n")
        logger.close_file()

    def test_add_point(self):
        logger = Logger(xlabel="x", ylabel="y", legend="test", csv_path="./newtest/test_csv.csv")
        logger.add_point(x=1, y=1)
        self.assertEqual(logger.xs[0], 1)
        self.assertEqual(logger.ys[0], 1)

    def test_make_plot(self):
        logger = Logger(xlabel="x", ylabel="y", legend="test")
        for x in range(10):
            logger.add_point(x=x, y=x*x)
        self.assertEqual(9*9, logger.ys[9])
        logger.make_plot(save_path='./newtest/test.png')

    def test_close_file(self):
        logger = Logger(xlabel="x", ylabel="y", legend="test", log_path="./newtest/test_log.txt",csv_path="./newtest/test_csv.csv")
        logger.close_file()
        self.assertTrue(os.path.exists('./newtest/'))

if __name__ == '__main__':
    unittest.main()
