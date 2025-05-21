import os
import glob
import pandas as pd
from tqdm import tqdm

def parse_fxout_file(fxout_path):
    """Parse the first DDG value from a FoldX .fxout file."""
    try:
        with open(fxout_path, "r") as f:
            for line in f:
                parts = line.strip().split()
                # Skip empty lines and headers
                if not parts or not parts[0].endswith('.pdb'):
                    continue
                # Ensure there is at least a second column
                if len(parts) > 1:
                    try:
                        return float(parts[1])
                    except ValueError:
                        continue
    except Exception as e:
        print(f"Error reading {fxout_path}: {e}")
    return None

def extract_model_idx(model_name):
    # Example: "1APS_A_model_0.pdb" -> 0
    if isinstance(model_name, str) and "_model_" in model_name:
        try:
            return int(model_name.split("_model_")[1].split(".")[0])
        except Exception:
            return None
    return None

def find_fxout_and_ddg(row, output_folders):
    protein = row["Protein"]
    chain = row["Chain"]
    mutation = row["Mutasyon"]
    model_name = str(row["Model Adı"]) if "Model Adı" in row else None

    folder_pattern = f"{protein}_{chain}_"
    matching_folders = [f for f in output_folders if os.path.basename(f).startswith(folder_pattern)]
    if not matching_folders or not model_name:
        return {**row, "Model": None, "DDG": None}

    folder = matching_folders[0]
    folder_path = folder

    # Extract model index from model_name like "1APS_A_model_0.pdb"
    model_idx = extract_model_idx(model_name)

    fxout_pattern = os.path.join(folder_path, f"Dif_Dif_*{mutation}*model_{model_idx}_*.fxout")
    fxout_files = glob.glob(fxout_pattern)
    if not fxout_files:
        return {**row, "Model": model_idx, "DDG": None}

    ddg = parse_fxout_file(fxout_files[0])
    return {**row, "Model": model_idx, "DDG": ddg}

def supplement_ddg_to_excel(excel_path, foldx_output_dir, output_excel_path):
    df = pd.read_excel(excel_path)
    output_folders = glob.glob(f'{foldx_output_dir}/*')

    expanded_rows = []
    for _, row in tqdm(df.iterrows(), total=len(df), desc="Parsing fxout files"):
        expanded_rows.append(find_fxout_and_ddg(row, output_folders))

    expanded_df = pd.DataFrame(expanded_rows)
    expanded_df.to_excel(output_excel_path, index=False)
    print(f"\nAll ddG values were saved to '{output_excel_path}'.")

# Example usage:
if __name__ == "__main__":
    supplement_ddg_to_excel(
        excel_path="/home/begum/model_mutation_pairs.xlsx",
        foldx_output_dir="/home/begum/Fixed_pdb/fixedd3_foldx_output",
        output_excel_path="/home/begum/model_mutation_pairs_foldx_supplemented.xlsx"
    )