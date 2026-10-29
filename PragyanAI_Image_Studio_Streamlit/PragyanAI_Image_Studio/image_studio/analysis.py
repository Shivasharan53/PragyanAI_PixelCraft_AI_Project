from PIL import Image, ImageOps
import numpy as np
import cv2

def _dhash(image, hash_size=8):
    gray = ImageOps.grayscale(image).resize((hash_size+1, hash_size), Image.Resampling.LANCZOS)
    pixels = np.asarray(gray)
    return pixels[:, 1:] > pixels[:, :-1]

def compare_images(image_a, image_b):
    a_hash, b_hash = _dhash(image_a), _dhash(image_b)
    distance = int(np.count_nonzero(a_hash != b_hash))
    hash_score = 100 * (1 - distance / a_hash.size)
    size = (256, 256)
    a = cv2.resize(np.asarray(image_a.convert("RGB")), size)
    b = cv2.resize(np.asarray(image_b.convert("RGB")), size)
    # Compare grayscale structure using SSIM-style local statistics.
    a = cv2.cvtColor(a, cv2.COLOR_RGB2GRAY).astype(np.float64)
    b = cv2.cvtColor(b, cv2.COLOR_RGB2GRAY).astype(np.float64)
    mu_a = cv2.GaussianBlur(a, (11,11), 1.5)
    mu_b = cv2.GaussianBlur(b, (11,11), 1.5)
    sigma_a = cv2.GaussianBlur(a*a, (11,11), 1.5) - mu_a*mu_a
    sigma_b = cv2.GaussianBlur(b*b, (11,11), 1.5) - mu_b*mu_b
    sigma_ab = cv2.GaussianBlur(a*b, (11,11), 1.5) - mu_a*mu_b
    c1, c2 = (0.01*255)**2, (0.03*255)**2
    ssim_map = ((2*mu_a*mu_b+c1)*(2*sigma_ab+c2))/((mu_a*mu_a+mu_b*mu_b+c1)*(sigma_a+sigma_b+c2)+1e-12)
    structural = float(np.clip(ssim_map.mean(), -1, 1) * 100)
    score = float(np.clip(0.55*hash_score + 0.45*max(0, structural), 0, 100))
    return score, distance, structural
