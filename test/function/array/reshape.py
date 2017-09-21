import unittest
import numpy as np
from bayes.tensor import Parameter
from bayes.function import reshape


class TestReshape(unittest.TestCase):

    def test_reshape(self):
        self.assertRaises(ValueError, reshape, 1, (2, 3))

        x = np.random.rand(2, 6)
        p = Parameter(x)
        y = reshape(p, (3, 4))
        self.assertTrue((x.reshape(3, 4) == y.value).all())
        y.backward(np.ones((3, 4)))
        self.assertTrue((p.grad == np.ones((2, 6))).all())
