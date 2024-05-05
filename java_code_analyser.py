#!/usr/bin/env python

import subprocess
import re
import optparse
import random
import os


def parse_args():
    parser = optparse.OptionParser()
    parser.add_option("-f", "--file", dest="file", help="Path to the Java file to analyze")
    parser.add_option("-p", "--print-statements", dest="print_output", help="To print the steps")
    parser.add_option("-b", "--benchmark", dest="benchmark", help="To run the benchmark")
    (options, args) = parser.parse_args()

    if options.benchmark or not options.print_output:
        options.print_output = None

    return options
    

def print_statements(should_print, message):
    if should_print:
        print(message)


def convert_java_to_class(java_file_path, should_print):
    print_statements(should_print, f"Converting {java_file_path} to class file...")
    subprocess.run(["javac", java_file_path], capture_output=True, text=True)


def run_jbmc(java_file_path, should_print):
    convert_java_to_class(java_file_path, should_print)
    try:
        class_file_path = java_file_path.replace(".java", "")
        print_statements(should_print, f"Running JBMC on {class_file_path}...")
        result = subprocess.run(["jbmc", class_file_path, "--trace", "--unwind", "5"], capture_output=True, text=True, timeout=1)
        return result.stdout
    except Exception as e:
        print(f"Error running JBMC: {e}")
        return None
    

def run_jbmc_on_jar(jar_file_path, should_print):
    try:
        print_statements(should_print, f"Running JBMC on {jar_file_path}...")
        result = subprocess.run(["jbmc", "-jar", jar_file_path, "--main-class", "Main", "--unwind", "5", "--trace"], capture_output=True, text=True, timeout=1)
        return result.stdout
    except Exception as e:
        print(f"Error running JBMC: {e}")
        return None


def extract_null_pointer_error_details(jbmc_output):
    pattern = r'(?: Null pointer check: FAILURE)(\w*)'
    matches = re.search(pattern, jbmc_output)

    if matches:
        variable_name = re.search(r"(?:\!\(\(struct java.lang.Object \*\)anonlocal::1)(\w*)", jbmc_output)
        if variable_name:
            return { 'hasError': True, 'message': "Null Pointer Exception detected!", 'variable': variable_name.group(1) }
        else:
            return { 'hasError': True, 'message': "No null pointer exception detected" }    
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
    pattern = r'Denominator should be nonzero: FAILURE'
    matches = re.search(pattern, jbmc_output)

    if matches:
        variable_name = re.search(r"(?:anonlocal::2)(\w*)", jbmc_output)
        if variable_name:
            return { 'hasError': True, 'message': 'Divide by Zero Exception detected!', 'variable': variable_name.group(1) }
        else:
            return { 'hasError': True, 'message': "No divide by zero exception detected" }
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
        variable_name = re.search(r"(?:\(\(struct java::array\[reference\] \*\)arg0a\)->length < \(\(struct java::array\[int\] \*\)anonlocal::2)(\w*)", jbmc_output)
        array_size = random.randint(1, 10)
        return { 'hasError': True, 'variable': variable_name, 'index': array_size+1, 'array_size': array_size , 'error': 'Array Index Out of Bounds Exception' }
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
    with open(file_name, 'w') as file:
        file.write(code)


def main(java_file_path, benchmarking, should_print):
    jbmc_output = None

    if(benchmarking):
        jbmc_output = run_jbmc_on_jar(java_file_path, should_print)
    else:
        jbmc_output = run_jbmc(java_file_path, should_print)

    benchmark_object = { 'hasError': None, 'message': "No errors found" }

    if jbmc_output:
        print_statements(should_print, "Received JBMC output")

        null_pointer_details = extract_null_pointer_error_details(jbmc_output)
        divide_by_zero_details = extract_divide_by_zero_error_details(jbmc_output)
        array_bounds_details = extract_array_index_out_of_bounds_details(jbmc_output)

        error_detected = False

        if "VERIFICATION SUCCESSFUL" in jbmc_output:
            benchmark_object["message"] = "No errors found, verification successful."
            benchmark_object["hasError"] = False

        else:
            if null_pointer_details['hasError']:
                print_statements(should_print, "Null Pointer Exception detected!")
                if null_pointer_details['variable'] is not None:
                    java_code_null_pointer = generate_null_pointer_exception_code(null_pointer_details)
                    write_code_to_file(java_code_null_pointer, "NullPointerException.java")

                null_pointer_details['file_name'] = "NullPointerException.java"
                benchmark_object = null_pointer_details
                error_detected = True
            elif divide_by_zero_details['hasError']:
                print_statements(should_print, "Divide by Zero Exception detected!")
                if divide_by_zero_details['variable'] is not None:
                    java_code_divide_by_zero = generate_divide_by_zero_exception_code(divide_by_zero_details)
                    write_code_to_file(java_code_divide_by_zero, "DivideByZeroException.java")
                    
                divide_by_zero_details['file_name'] = "DivideByZeroException.java"
                benchmark_object = divide_by_zero_details
                error_detected = True
            elif array_bounds_details['hasError']:
                print_statements(should_print, "Array Index Out of Bounds Exception detected!")
                java_code_array_bounds = generate_array_index_out_of_bounds_exception_code(array_bounds_details)
                write_code_to_file(java_code_array_bounds, "ArrayBoundsException.java")  
                array_bounds_details['file_name'] = "ArrayBoundsException.java"
                benchmark_object = array_bounds_details  
                error_detected = True  

            if not error_detected:
                print_statements(should_print, "Unknown error detected!")
                benchmark_object["hasError"] = True
                benchmark_object["message"] = "Unknown error detected"
                benchmark_object["unknown"] = True

    if(benchmarking):
        print(benchmark_object)
        return benchmark_object
    

if __name__ == "__main__":
    options = parse_args()
    print("Reading file...")
    if(options.file):
        print_statements(options.print_output, "Analyzing file...")
        main(options.file, options.benchmark, options.print_output)
    else:
        print("No file provided. Exiting...")
