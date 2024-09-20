import os
import numpy as np
import pandas as pd
from scipy.ndimage import gaussian_filter
from scipy import optimize as opt
from skimage import io as skio
from skimage.feature import canny
from skimage.morphology import label
from skimage.measure import regionprops
import argparse

def twoD_GaussianScaledAmp(xdata_tuple, xo, yo, sigma_x, sigma_y, amplitude, offset):
    """Returns a 2D Gaussian function as a 1D array for fitting."""
    (x, y) = xdata_tuple
    g = offset + amplitude * np.exp(
        -(((x - xo) ** 2) / (2 * sigma_x ** 2) + ((y - yo) ** 2) / (2 * sigma_y ** 2))
    )
    return g.ravel()

def getFWHM_GaussianFitScaledAmp(img):
    """Fits a 2D Gaussian to a cropped image and returns the volume and amplitude."""
    x, y = np.meshgrid(np.linspace(0, img.shape[1], img.shape[1]), np.linspace(0, img.shape[0], img.shape[0]))

    initial_guess = (img.shape[1] / 2, img.shape[0] / 2, 5, 5, 1, 0)
    bg = np.percentile(img, 5)
    img_scaled = np.clip((img - bg) / (img.max() - bg), 0, 1)

    popt, _ = opt.curve_fit(
        twoD_GaussianScaledAmp, (x, y), img_scaled.ravel(), 
        p0=initial_guess,
        bounds=(
            (img.shape[1] * 0.4, img.shape[0] * 0.4, 1, 1, 0.05, -0.1),
            (img.shape[1] * 0.6, img.shape[0] * 0.6, img.shape[1] / 2, img.shape[0] / 2, 2.5, 0.5)
        ),
        maxfev=2000
    )
    sigma_x, sigma_y, amp = popt[2], popt[3], popt[4]
    V = 2 * np.pi * sigma_x * sigma_y * amp
    return V, amp

def process_image(image):
    """Processes an image, detects edges, and quantifies features (foci)."""
    bg = gaussian_filter(image, sigma=1.5)
    image = image - bg
    blur = gaussian_filter(image, sigma=0.7)
    thres = blur > 60
    edges = canny(thres, sigma=0.7)

    # Label connected regions and quantify foci
    label_image = label(edges)
    features = []

    for region in regionprops(label_image):
        if region.area < 5 or region.bbox[0] < 10 or region.bbox[1] < 10 or region.bbox[2] > image.shape[0] - 10 or region.bbox[3] > image.shape[1] - 10:
            continue

        minr, minc, maxr, maxc = region.bbox
        cropped_image = image[max(minr - 6, 0):min(maxr + 6, image.shape[0]), max(minc - 6, 0):min(maxc + 6, image.shape[1])]

        V, amp = getFWHM_GaussianFitScaledAmp(cropped_image)
        features.append({
            'xmin': minr - 6, 'xmax': maxr + 6, 'ymin': minc - 6, 'ymax': maxc + 6, 
            'V': V, 'Amp': amp, 'y': region.centroid[0], 'x': region.centroid[1], 'frame': 1
        })

    return pd.DataFrame(features)

def process_folder(input_path, output_path, split_term):
    """Processes all images in the given folder and saves foci data."""
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    for folder in os.listdir(input_path):
        dir_path = os.path.join(input_path, folder)
        files = [f for f in os.listdir(dir_path) if f.endswith('.tif')]

        foci_data = []

        for filename in files:
            file_path = os.path.join(dir_path, filename)
            imstack = skio.imread(file_path, plugin="tifffile").astype(float)

            features = process_image(imstack)
            if not features.empty:
                frame_num = int(filename.split('.')[0])
                data_summary = np.hstack((np.full((features.shape[0], 1), frame_num), features[['Amp', 'V']].values))
                foci_data.append(data_summary)

        if foci_data:
            foci_data = np.vstack(foci_data)
            # Using split_term to generate the output file name
            output_file = os.path.join(output_path, folder.split(split_term)[1].replace("/", "_") + '_foci_summary.txt')
            np.savetxt(output_file, foci_data, delimiter='\t', fmt='%f')

if __name__ == "__main__":
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description="Process images and extract foci data.")
    parser.add_argument("input_path", help="Path to the input directory containing subfolders with images.")
    parser.add_argument("output_path", help="Path to the output directory where results will be saved.")
    parser.add_argument("split_term", help="String used to split folder names for generating unique output filenames.")
    
    args = parser.parse_args()

    # Run the folder processing with command line arguments
    process_folder(args.input_path, args.output_path, args.split_term)
