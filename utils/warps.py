import numpy as np
import cv2
from typing import List, Tuple

try:
    from skimage.transform import PiecewiseAffineTransform, warp
    SKIMAGE_AVAILABLE = True
except Exception:
    SKIMAGE_AVAILABLE = False
    # Log warning for missing optional dependency
    import logging
    logger = logging.getLogger(__name__)
    logger.warning("scikit-image not available - TPS warping disabled")


def apply_affine_warp(src_img: np.ndarray, src_landmarks: np.ndarray,
                      dst_landmarks: np.ndarray, output_shape: Tuple[int, int]) -> np.ndarray:
    """Simple global affine warp based on 3 key points (eyes + mouth)."""
    src_points = np.array([
        np.mean(src_landmarks[36:42], axis=0),
        np.mean(src_landmarks[42:48], axis=0),
        np.mean(src_landmarks[48:68], axis=0),
    ], dtype=np.float32)

    dst_points = np.array([
        np.mean(dst_landmarks[36:42], axis=0),
        np.mean(dst_landmarks[42:48], axis=0),
        np.mean(dst_landmarks[48:68], axis=0),
    ], dtype=np.float32)

    M = cv2.getAffineTransform(src_points, dst_points)
    warped = cv2.warpAffine(src_img, M, (output_shape[1], output_shape[0]), flags=cv2.INTER_LINEAR)
    return warped


def get_delaunay_triangles(points: np.ndarray, rect: Tuple[int, int, int, int]) -> List[Tuple[int, int, int]]:
    x, y, w, h = rect
    subdiv = cv2.Subdiv2D((x, y, x + w, y + h))
    pts = [tuple(map(int, p)) for p in points]
    for p in pts:
        subdiv.insert(p)

    triangle_list = subdiv.getTriangleList()
    triangles = []
    pts_arr = np.array(pts)
    for t in triangle_list:
        p1 = (int(t[0]), int(t[1]))
        p2 = (int(t[2]), int(t[3]))
        p3 = (int(t[4]), int(t[5]))
        indices = []
        for p in (p1, p2, p3):
            # find index of p in pts (allow small tolerance)
            d = np.linalg.norm(pts_arr - np.array(p), axis=1)
            idx = int(np.argmin(d))
            if d[idx] < 2.0:
                indices.append(idx)
        if len(indices) == 3:
            triangles.append(tuple(indices))
    return triangles


def warp_delaunay(src_img: np.ndarray, src_points: np.ndarray,
                  dst_points: np.ndarray, output_shape: Tuple[int, int]) -> np.ndarray:
    """Piecewise affine warp using Delaunay triangulation.

    src_points and dst_points should be arrays of matching 2D points.
    """
    h, w = output_shape[:2]
    src_img_out = np.zeros((h, w, 3), dtype=src_img.dtype)

    # Build triangulation on destination points to avoid holes
    rect = (0, 0, w, h)
    tris = get_delaunay_triangles(dst_points, rect)

    for tri in tris:
        src_tri = np.float32([src_points[i] for i in tri])
        dst_tri = np.float32([dst_points[i] for i in tri])

        # Warp each triangle
        src_rect = cv2.boundingRect(src_tri)
        dst_rect = cv2.boundingRect(dst_tri)

        if src_rect[2] == 0 or src_rect[3] == 0 or dst_rect[2] == 0 or dst_rect[3] == 0:
            continue

        src_tri_offset = src_tri - [src_rect[0], src_rect[1]]
        dst_tri_offset = dst_tri - [dst_rect[0], dst_rect[1]]

        src_cropped = src_img[src_rect[1]:src_rect[1] + src_rect[3], src_rect[0]:src_rect[0] + src_rect[2]]
        if src_cropped.size == 0:
            continue

        M = cv2.getAffineTransform(src_tri_offset, dst_tri_offset)
        warped = cv2.warpAffine(src_cropped, M, (dst_rect[2], dst_rect[3]), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101)

        mask = np.zeros((dst_rect[3], dst_rect[2]), dtype=np.uint8)
        cv2.fillConvexPoly(mask, np.int32(dst_tri_offset), 255)

        dst_area = src_img_out[dst_rect[1]:dst_rect[1] + dst_rect[3], dst_rect[0]:dst_rect[0] + dst_rect[2]]
        dst_area_bg = cv2.bitwise_and(dst_area, dst_area, mask=cv2.bitwise_not(mask))
        warped_fg = cv2.bitwise_and(warped, warped, mask=mask)
        dst_area_combined = cv2.add(dst_area_bg, warped_fg)
        src_img_out[dst_rect[1]:dst_rect[1] + dst_rect[3], dst_rect[0]:dst_rect[0] + dst_rect[2]] = dst_area_combined

    return src_img_out


def warp_tps(src_img: np.ndarray, src_points: np.ndarray, dst_points: np.ndarray, output_shape: Tuple[int, int]) -> np.ndarray:
    """Thin-plate-spline like warp. Prefer scikit-image PiecewiseAffine as fallback.

    If scikit-image is available, use its PiecewiseAffineTransform to produce smooth nonlinear warps.
    Otherwise raise ImportError.
    """
    if not SKIMAGE_AVAILABLE:
        raise ImportError('scikit-image is required for TPS warp mode. Install scikit-image to enable this feature.')

    # Build mesh on destination points using their convex hull + triangulation implicitly handled by PiecewiseAffine
    src = np.asarray(src_points)
    dst = np.asarray(dst_points)
    tform = PiecewiseAffineTransform()
    try:
        tform.estimate(src, dst)
        # Warp the image
        out = warp(src_img, tform, output_shape=output_shape)
        # warp returns float in [0,1], convert back
        out = (out * 255).astype(src_img.dtype)
        return out
    except Exception:
        # Fallback to piecewise (delaunay) warp
        return warp_delaunay(src_img, src_points, dst_points, output_shape)
