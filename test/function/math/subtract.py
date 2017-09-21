import unittest
import numpy as np
from bayes.tensor import Parameter


class TestSubtract(unittest.TestCase):

    def test_forward_backward(self):
        x = Parameter(2)
        z = x - 5
        self.assertEqual(z.value, -3)
        z.backward()
        self.assertEqual(x.grad, 1)

        x = np.random.rand(5, 4)
        y = np.random.rand(4)
        p = Parameter(y)
        z = x - p
        self.assertTrue((z.value == x - y).all())
        z.backward(np.ones((5, 4)))
        self.assertTrue((p.grad == -np.ones(4) * 5).all())
