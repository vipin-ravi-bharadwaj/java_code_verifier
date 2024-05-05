#!/usr/bin/env python

import subprocess
import re
import optparse
import random

def parse_args():
    parser = optparse.OptionParser()
    parser.add_option("-f", "--file", dest="file", help="Path to the Java file to analyze")
    parser.add_option("-y", "--yaml", dest="yaml_file", help="Path to the YAML configuration file")
    (options, args) = parser.parse_args()
    return options


def read_yaml_as_text(yaml_file):
    expected_verdict = None
    with open(yaml_file, 'r') as file:
        lines = file.readlines()
        for line in lines:
            if 'expected_verdict:' in line:
                expected_verdict = line.strip().split(': ')[1]
                break
    return {'properties': [{'expected_verdict': expected_verdict}]}


def run_jbmc(java_file_path):
    print(f"Running JBMC on {java_file_path}...")
    result = subprocess.run(["jbmc", java_file_path, "--trace"], capture_output=True, text=True)
    return result.stdout


def extract_null_pointer_error_details(jbmc_output):
    pattern = r'(?: Null pointer check: FAILURE)(\w*)'
    matches = re.search(pattern, jbmc_output)

    if matches:
        print("Null Pointer Exception detected!")
        variable_name = re.search(r"(?:\!\(\(struct java.lang.Object \*\)anonlocal::1)(\w*)", jbmc_output)
        return { 'hasError': True, 'variable': variable_name.group(1) }
    else:
        return { 'hasError': False, 'message': "No null pointer exception detected" }


def generate_null_pointer_exception_code(error_details):
    variable_name = error_details['variable']
    code = f"""
public class NullPointerException {{
    public static void main(String[] args) {{
        Object {variable_name} = null;
        {variable_name}.toString();
    }}
}}
"""
    return code


def extract_divide_by_zero_error_details(jbmc_output):
    pattern = r'Denominator should be nonzero'
    matches = re.search(pattern, jbmc_output)

    if matches:
        print("Divide by Zero Exception detected!")
        variable_name = re.search(r"(?:anonlocal::2)(\w*)", jbmc_output)
        return { 'hasError': True,  'variable': variable_name.group(1) }
    else:
        return { 'hasError': False, 'message': "No divide by zero exception detected" }


def generate_divide_by_zero_exception_code(error_details):
    variable_name = error_details['variable']
    code = f"""
public class DivideByZeroException {{
    public static void main(String[] args) {{
        int {variable_name} = 0;
        int result = 10 / {variable_name};
    }}
}}
"""
    return code


def extract_array_index_out_of_bounds_details(jbmc_output):
    pattern = r'Array index should be < length'
    matches = re.search(pattern, jbmc_output)

    if matches:
        print("Array Index Out of Bounds Exception detected!")
        variable_name = re.search(r"(?:\(\(struct java::array\[reference\] \*\)arg0a\)->length < \(\(struct java::array\[int\] \*\)anonlocal::2)(\w*)", jbmc_output)
        array_size = random.randint(1, 10)
        return { 'hasError': True, 'variable': variable_name, 'index': array_size+1, 'array_size': array_size }
    else:
        return { 'hasError': False, 'message': "No array index out of bounds exception detected" }


def generate_array_index_out_of_bounds_exception_code(error_details):
    variable_name = error_details['variable']
    index = error_details['index']
    array_size = error_details['array_size']
    code = f"""
public class ArrayBoundsException {{
    public static void main(String[] args) {{
        int[] {variable_name} = new int[{array_size}];
        int illegalAccess = {variable_name}[{index}]; 
    }}
}}
"""
    return code


def write_code_to_file(code, file_name):
    print(f"Generating counterexample - {file_name}")
    with open(file_name, 'w') as file:
        file.write(code)


def main(java_file_path, yaml_file_path):
    yaml_data = read_yaml_as_text(yaml_file_path)
    expected_verdict = yaml_data['properties'][0]['expected_verdict']

    jbmc_output = run_jbmc(java_file_path)
    actual_verdict = "true" if "VERIFICATION FAILED" in jbmc_output else "false"

    print(f"File: {java_file_path}, Expected Verdict: {expected_verdict}, Actual Output: {actual_verdict}")

    if expected_verdict != actual_verdict:
        print("Mismatch detected. Analyzing errors...")
        error_detected = False
        for error_extract_func, error_generate_func in [
            (extract_null_pointer_error_details, generate_null_pointer_exception_code),
            (extract_divide_by_zero_error_details, generate_divide_by_zero_exception_code),
            (extract_array_index_out_of_bounds_details, generate_array_index_out_of_bounds_exception_code)
        ]:
            error_details = error_extract_func(jbmc_output)
            if error_details['hasError']:
                java_code = error_generate_func(error_details)
                file_name = java_file_path + "Exception.java"
                write_code_to_file(java_code, file_name)
                error_detected = True
                break

        if not error_detected:
            print("No specific errors detected, check JBMC output for more details.")
    else:
        print("Verification successful, actual output matches expected verdict.")

if __name__ == "__main__":
    options = parse_args()
    if options.file and options.yaml_file:
        print(f"Analyzing {options.file} based on the settings in {options.yaml_file}...")
        main(options.file, options.yaml_file)
    else:
        print("Required files not provided. Exiting...")
