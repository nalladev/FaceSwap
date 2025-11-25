import numpy as np
import cv2

try:
    from skimage import color, exposure
    SKIMAGE = True
except Exception:
    SKIMAGE = False


def match_histograms_lab(src, dst, strength=1.0):
    """Match color histogram of src to dst in Lab space.

    strength: 0.0 (no change) .. 1.0 (full matching)
    """
    if not SKIMAGE:
        # fallback: simple mean matching in BGR space
        src_f = src.astype(np.float32)
        dst_f = dst.astype(np.float32)
        mask = np.ones(src.shape[:2], dtype=np.uint8)
        src_mean = cv2.mean(src_f, mask=mask)[:3]
        dst_mean = cv2.mean(dst_f, mask=mask)[:3]
        factors = [1.0 if s == 0 else (d / (s + 1e-6)) for s, d in zip(src_mean, dst_mean)]
        out = src_f.copy()
        for i in range(3):
            out[:,:,i] = np.clip(out[:,:,i] * (1.0 + (factors[i]-1.0)*strength), 0, 255)
        return out.astype(np.uint8)

    # convert to Lab
    src_lab = color.rgb2lab(cv2.cvtColor(src, cv2.COLOR_BGR2RGB))
    dst_lab = color.rgb2lab(cv2.cvtColor(dst, cv2.COLOR_BGR2RGB))

    matched = np.zeros_like(src_lab)
    for ch in range(3):
        matched[:,:,ch] = exposure.match_histograms(src_lab[:,:,ch], dst_lab[:,:,ch])

    # blend between original and matched by strength
    out_lab = (1.0 - strength) * src_lab + strength * matched
    out_rgb = cv2.cvtColor((color.lab2rgb(out_lab) * 255).astype(np.uint8), cv2.COLOR_RGB2BGR)
    return out_rgb


class TemporalColorSmoother:
    """Simple temporal smoothing for color transform strength or parameters."""
    def __init__(self, alpha=0.6):
        self.alpha = alpha
        self.state = None

    def update(self, val):
        if self.state is None:
            self.state = val
            return val
        self.state = self.alpha * val + (1 - self.alpha) * self.state
        return self.state
