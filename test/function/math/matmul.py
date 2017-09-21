import unittest
import numpy as np
from bayes.tensor import Parameter


class TestMatMul(unittest.TestCase):

    def test_matmul(self):
        x = np.random.rand(10, 3)
        y = np.random.rand(3, 5)
        g = np.random.rand(10, 5)
        xp = Parameter(x)
        z = xp @ y
        self.assertTrue((z.value == x @ y).all())
        z.backward(g)
        self.assertTrue((xp.grad == g @ y.T).all())

        yp = Parameter(y)
        z = x @ yp
        self.assertTrue((z.value == x @ y).all())
        z.backward(g)
        self.assertTrue((yp.grad == x.T @ g).all())
