import os
import glob
import subprocess
from concurrent.futures import ThreadPoolExecutor

# Define the input and output directories
input_dir = "/home/begum/Fixed_pdb/fixedd3_pdbs"
output_dir = "/home/begum/Fixed_pdb/fixedd3_cabs_output"
n_cpu = 60  # Number of threads to use

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

def run_docker(pdb_file):
    """Run the Docker command for a single PDB file."""
    pdb_filename = os.path.basename(pdb_file)
    # Get only the basename of the PDB file using os.path.basename
    pdb_filename = os.path.basename(pdb_file) 
    # Remove the .pdb extension
    pdb_filename_wo = os.path.splitext(pdb_filename)[0]

    # Create a temporary string to server as docker container name
    temp_container_name = f"my-cabs-run-{pdb_filename_wo}"

    output_path = os.path.join(output_dir, pdb_filename_wo)
    docker_command = (
        f"docker run --name {temp_container_name} -v {input_dir}:/home:ro cabsflex_local "
        f"-i /home/{pdb_filename} -v 4 -w / -A && "
        f"docker cp {temp_container_name}:/output_pdbs {output_path}/ && "
        f"docker rm {temp_container_name}"
    )
    try:
        subprocess.run(docker_command, shell=True, check=True)
        print(f"Processed: {pdb_filename}")
    except subprocess.CalledProcessError as e:
        print(f"Error processing {pdb_filename}: {e}")

def main():
    # Get a list of all PDB files in the input directory
    pdb_files = glob.glob(os.path.join(input_dir, "*.pdb"))
    
    # Run the Docker commands in parallel
    with ThreadPoolExecutor(max_workers=n_cpu) as executor:
        executor.map(run_docker, pdb_files)

if __name__ == "__main__":
    main()