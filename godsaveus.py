#!/usr/bin/env python

import os
import subprocess
import json
import time
from tabulate import tabulate
import shutil
import re

def run_command_on_jars(directory, output_directory):
    original_directory = os.getcwd()  # Save the original directory
    os.chdir(directory)  # Change to the target directory

    try:
        files = os.listdir()
        jar_files = [file for file in files if file.endswith('.jar')]

        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        results = []

        for jar_file in jar_files:
            command = ['python3', 'java_code_analyser.py', '-b', 'True', '-f', jar_file]
            print(f"Running command on {jar_file}: {' '.join(command)}")
            start_time = time.time()
            result = subprocess.run(command, capture_output=True, text=True)
            output = result.stdout
            elapsed_time = time.time() - start_time
            
            
            if result.stderr:
                print("Error:", result.stderr)

            if output:
                try:
                    actual_result = re.search(r"(?:'hasError':\s)(\w*)", output)
                    if actual_result is not None:
                        actual_result = actual_result.group(1)
                        actual_result = 'False' if 'True' in actual_result else 'True'
                    
                    hasFileName = re.search(r"(?:'file_name':\s)(\w*)", output)
                    counter_example_generated = "Yes" if hasFileName is not None else "No"
                    filename = None
                    if counter_example_generated is "Yes":
                        filename = hasFileName.group(1)

                    if filename and os.path.exists(filename):
                        shutil.move(filename, os.path.join(output_directory, filename))
                        print(f"Moved {filename} to {output_directory}")

                except json.JSONDecodeError:
                    actual_result = "Error parsing output"
                    counter_example_generated = "No"
                
                expected_result = 'True' if 'true' in jar_file else 'False'

                results.append({
                    'File Name': jar_file,
                    'Expected Result': expected_result,
                    'Actual Result': actual_result,
                    'Counter Example Generated?': counter_example_generated,
                    'Time to Execute (s)': f"{elapsed_time:.2f}"
                })
        
        print(tabulate(results, headers="keys", tablefmt="grid"))
        with open(os.path.join(output_directory, 'results.json'), 'w') as file:
            json.dump(results, file, indent=4)
        print("Results saved to results.json in", output_directory)

    finally:
        os.chdir(original_directory)  # Restore original directory

# Example usage
run_command_on_jars('jbmc-regression/', 'path_to_output_directory')
