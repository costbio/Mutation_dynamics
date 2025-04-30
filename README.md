# Grad Project: Protein Mutation Automation

This project automates the preparation of input files and ΔΔG calculations using FoldX for assessing the impact of point mutations on protein stability.

##  Files

- `foldx loop.ipynb`: Loops through an Excel file containing PDB IDs, chains, and mutations to generate `individual_list` files and execute FoldX analysis.
- `pdb fixer loop.ipynb`: Script to fix PDB files before running FoldX (e.g., for chain cleanup or structure validation).

##  Features

- Accepts mutation info from Excel (PDB ID, chain, mutation format)
- Creates properly formatted `individual_list_*.txt` files for FoldX
- Automatically finds and copies matching PDB files for each mutation
- Prepares for batch processing in FoldX (BuildModel)

##  Requirements

- Python (3.8+)
- pandas
- os, shutil, glob
- FoldX (installed separately)
- Jupyter Notebook

##  Usage

1. Place your mutation Excel sheet in the project folder
2. Set `excel_path` and `foldx_path` in the notebook
3. Run the Jupyter notebook cells step by step
4. Output files will be generated for FoldX

##  Project Status

This project is part of a graduation thesis at Gebze Technical University 
It is actively being developed and optimized for large-scale FoldX usage.
