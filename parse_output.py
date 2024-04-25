#!/usr/bin/env python

import subprocess
import re
import optparse
import random


def parse_args():
    parser = optparse.OptionParser()
    parser.add_option("-f", "--file", dest="file", help="Path to the Java file to analyze")
    (options, args) = parser.parse_args()
    return options


def run_jbmc(java_file_path):
    try:
        result = subprocess.run(["jbmc", java_file_path, "--trace"], capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        print(f"Error running JBMC: {e}")
        return None


def extract_null_pointer_error_details(jbmc_output):
    pattern = r'(?: Null pointer check: FAILURE)(\w*)'
    matches = re.search(pattern, jbmc_output)


    if matches:
        variable_name = re.search(r"(?:\!\(\(struct java.lang.Object \*\)anonlocal::1)(\w*)", jbmc_output)
        return {'variable': variable_name.group(1)}
    return None


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
        variable_name = re.search(r"(?:anonlocal::2)(\w*)", jbmc_output)
        return { 'variable': variable_name.group(1) }
    
    return None


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
        variable_name = re.search(r"(?:\(\(struct java::array\[reference\] \*\)arg0a\)->length < \(\(struct java::array\[int\] \*\)anonlocal::2)(\w*)", jbmc_output)
        
        array_size = random.randint(1, 10)

        return {'variable': variable_name, 'index': array_size, 'array_size': array_size+1}
    return None


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
    with open(file_name, 'w') as file:
        file.write(code)


def main(java_file_path):
    jbmc_output = run_jbmc(java_file_path)
    if jbmc_output:
        print(jbmc_output)
        null_pointer_details = extract_null_pointer_error_details(jbmc_output)
        divide_by_zero_details = extract_divide_by_zero_error_details(jbmc_output)
        array_bounds_details = extract_array_index_out_of_bounds_details(jbmc_output)

        # Generate Java code for each error type if detected

        if "VERIFICATION FAILED" not in jbmc_output:
            return "No errors found, verification successful."\

        if null_pointer_details:
            java_code_null_pointer = generate_null_pointer_exception_code(null_pointer_details)
            write_code_to_file(java_code_null_pointer, "NullPointerException.java")
            return "Generated Java Code for Null Pointer Exception\n"

        if divide_by_zero_details:
            java_code_divide_by_zero = generate_divide_by_zero_exception_code(divide_by_zero_details)
            write_code_to_file(java_code_divide_by_zero, "DivideByZeroException.java")
            return "Generated Java Code for Divide By Zero Exception:\n"

        if array_bounds_details:
            java_code_array_bounds = generate_array_index_out_of_bounds_exception_code(array_bounds_details)
            write_code_to_file(java_code_array_bounds, "ArrayBoundsException.java")
            return "Generated Java Code for Array Index Out of Bounds Exception:\n"

    else:
        return "Unknown"


if __name__ == "__main__":
    options = parse_args()
    output = main(options.file)
    print(output)
