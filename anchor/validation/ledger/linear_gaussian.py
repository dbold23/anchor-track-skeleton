"""A linear-Gaussian model with an exact smoother, as the ledger's own control.

Every score in :mod:`anchor.validation.ledger.scores` is an estimator, and an
estimator with a sign error still returns a plausible-looking number. The only
cheap way to know the harness is right is to feed it a posterior that is known
in closed form and check that the calibration diagnostics come out at their
theoretical values: a flat rank histogram and containment equal to the nominal
level.

The model is a ``d``-dimensional Gaussian random walk observed in Gaussian
noise::

    x_0 ~ N(m0, P0)
    x_t = x_{t-1} + w_t,   w_t ~ N(0, q I)
    y_t = x_t + v_t,       v_t ~ N(0, r I)

Three routines: a forward Kalman filter, an RTS smoother (marginals), and
forward-filtering backward-sampling, which draws **joint** posterior paths.
The joint draws are the ones the ledger needs: the variogram score and the
path functionals read correlation structure that marginal draws do not carry.

Nothing here touches ``data/``, the network, or any optional dependency.
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
__all__ = ['LinearGaussianModel', 'ffbs_sample', 'kalman_filter', 'rts_smoother']

@dataclass(frozen=True)
class LinearGaussianModel:
    """Isotropic random walk observed in isotropic noise.

    Parameters
    ----------
    dim
        State dimension (1 or 2 for the ledger's cross-check).
    process_var
        ``q``, per-step process variance per axis.
    obs_var
        ``r``, observation variance per axis.
    init_mean, init_var
        Prior ``N(m0, P0)`` with ``P0 = init_var * I``.
    """
    dim: int = 2
    process_var: float = 1.0
    obs_var: float = 1.0
    init_mean: float = 0.0
    init_var: float = 1.0

    def __post_init__(self) -> None:
        ...

    def simulate(self, n_steps: int, rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
        """Draw ``(truth, observations)``, both ``(n_steps, dim)``, from the model.

        Truth is drawn from the *prior*, which is what makes the rank histogram
        of a functional of the exact posterior uniform: truth and posterior
        draws are then exchangeable.
        """
        ...

def kalman_filter(model: LinearGaussianModel, observations: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Forward filter.

    Returns ``(filt_mean, filt_var, pred_var)``, each ``(n, dim)`` /
    ``(n,)``-broadcastable: because every matrix in the model is a multiple of
    the identity, all covariances stay scalar multiples of ``I`` and are
    carried as scalars per step. ``pred_var[t]`` is the one-step prediction
    variance into ``t``, which the backward pass needs.
    """
    ...

def rts_smoother(model: LinearGaussianModel, observations: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Rauch-Tung-Striebel smoother: ``(mean, var)`` marginals, ``(n, dim)`` and ``(n,)``."""
    ...

def ffbs_sample(model: LinearGaussianModel, observations: np.ndarray, n_samples: int, rng: np.random.Generator) -> np.ndarray:
    """Exact joint posterior paths, ``(n_samples, n, dim)``.

    Forward-filtering backward-sampling: draw ``x_N ~ N(m_N, P_N)``, then for
    ``t = N-1 .. 0`` draw ``x_t | x_{t+1}, y_{1:N}``, whose mean is
    ``m_t + J (x_{t+1} - m_t)`` and whose variance is ``P_t - J**2 (P_t + q)``
    with ``J = P_t / (P_t + q)`` — the walk's transition being the identity.
    The result is a set of draws from the exact posterior over whole paths, so
    any functional computed on them is a draw from that functional's exact
    posterior.
    """
    ...
