### Instructions for Running Image Processing Scripts

#### 1. Setting up the Environment
- **On Windows**: Install a terminal application like `Ubuntu` from the Microsoft Store.
- **On macOS**: Use the built-in Terminal application.

In the terminal, run the following command to install the necessary Python packages:
```
pip install numpy pandas scipy scikit-image matplotlib argparse
```
If you don't have `pip` installed, you'll need to install it first. Make sure to create `input` and `output` folders where your data will be stored.

#### 2. Navigating to the Script
Change directory to the folder containing the `process_image.py` script using:
```
cd /path/to/folder
```

#### 3. Running the Script
To quantify foci data, run the following command:
```
python process_images.py /input_path /output_path "desired_split_string"
```
- **`/input_path`**: The directory containing subfolders of images.
- **`/output_path`**: The directory where results will be saved.
- **`"desired_split_string"`**: A string used to split folder names to generate unique output filenames.

#### 4. Example Folder Structure
```
input/
    folder1/
        image1.tif
        image2.tif
    folder2/
        image3.tif
        image4.tif
```

#### 5. Output
For each folder, the script will generate a summary file like `folder1_foci_summary.txt` in the specified `output_path`. 

Assuming all nuclei images from the same replicate are stored together in a folder, the `split_term` is the portion of the file name (or path) you want to use to differentiate and generate unique output filenames. This ensures that each output file is distinct and correctly linked to the image data.

**Note**: If your input and output paths are not in the same directory as the `process_image.py` script, make sure to specify the full paths.

#### 6. Naming Convention
The output `foci_summary` files will follow this format:
```
replicate-number_sample-name_foci_summary.txt
```
This structure ensures data is grouped correctly, preventing mix-ups between samples. The underscore (`_`) separates the replicate number from the sample name.

---

### Compiling Data Across Replicates

To combine data from replicates of the same experimental setup, use the `Data_compilation.py` script. Run the script with the following command:
```
python Data_compilation.py /input_path /output_path i
```
- **`/input_path`**: The folder where all the `_foci_summary.txt` files were saved during foci quantification.
- **`i`**: An integer that specifies the data to extract:
  - `0`: Number of cells
  - `1`: Total foci count
  - `2`: Number of foci per cell
  - `3`: Mean foci amplitude
  - `4`: Mean foci volume
  - `5`: Number of cells without foci

The output will be a final summary of all data for each experimental condition, which can then be plotted or analyzed further as needed.
