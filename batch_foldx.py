import os
import pandas as pd
import subprocess
import glob
import time

def run_foldx_and_update_excel(excel_path, pdb_model_dir, foldx_dir, foldx_output_dir, output_excel_path):

    # Create the output directory if it doesn't exist
    os.makedirs(foldx_output_dir, exist_ok=True)
    # Read the Excel file
    df = pd.read_excel(excel_path)
    ddg_values = []

    foldx_binary = os.path.join(foldx_dir, "foldx_20251231")
    rotabase_path = os.path.join(foldx_dir, "rotabase.txt")
    os.environ["FOLDX_DIRECTORY"] = foldx_dir

    error_count = 0
    max_errors = 5

    for folder in os.listdir(pdb_model_dir)[:2]:
        
        # Get base folder name
        base_folder_name = os.path.basename(folder)

        # Get a list of model_*.pdb files in folder
        pdb_files = glob.glob(os.path.join(pdb_model_dir, base_folder_name, "model_*.pdb"))
        if not pdb_files:
            print(f"Folder '{folder}' does not contain any model_*.pdb files.")
            continue
        
        # Loop through each pdb file
        for pdb_file in pdb_files:
            # Get base name of the pdb file
            pdb_file = os.path.basename(pdb_file)
            # Get the full path of the pdb file
            pdb_path = os.path.join(pdb_model_dir, folder, pdb_file)
            base_model_name = pdb_file.replace(".pdb", "")

            try:
                protein, chain, _ = base_folder_name.split("_")
            except ValueError:
                print(f"Folder name error: {pdb_file}")
                continue

            try:
                # Extract model index from the base_model_name
                model_index = int(base_model_name.split("_")[1])
            except (IndexError, ValueError):
                print(f"Model index error: {base_model_name}")
                continue
                
            # Create an output directory for the current model in the foldx output directory, if it doesn't exist
            output_dir = os.path.join(foldx_output_dir, base_folder_name)
            os.makedirs(output_dir, exist_ok=True)

            # Repair
            repaired_pdb = f"{base_model_name}_Repair.pdb"

            if not os.path.exists(os.path.join(output_dir, repaired_pdb)):
                subprocess.run([
                    foldx_binary,
                    "--command=RepairPDB",
                    f"--pdb={pdb_file}",
                    f"--pdb-dir={os.path.join(pdb_model_dir, folder)}",
                    f"--rotabase={rotabase_path}"
                ], cwd=output_dir)
            subset = df[(df["Protein"] == protein) & (df["Chain"] == chain)]
            if subset.empty:
                print(f"🔍 No mutation: {base_model_name}")
                continue
            
            for idx, row in subset.iterrows():
                mutation = row["Mutasyon"]  # örn: A66H
                try:
                    wt = mutation[0]
                    pos = mutation[1:-1]
                    mt = mutation[-1]
                    foldx_mutation = f"{wt}{chain}{pos}{mt}"
                except Exception as e:
                    print(f"Mutation format error: {mutation} ({e})")
                    continue

                list_file = os.path.join(output_dir,f"individual_list_{base_model_name}_{foldx_mutation}.txt")

                with open(list_file, "w") as f:
                    f.write(foldx_mutation + ";\n")

                subprocess.run([
                    foldx_binary,
                    "--command=BuildModel",
                    f"--pdb={repaired_pdb}",
                    f"--pdb-dir={output_dir}",
                    f"--mutant-file={list_file}",
                    f"--rotabase={rotabase_path}"
                ], cwd=output_dir)

                time.sleep(0.5)

                dif_files = glob.glob(os.path.join(output_dir, f"Dif_*{mutation}*.fxout"))
                ddg_value = None
                if dif_files:
                    with open(dif_files[0], "r") as f:
                        for line in f:
                            parts = line.strip().split()
                            if len(parts) >= 2:
                                try:
                                    ddg_value = float(parts[1])
                                    print(f"✅ {base_model_name}, {mutation} → ΔΔG = {ddg_value}")
                                    break
                                except:
                                    continue
                else:
                    print(f"No file found: {base_model_name}, {mutation}")
                    error_count += 1
                    if error_count >= max_errors:
                        print("Error limit exceeded. Exiting.")
                        df.to_excel(excel_path, index=False)
                        return

                ddg_values.append((idx, ddg_value))

    df["DDG"] = [None] * len(df)
    for idx, ddg in ddg_values:
        df.at[idx, "DDG"] = ddg

    df.to_excel(output_excel_path, index=False)
    print(f"\n All ddG values were saved to '{excel_path}'.")

# Kullanım
if __name__ == "__main__":
    run_foldx_and_update_excel(
        excel_path="model_mutation_pairs.xlsx",
        pdb_model_dir="/home/begum/Fixed_pdb/fixedd3_cabs_output",
        foldx_dir="/home/begum/foldx5_1Mac_0/foldx__1Linux64_0",
        foldx_output_dir="/home/begum/Fixed_pdb/fixedd3_foldx_output",
        output_excel_path="model_mutation_pairs_foldx.xlsx"
    )

