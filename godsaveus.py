import os
import subprocess
import json
import time
from tabulate import tabulate

def run_command_on_jars(directory, output_directory):
    original_directory = os.getcwd()  # Save the original directory
    os.chdir(directory)  # Change to the target directory

    # Check and create output directory if not exists
    full_output_path = os.path.join(original_directory, output_directory)
    if not os.path.exists(full_output_path):
        os.makedirs(full_output_path)
        print(f"Created directory {full_output_path}")
    else:
        print(f"Directory {full_output_path} already exists")

    results = []
    summary = {
        'Total Expected True': 0,
        'Total Actual True': 0,
        'Total Expected False': 0,
        'Total Actual False': 0,
        'Counter Examples Generated': 0,
        'Total Timeouts': 0
    }

    try:
        files = os.listdir()
        jar_files = [file for file in files if file.endswith('.jar')]

        for jar_file in jar_files:
            expected_result = 'True' if 'true' in jar_file else 'False'
            summary['Total Expected True' if expected_result == 'True' else 'Total Expected False'] += 1
            command = ['python3', 'jbmcsaveus.py', '-b', 'True', '-f', jar_file]
            print(f"Running command on {jar_file}: {' '.join(command)}")
            start_time = time.time()

            try:
                result = subprocess.run(command, timeout=1, capture_output=True, text=True)
                output = result.stdout
                elapsed_time = time.time() - start_time
                if result.stderr:
                    print("Error:", result.stderr)

                actual_result = 'False' if 'True' in output else 'True' 
                summary['Total Actual True' if actual_result == 'False' else 'Total Actual False'] += 1
                counter_example_generated = "Yes" if "file_name" in output else "No"
                if counter_example_generated == "Yes":
                    summary['Counter Examples Generated'] += 1

                results.append({
                    'File Name': jar_file,
                    'Expected Result': expected_result,
                    'Actual Result': actual_result,
                    'Counter Example Generated?': counter_example_generated,
                    'Time to Execute (s)': f"{elapsed_time:.2f}"
                })

            except subprocess.TimeoutExpired:
                print(f"Command on {jar_file} timed out.")
                summary['Total Timeouts'] += 1
                results.append({
                    'File Name': jar_file,
                    'Expected Result': expected_result,
                    'Actual Result': 'Timeout',
                    'Counter Example Generated?': 'No',
                    'Time to Execute (s)': '1.00'
                })

    finally:
        os.chdir(original_directory)  # Restore original directory

    # Print results table
    print(tabulate(results, headers="keys", tablefmt="grid"))

    # Calculate the new accuracy based on the given formula
    total_cases = len(jar_files)
    difference_true = abs(summary['Total Expected True'] - summary['Total Actual True'])
    difference_false = abs(summary['Total Expected False'] - summary['Total Actual False'])
    tt = summary['Total Timeouts']
    accuracy = (((difference_true + difference_false) - tt) / total_cases)*100
    accuracy = 100 - accuracy

    # Print summary
    print("\nSummary of Results:")
    print(f"Testsuite Name: CAV2018")
    print(f"Total number of testcases:", total_cases)
    print(f"Total Expected True: {summary['Total Expected True']}")
    print(f"Total Actual True: {summary['Total Actual True']}")
    print(f"Total Expected False: {summary['Total Expected False']}")
    print(f"Total Actual False: {summary['Total Actual False']}")
    print(f"Accuracy of proposed model: {accuracy:.2f}")
    print(f"Counter Examples Generated: {summary['Counter Examples Generated']}")
    print(f"Total Timeouts: {summary['Total Timeouts']}")

    # Save results to JSON file
    results_file_path = os.path.join(full_output_path, 'results.json')
    with open(results_file_path, 'w') as file:
        json.dump(results, file, indent=4) # Save summary to the same file
        json.dump(summary, file, indent=4)
    print(f"Results saved to {results_file_path}")
    

# Example usage
run_command_on_jars('jbmc-regression/', 'path_to_output_directory')
