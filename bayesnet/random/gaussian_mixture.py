import numpy as np
from bayesnet.math.exp import exp
from bayesnet.math.log import log
from bayesnet.math.sqrt import sqrt
from bayesnet.math.square import square
from bayesnet.random.random import RandomVariable
from bayesnet.tensor.constant import Constant
from bayesnet.tensor.tensor import Tensor


class GaussianMixture(RandomVariable):
    """
    Mixture of the Gaussian distribution
    p(x|w, mu, std)
    = w_1 * N(x|mu_1, std_1) + ... + w_K * N(x|mu_K, std_K)

    Parameters
    ----------
    coef : tensor_like
        mixing coefficient whose sum along specified axis should equal to 1
    mu : tensor_like
        mean parameter along specified axis for each component
    std : tensor_like
        std parameter along specified axis for each component
    axis : int
        axis along which represents each component
    data : tensor_like
        realization
    prior : RandomVariable
        prior distribution
    """

    def __init__(self, coef, mu, std, axis=-1, data=None, prior=None):
        super().__init__(data, prior)
        self.axis = axis
        self.coef, self.mu, self.std = self._check_input(coef, mu, std)

    def _check_input(self, coef, mu, std):
        coef = self._convert2tensor(coef)
        mu = self._convert2tensor(mu)
        std = self._convert2tensor(std)

        if not coef.shape == mu.shape == std.shape:
            raise ValueError("shape of coef, mu, and std must be the same")
        self.n_component = coef.shape[self.axis]

        return coef, mu, std

    @property
    def axis(self):
        return self.parameter["axis"]

    @axis.setter
    def axis(self, axis):
        if not isinstance(axis, int):
            raise TypeError("axis must be int")
        self.parameter["axis"] = axis

    @property
    def coef(self):
        return self.parameter["coef"]

    @coef.setter
    def coef(self, coef):
        self._atleast_ndim(coef, 1)
        if (coef.value < 0).any():
            raise ValueError("value of mixing coefficient must all be positive")

        if not np.allclose(coef.value.sum(axis=self.axis), 1):
            raise ValueError("sum of mixing coefficients must be 1")
        self.parameter["coef"] = coef

    @property
    def mu(self):
        return self.parameter["mu"]

    @mu.setter
    def mu(self, mu):
        self.parameter["mu"] = mu

    @property
    def std(self):
        return self.parameter["std"]

    @std.setter
    def std(self, std):
        self._atleast_ndim(std, 1)
        if (std.value < 0).any():
            raise ValueError("value of std must all be positive")
        self.parameter["std"] = std

    @property
    def var(self):
        return square(self.parameter["std"])

    def forward(self):
        indices = np.array(
            [np.random.choice(self.n_component, p=c) for c in self.coef.value]
        )
        output = np.random.normal(
            loc=self.mu.value[indices],
            scale=self.std.value[indices]
        )
        if (
                isinstance(self.coef, Constant)
                and isinstance(self.mu, Constant)
                and isinstance(self.std, Constant)
        ):
            return Constant(output)
        return Tensor(output, function=self)

    def backward(self):
        raise NotImplementedError

    def _pdf(self, x):
        gauss = (
            exp(-0.5 * square((x - self.mu) / self.std))
            / sqrt(2 * np.pi) / self.std
        )
        return (self.coef * gauss).sum(axis=self.axis)

    def _log_pdf(self, x):
        return log(self.pdf(x))
