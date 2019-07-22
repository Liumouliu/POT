"""Tests for module Unbalanced OT with entropy regularization"""

# Author: Hicham Janati <hicham.janati@inria.fr>
#
# License: MIT License

import numpy as np
import ot
import pytest

from scipy.misc import logsumexp


@pytest.mark.parametrize("method", ["sinkhorn", "sinkhorn_stabilized"])
def test_unbalanced_convergence(method):
    # test generalized sinkhorn for unbalanced OT
    n = 100
    rng = np.random.RandomState(42)

    x = rng.randn(n, 2)
    a = ot.utils.unif(n)

    # make dists unbalanced
    b = ot.utils.unif(n) * 1.5

    M = ot.dist(x, x)
    epsilon = 1.
    mu = 1.

    G, log = ot.unbalanced.sinkhorn_unbalanced(a, b, M, reg=epsilon, mu=mu,
                                               stopThr=1e-10, method=method,
                                               log=True)
    loss = ot.unbalanced.sinkhorn_unbalanced2(a, b, M, epsilon, mu,
                                              method=method)
    # check fixed point equations
    # in log-domain
    fi = mu / (mu + epsilon)
    logb = np.log(b + 1e-16)
    loga = np.log(a + 1e-16)
    logKtu = logsumexp(log["logu"][None, :] - M.T / epsilon, axis=1)
    logKv = logsumexp(log["logv"][None, :] - M / epsilon, axis=1)

    v_final = fi * (logb - logKtu)
    u_final = fi * (loga - logKv)

    np.testing.assert_allclose(
        u_final, log["logu"], atol=1e-05)
    np.testing.assert_allclose(
        v_final, log["logv"], atol=1e-05)

    # check if sinkhorn_unbalanced2 returns the correct loss
    np.testing.assert_allclose((G * M).sum(), loss, atol=1e-5)


@pytest.mark.parametrize("method", ["sinkhorn", "sinkhorn_stabilized"])
def test_unbalanced_multiple_inputs(method):
    # test generalized sinkhorn for unbalanced OT
    n = 100
    rng = np.random.RandomState(42)

    x = rng.randn(n, 2)
    a = ot.utils.unif(n)

    # make dists unbalanced
    b = rng.rand(n, 2)

    M = ot.dist(x, x)
    epsilon = 1.
    mu = 1.

    loss, log = ot.unbalanced.sinkhorn_unbalanced(a, b, M, reg=epsilon, mu=mu,
                                                  stopThr=1e-10, method=method,
                                                  log=True)
    # check fixed point equations
    # in log-domain
    fi = mu / (mu + epsilon)
    logb = np.log(b + 1e-16)
    loga = np.log(a + 1e-16)[:, None]
    logKtu = logsumexp(log["logu"][:, None, :] - M[:, :, None] / epsilon,
                       axis=0)
    logKv = logsumexp(log["logv"][None, :] - M[:, :, None] / epsilon, axis=1)
    v_final = fi * (logb - logKtu)
    u_final = fi * (loga - logKv)

    np.testing.assert_allclose(
        u_final, log["logu"], atol=1e-05)
    np.testing.assert_allclose(
        v_final, log["logv"], atol=1e-05)

    assert len(loss) == b.shape[1]


def test_stabilized_vs_sinkhorn():
    # test if stable version matches sinkhorn
    n = 100

    # Gaussian distributions
    a = ot.datasets.make_1D_gauss(n, m=20, s=5)  # m= mean, s= std
    b1 = ot.datasets.make_1D_gauss(n, m=60, s=8)
    b2 = ot.datasets.make_1D_gauss(n, m=30, s=4)

    # creating matrix A containing all distributions
    b = np.vstack((b1, b2)).T

    M = ot.utils.dist0(n)
    M /= np.median(M)
    epsilon = 0.1
    mu = 1.
    G, log = ot.unbalanced.sinkhorn_stabilized_unbalanced(a, b, M, reg=epsilon,
                                                          mu=mu,
                                                          log=True)
    G2, log2 = ot.unbalanced.sinkhorn_unbalanced2(a, b, M, epsilon, mu,
                                                  method="sinkhorn", log=True)

    np.testing.assert_allclose(G, G2)


def test_unbalanced_barycenter():
    # test generalized sinkhorn for unbalanced OT barycenter
    n = 100
    rng = np.random.RandomState(42)

    x = rng.randn(n, 2)
    A = rng.rand(n, 2)

    # make dists unbalanced
    A = A * np.array([1, 2])[None, :]
    M = ot.dist(x, x)
    epsilon = 1.
    mu = 1.

    q, log = ot.unbalanced.barycenter_unbalanced(A, M, reg=epsilon, mu=mu,
                                                 stopThr=1e-10,
                                                 log=True)
    # check fixed point equations
    fi = mu / (mu + epsilon)
    logA = np.log(A + 1e-16)
    logq = np.log(q + 1e-16)[:, None]
    logKtu = logsumexp(log["logu"][:, None, :] - M[:, :, None] / epsilon,
                       axis=0)
    logKv = logsumexp(log["logv"][None, :] - M[:, :, None] / epsilon, axis=1)
    v_final = fi * (logq - logKtu)
    u_final = fi * (logA - logKv)

    np.testing.assert_allclose(
        u_final, log["logu"], atol=1e-05)
    np.testing.assert_allclose(
        v_final, log["logv"], atol=1e-05)


def test_implemented_methods():
    IMPLEMENTED_METHODS = ['sinkhorn', 'sinkhorn_stabilized']
    TO_BE_IMPLEMENTED_METHODS = ['sinkhorn_reg_scaling']
    NOT_VALID_TOKENS = ['foo']
    # test generalized sinkhorn for unbalanced OT barycenter
    n = 3
    rng = np.random.RandomState(42)

    x = rng.randn(n, 2)
    a = ot.utils.unif(n)

    # make dists unbalanced
    b = ot.utils.unif(n) * 1.5

    M = ot.dist(x, x)
    epsilon = 1.
    mu = 1.
    for method in IMPLEMENTED_METHODS:
        ot.unbalanced.sinkhorn_unbalanced(a, b, M, epsilon, mu,
                                          method=method)
        ot.unbalanced.sinkhorn_unbalanced2(a, b, M, epsilon, mu,
                                           method=method)
    with pytest.warns(UserWarning, match='not implemented'):
        for method in set(TO_BE_IMPLEMENTED_METHODS):
            ot.unbalanced.sinkhorn_unbalanced(a, b, M, epsilon, mu,
                                              method=method)
            ot.unbalanced.sinkhorn_unbalanced2(a, b, M, epsilon, mu,
                                               method=method)
    with pytest.raises(ValueError):
        for method in set(NOT_VALID_TOKENS):
            ot.unbalanced.sinkhorn_unbalanced(a, b, M, epsilon, mu,
                                              method=method)
            ot.unbalanced.sinkhorn_unbalanced2(a, b, M, epsilon, mu,
                                               method=method)
