import os

import cv2
import matplotlib.pyplot as plt
import pywt
import numpy as np




# 小波去噪
def wavelet_domain_denoise(img):
    coeffs2 = pywt.dwt2(img, 'haar')
    LL, (LH, HL, HH) = coeffs2
    threshold = np.sqrt(2 * np.log(img.size))
    LH_new = pywt.threshold(LH.copy(), threshold * 0.5, 'soft')
    HL_new = pywt.threshold(HL.copy(), threshold * 0.5, 'soft')
    HH_new = pywt.threshold(HH.copy(), threshold * 0.5, 'soft')
    coeffs_new = (LL, (LH_new, HL_new, HH_new))
    denoised_img = pywt.idwt2(coeffs_new, 'haar')
    denoised_img = denoised_img.astype(np.uint8)
    return denoised_img


def baweraopen(image, size):
    '''
    @image:单通道二值图，数据类型uint8
    @size:欲去除区域大小(黑底上的白区域)
    '''
    output = image.copy()
    nlabels, labels, stats, centroids = cv2.connectedComponentsWithStats(image)
    for i in range(1, nlabels - 1):
        regions_size = stats[i, 4]
        if regions_size < size:
            x0 = stats[i, 0]
            y0 = stats[i, 1]
            x1 = stats[i, 0] + stats[i, 2]
            y1 = stats[i, 1] + stats[i, 3]
            for row in range(y0, y1):
                for col in range(x0, x1):
                    if labels[row, col] == i:
                        output[row, col] = 0
    return output

def get_contour(mask):
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(mask, connectivity=8)

    mask = np.zeros_like(mask)

    for label in range(1, num_labels):
        region_mask = np.uint8(labels == label)
        contours, _ = cv2.findContours(region_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            cv2.drawContours(mask, [contour], -1, 255, thickness=cv2.FILLED)

    return mask

