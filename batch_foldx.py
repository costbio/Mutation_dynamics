import os
import pandas as pd
import subprocess
import glob
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

def process_pdb(args):
    (folder, pdb_model_dir, foldx_dir, foldx_output_dir, df, foldx_binary, rotabase_path, pdb_file) = args
    base_folder_name = os.path.basename(folder)
    pdb_file_name = os.path.basename(pdb_file)
    base_model_name = pdb_file_name.replace(".pdb", "")

    try:
        protein, chain, _ = base_folder_name.split("_")
    except ValueError:
        print(f"Folder name error: {base_folder_name}")
        return []

    try:
        model_index = int(base_model_name.split("_")[1])
    except (IndexError, ValueError):
        print(f"Model index error: {base_model_name}")
        return []

    output_dir = os.path.join(foldx_output_dir, base_folder_name)
    os.makedirs(output_dir, exist_ok=True)
    repaired_pdb = f"{base_model_name}_Repair.pdb"

    if not os.path.exists(os.path.join(output_dir, repaired_pdb)):
        subprocess.run([
            foldx_binary,
            "--command=RepairPDB",
            f"--pdb={pdb_file_name}",
            f"--pdb-dir={os.path.join(pdb_model_dir, folder)}",
            f"--rotabase={rotabase_path}"
        ], cwd=output_dir)

    subset = df[(df["Protein"] == protein) & (df["Chain"] == chain)]
    if subset.empty:
        print(f"🔍 No mutation: {base_model_name}")
        return []

    results = []
    for idx, row in subset.iterrows():
        mutation = row["Mutasyon"]
        try:
            wt = mutation[0]
            pos = mutation[1:-1]
            mt = mutation[-1]
            foldx_mutation = f"{wt}{chain}{pos}{mt}"
        except Exception as e:
            print(f"Mutation format error: {mutation} ({e})")
            continue

        list_file = os.path.join(output_dir, f"individual_list_{base_model_name}_{foldx_mutation}.txt")
        with open(list_file, "w") as f:
            f.write(foldx_mutation + ";\n")

        fxout_file = os.path.join(output_dir, f"Dif_{mutation}.fxout")
        # Skip if output already exists
        if os.path.exists(fxout_file):
            print(f"⏩ Skipping {base_model_name}, {mutation} (already predicted)")
            continue

        subprocess.run([
            foldx_binary,
            "--command=BuildModel",
            f"--pdb={repaired_pdb}",
            f"--pdb-dir={output_dir}",
            f"--out-pdb=true",
            f"--output-file=Dif_{mutation}.fxout",
            f"--mutant-file={list_file}",
            f"--rotabase={rotabase_path}"
        ], cwd=output_dir)

        time.sleep(0.5)

    return results

def run_foldx_parallel(excel_path, pdb_model_dir, foldx_dir, foldx_output_dir, max_workers=4):
    os.makedirs(foldx_output_dir, exist_ok=True)
    df = pd.read_excel(excel_path)
    foldx_binary = os.path.join(foldx_dir, "foldx_20251231")
    rotabase_path = os.path.join(foldx_dir, "rotabase.txt")
    os.environ["FOLDX_DIRECTORY"] = foldx_dir

    folders = os.listdir(pdb_model_dir)  # adjust as needed

    pdb_tasks = []
    for folder in folders:
        base_folder_name = os.path.basename(folder)
        pdb_files = glob.glob(os.path.join(pdb_model_dir, base_folder_name, "model_*.pdb"))
        for pdb_file in pdb_files:
            pdb_tasks.append((folder, pdb_model_dir, foldx_dir, foldx_output_dir, df, foldx_binary, rotabase_path, pdb_file))

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_pdb, args) for args in pdb_tasks]
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"Parallel error: {e}")

# Kullanım
if __name__ == "__main__":
    run_foldx_parallel(
        excel_path="/home/begum/model_mutation_pairs.xlsx",
        pdb_model_dir="/home/begum/Fixed_pdb/fixedd3_cabs_output",
        foldx_dir="/home/begum/foldx5_1Mac_0/foldx__1Linux64_0",
        foldx_output_dir="/home/begum/Fixed_pdb/fixedd3_foldx_output",
        max_workers=60  # Set your desired parallelism here
    )

