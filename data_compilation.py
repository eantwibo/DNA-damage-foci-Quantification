import os
import glob
import numpy as np
import pandas as pd
import argparse

def process_files(input_directory, output_directory):
    """Process all summary files in the input directory and save results to the output directory."""
    # Change working directory to the input path
    os.chdir(input_directory)
    
    # Get all summary files
    filenames = glob.glob("*foci_summary.txt")
    
    # Extract unique prefixes from filenames
    prefixes = sorted(set(f.split('_')[1] for f in filenames))
    
    for prefix in prefixes:
        files_data = [f for f in filenames if prefix in f]
        
        # Initialize a DataFrame to hold the final results
        final = pd.DataFrame()
        
        for file in files_data:
            # Load data from the file
            df = pd.DataFrame(np.loadtxt(file))
            # Add prefix to the first column
            df.iloc[:, 0] = file.split('_')[0] + df.iloc[:, 0].astype(str)
            
            # Filter data
            no_cells = df.iloc[:, 0].nunique()
            filtered_data = df[(df.iloc[:, 1] > 0.06) & (df.iloc[:, 2] > 5.)]
            
            # Calculate metrics
            foci_count = filtered_data.count().iloc[0]
            no_nofoci = (1 - filtered_data.groupby(filtered_data.iloc[:, 0]).size().count() / no_cells) * 100
            metrics = pd.DataFrame([no_cells, foci_count, foci_count / no_cells, filtered_data.iloc[:,1].mean(), filtered_data.iloc[:,2].mean(), no_nofoci]).T
            
            # Append metrics to the final DataFrame
            final = pd.concat([final, metrics], ignore_index=True, axis=0)
        
        # Calculate mean and std deviation
        final2 = pd.concat([final, final.mean(axis=1), final.std(axis=1)], ignore_index=True, axis=1)
        
        # Save results to a file
        final2.to_csv(os.path.join(output_directory, f"{prefix}_grouped.txt"), sep='\t', index=False)

def compile_final_data(input_directory, output_directory, i):
    os.chdir(input_directory)
    pfiles = glob.glob("*_grouped.txt")
    
    col_names = [file.replace("_grouped.txt", "") for file in pfiles]
    all_data = pd.DataFrame()

    # Process each grouped file and extract relevant data
    for file in pfiles:
        data = pd.read_csv(file, sep='\t', header=0, index_col=0)
        relevant_data = data.iloc[i, :3]  # Adjust this if necessary
        all_data = pd.concat([all_data, relevant_data], ignore_index=True, axis=1)
    
    all_data.columns = col_names
    ind_names = pd.Index(['exp1', 'exp2', 'exp3'])
    all_data.index = ind_names
    
    # Save the compiled data
    all_data.to_csv(os.path.join(output_directory, 'per_experiment.txt'), sep='\t')
	
def main(input_path, output_path, i):
    """Main function to process and compile data."""
    # Process summary files
    process_files(input_path, output_path)
    
    # Compile final data
    compile_final_data(input_path, output_path, i)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process and analyze foci data from images.")
    parser.add_argument("input_path", help="Path to the input directory containing summary files.")
    parser.add_argument("output_path", help="Path to the output directory where results will be saved.")
    parser.add_argument("i", type=int, help="Row index to use in data.iloc[i, :3].")
    
    args = parser.parse_args()
    main(args.input_path, args.output_path, args.i)
