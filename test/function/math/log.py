import unittest
import numpy as np
from bayes.tensor import Parameter
from bayes.function import log


class TestLog(unittest.TestCase):

    def test_log(self):
        x = Parameter(2.)
        y = log(x)
        self.assertEqual(y.value, np.log(2))
        y.backward()
        self.assertEqual(x.grad, 0.5)

        x = np.random.rand(4, 6)
        p = Parameter(x)
        y = log(p)
        self.assertTrue((y.value == np.log(x)).all())
        y.backward(np.ones((4, 6)))
        self.assertTrue((p.grad == 1 / x).all())
