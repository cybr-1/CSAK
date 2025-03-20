"""Tool to scan modules in a python file or a folder of python files."""

import os
import ast
import sys
import argparse
import importlib.metadata

def get_imports_from_file(filepath):
    """Extract imported modules from a given Python file."""
    with open(filepath, "r", encoding="utf-8") as file:
        tree = ast.parse(file.read(), filename=filepath)

    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split('.')[0])

    return imports

def get_standard_library_modules():
    """Returns a set of standard library modules."""
    if hasattr(sys, "stdlib_module_names"):  # Python 3.10+
        return set(sys.stdlib_module_names)
    
    # Fallback for older versions
    std_libs = set(sys.builtin_module_names)
    return std_libs

def get_installed_packages():
    """Returns a set of installed package names using importlib.metadata."""
    return {pkg.metadata["Name"].lower() for pkg in importlib.metadata.distributions()}

def scan_directory(directory):
    """Scans a directory for Python files and extracts external dependencies."""
    all_imports = set()
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                all_imports.update(get_imports_from_file(file_path))

    return all_imports

def write_requirements(imports, output_file):
    """Writes the extracted packages to a requirements.txt file."""
    standard_libs = get_standard_library_modules()
    installed_packages = get_installed_packages()

    external_packages = sorted(imports - standard_libs)

    with open(output_file, "w", encoding="utf-8") as file:
        for package in external_packages:
            if package in installed_packages:
                file.write(f"{package}\n")
    
    print(f"Generated {output_file} with {len(external_packages)} packages.")

def main():
    parser = argparse.ArgumentParser(description="Scan Python files for imported modules and generate a requirements.txt file.")
    parser.add_argument("--directory",type=str,default=None,help="Directory to scan modules in python files.", required=True)
    parser.add_argument("--output",type=str,default="requirements.txt",help="Output file name (default: ./requirements.txt).")

    args = parser.parse_args()

    imports = scan_directory(args.directory)
    write_requirements(imports, args.output)

if __name__ == "__main__":
    main()
