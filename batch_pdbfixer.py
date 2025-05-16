
import os
import subprocess

input_folder = '/home/begum/S4038_structures'
output_folder = '/home/begum/Fixed_pdb/fixedd3_pdbs'

os.makedirs(output_folder, exist_ok=True)

for filename in os.listdir(input_folder):
    if filename.endswith('.pdb'):
        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, filename.replace('.pdb', '_fixed.pdb'))

        print(f'Fixing {filename}...')

        try:
            # Call pdbfixer as a command-line tool
            result = subprocess.run(
                ['pdbfixer', input_path, f'--output={output_path}'],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                print(f'✓ Saved: {output_path}')
            else:
                print(f' Hata: {filename} — {result.stderr}')
        except Exception as e:
            print(f' Hata: {filename} — {e}')
