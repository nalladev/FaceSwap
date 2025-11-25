import cv2
import numpy as np

def gaussian_pyramid(img, levels):
    g = img.copy().astype(np.float32)
    gp = [g]
    for i in range(levels):
        g = cv2.pyrDown(g)
        gp.append(g)
    return gp

def laplacian_pyramid(gp):
    lp = []
    for i in range(len(gp)-1):
        GE = cv2.pyrUp(gp[i+1])
        # ensure same size
        GE = cv2.resize(GE, (gp[i].shape[1], gp[i].shape[0]))
        L = gp[i] - GE
        lp.append(L)
    lp.append(gp[-1])
    return lp

def reconstruct_from_laplacian(lp):
    img = lp[-1]
    for i in range(len(lp)-2, -1, -1):
        img = cv2.pyrUp(img)
        img = cv2.resize(img, (lp[i].shape[1], lp[i].shape[0]))
        img = img + lp[i]
    return img


def laplacian_blend(img1, img2, mask, levels=4):
    """Blend two images using Laplacian pyramids and a mask.

    img1, img2: uint8 BGR images same size
    mask: single channel 0..255
    """
    if img1.shape != img2.shape:
        raise ValueError('Images must be same shape')

    mask_f = (mask.astype(np.float32) / 255.0)
    mask_f = cv2.merge([mask_f, mask_f, mask_f])

    gp1 = gaussian_pyramid(img1, levels)
    gp2 = gaussian_pyramid(img2, levels)
    gpm = gaussian_pyramid(mask_f, levels)

    lp1 = laplacian_pyramid(gp1)
    lp2 = laplacian_pyramid(gp2)

    LS = []
    for l1, l2, lm in zip(lp1, lp2, gpm):
        LS.append(l1 * lm + l2 * (1.0 - lm))

    blended = reconstruct_from_laplacian(LS)
    blended = np.clip(blended, 0, 255).astype(np.uint8)
    return blended


def create_adaptive_feather_mask(mask, feather_radius=15):
    """Create an adaptive feathered mask using distance transform.

    mask: binary 0/255 mask
    feather_radius: maximum feather radius in pixels
    """
    # distance from mask boundary
    kernel = np.ones((3,3), np.uint8)
    mask_bin = (mask > 127).astype(np.uint8)
    dist = cv2.distanceTransform(mask_bin, cv2.DIST_L2, 5)
    dist = np.clip(dist / (feather_radius + 1e-6), 0.0, 1.0)
    feather = (dist * 255).astype(np.uint8)
    return feather


def poisson_clone(src, dst, mask, center, flags=cv2.NORMAL_CLONE):
    try:
        return cv2.seamlessClone(src, dst, mask, center, flags)
    except Exception:
        # fallback to simple alpha blend
        mask_norm = (mask.astype(np.float32) / 255.0)
        mask_norm = np.dstack([mask_norm]*3)
        return (src * mask_norm + dst * (1-mask_norm)).astype(np.uint8)
