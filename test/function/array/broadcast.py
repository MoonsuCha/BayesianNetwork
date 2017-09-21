import unittest
import numpy as np
from bayes.tensor import Parameter
from bayes.function import broadcast_to


class TestBroadcastTo(unittest.TestCase):

    def test_broadcast(self):
        x = Parameter(np.ones((1, 1)))
        shape = (5, 2, 3)
        y = broadcast_to(x, shape)
        self.assertEqual(y.shape, shape)
        y.backward(np.ones(shape))
        self.assertTrue((x.grad == np.ones((1, 1)) * 30).all())
