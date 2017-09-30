import numpy as np
from bayesnet.array.broadcast import broadcast_to
from bayesnet.linalg.cholesky import cholesky
from bayesnet.linalg.det import det
from bayesnet.linalg.logdet import logdet
from bayesnet.linalg.solve import solve
from bayesnet.linalg.trace import trace
from bayesnet.math.exp import exp
from bayesnet.math.log import log
from bayesnet.math.sqrt import sqrt
from bayesnet.random.random import RandomVariable
from bayesnet.tensor.constant import Constant
from bayesnet.tensor.tensor import Tensor


class MultivariateGaussian(RandomVariable):
    """
    Multivariate Gaussian distribution
    p(x|mu, cov)
    = exp{-0.5 * (x - mu)^T cov^-1 (x - mu)} * (1 / 2pi) ** (d / 2) * |cov^-1| ** 0.5
    where d = dimensionality

    Parameters
    ----------
    mu : (d,) tensor_like
        mean parameter
    cov : (d, d) tensor_like
        variance-covariance matrix
    data : (..., d) tensor_like
        observed data
    prior : RandomVariable
        prior distribution
    """

    def __init__(self, mu, cov, data=None, prior=None):
        super().__init__(data, prior)
        self.mu, self.cov = self._check_input(mu, cov)

    def _check_input(self, mu, cov):
        mu = self._convert2tensor(mu)
        cov = self._convert2tensor(cov)
        self._equal_ndim(mu, 1)
        self._equal_ndim(cov, 2)
        if cov.shape != (mu.size, mu.size):
            raise ValueError("Mismatching dimensionality of mu and cov")
        return mu, cov

    @property
    def mu(self):
        return self.parameter["mu"]

    @mu.setter
    def mu(self, mu):
        self.parameter["mu"] = mu

    @property
    def cov(self):
        return self.parameter["cov"]

    @cov.setter
    def cov(self, cov):
        try:
            self.L = cholesky(cov.value)
        except np.linalg.LinAlgError:
            raise ValueError("cov must be positive-difinite matrix")
        self.parameter["cov"] = cov

    def _forward(self):
        self.eps = np.random.normal(size=self.mu.size)
        output = self.mu.value + self.L.value @ self.eps
        if isinstance(self.mu, Constant) and isinstance(self.cov, Constant):
            return Constant(output)
        return Tensor(output, self)

    def _backward(self, delta):
        dmu = delta
        dL = delta @ self.eps[:, None]
        self.mu.backward(dmu)
        self.L.backward(dL)

    def _pdf(self, x):
        assert x.shape[-1] == self.mu.size
        if x.ndim == 1:
            squeeze = True
            x = broadcast_to(x, (1, self.mu.size))
        else:
            squeeze = False
        assert x.ndim == 2
        d = x - self.mu
        d = d.transpose()
        p = (
            exp(-0.5 * (solve(self.cov, d) * d).sum(axis=0))
            / (2 * np.pi) ** (self.mu.size * 0.5)
            / sqrt(det(self.cov))
        )
        if squeeze:
            p = p.sum()

        return p

    def _log_pdf(self, x):
        assert x.shape[-1] == self.mu.size
        if x.ndim == 1:
            squeeze = True
            x = broadcast_to(x, (1, self.mu.size))
        else:
            squeeze = False
        assert x.ndim == 2
        d = x - self.mu
        d = d.transpose()

        logp = (
            -0.5 * (solve(self.cov, d) * d).sum(axis=0)
            - (self.mu.size * 0.5) * log(2 * np.pi)
            - 0.5 * logdet(self.cov)
        )
        if squeeze:
            logp = logp.sum()

        return logp

    def _KLqp(self, p):
        if isinstance(p, MultivariateGaussian):
            d = p.mu - self.mu
            d = broadcast_to(d, (1, self.mu.size))
            d = d.transpose()
            kl = 0.5 * (
                logdet(p.cov) - logdet(self.cov)
                + trace(solve(p.cov, self.cov))
                + (solve(self.cov, d) * d).sum()
                - self.mu.size
            )
        else:
            raise NotImplementedError

        return kl
