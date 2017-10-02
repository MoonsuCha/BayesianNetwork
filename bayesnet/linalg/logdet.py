import numpy as np
from bayesnet.tensor.constant import Constant
from bayesnet.tensor.tensor import Tensor
from bayesnet.function import Function


class LogDeterminant(Function):

    def _forward(self, x):
        x = self._convert2tensor(x)
        self.x = x
        self._equal_ndim(x, 2)
        sign, self.output = np.linalg.slogdet(x.value)
        if sign != 1:
            raise ValueError("matrix has to be positive-definite")
        if isinstance(self.x, Constant):
            return Constant(self.output)
        return Tensor(self.output, function=self)

    def _backward(self, delta):
        dx = delta * np.linalg.inv(self.x.value.T)
        self.x.backward(dx)


def logdet(x):
    """
    log determinant of a matrix

    Parameters
    ----------
    x : (d, d) tensor_like
        a matrix to compute its log determinant

    Returns
    -------
    output : (d, d) tensor_like
        determinant of the input matrix
    """
    return LogDeterminant().forward(x)
