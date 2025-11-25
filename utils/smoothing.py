import time
import numpy as np


class EMA:
    """Simple exponential moving average smoother."""

    def __init__(self, alpha: float = 0.5):
        self.alpha = float(alpha)
        self.state = None

    def reset(self):
        self.state = None

    def update(self, x: np.ndarray):
        x = np.asarray(x, dtype=np.float32)
        if self.state is None:
            self.state = x.copy()
        else:
            self.state = self.alpha * x + (1 - self.alpha) * self.state
        return self.state


class OneEuroFilter:
    """
    One Euro Filter for smoothing positions with adaptive cutoff.
    Lightweight implementation for landmark smoothing.
    """

    def __init__(self, freq=30.0, min_cutoff=1.0, beta=0.0, d_cutoff=1.0):
        self.freq = float(freq)
        self.min_cutoff = float(min_cutoff)
        self.beta = float(beta)
        self.d_cutoff = float(d_cutoff)
        self.reset()

    def _alpha(self, cutoff, dt):
        tau = 1.0 / (2 * np.pi * cutoff)
        return 1.0 / (1.0 + tau / dt)

    def reset(self):
        self.last_time = None
        self.x_prev = None
        self.dx_prev = None

    def update(self, x, timestamp=None):
        x = np.asarray(x, dtype=np.float32)
        t = timestamp if timestamp is not None else time.time()
        
        if self.last_time is None:
            dt = 1.0 / self.freq
        else:
            dt = max(1e-6, t - self.last_time)
        self.last_time = t

        if self.x_prev is None:
            self.x_prev = x.copy()
            self.dx_prev = np.zeros_like(x)
            return x

        # Calculate derivative
        dx = (x - self.x_prev) / dt

        # Smooth derivative
        a_d = self._alpha(self.d_cutoff, dt)
        dx_hat = a_d * dx + (1 - a_d) * self.dx_prev

        # Adaptive cutoff
        cutoff = self.min_cutoff + self.beta * np.abs(dx_hat)
        a = self._alpha(cutoff.mean(), dt)

        x_hat = a * x + (1 - a) * self.x_prev

        # Update state
        self.x_prev = x_hat
        self.dx_prev = dx_hat

        return x_hat


class LandmarkSmoother:
    """Stateful smoother for landmark sets (Nx2 arrays)."""

    def __init__(self, method='one_euro', **kwargs):
        self.method = method
        self.kwargs = kwargs
        self._init_filters()

    def _init_filters(self):
        if self.method == 'ema':
            alpha = self.kwargs.get('alpha', 0.5)
            self.filter = EMA(alpha=alpha)
        elif self.method == 'one_euro':
            freq = self.kwargs.get('freq', 30.0)
            min_cutoff = self.kwargs.get('min_cutoff', 1.0)
            beta = self.kwargs.get('beta', 0.0)
            d_cutoff = self.kwargs.get('d_cutoff', 1.0)
            self.filter = OneEuroFilter(freq=freq, min_cutoff=min_cutoff, beta=beta, d_cutoff=d_cutoff)
        else:
            raise ValueError(f'Unknown smoothing method: {self.method}')

    def reset(self):
        self._init_filters()

    def smooth(self, landmarks: np.ndarray, timestamp: float = None) -> np.ndarray:
        """Smooth landmark array."""
        arr = np.asarray(landmarks, dtype=np.float32)
        flat = arr.flatten()
        
        if self.method == 'ema':
            out = self.filter.update(flat)
        else:  # one_euro
            out = self.filter.update(flat, timestamp)
            
        return np.asarray(out).reshape(arr.shape)
