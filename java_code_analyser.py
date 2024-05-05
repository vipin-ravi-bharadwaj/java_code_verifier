#!/usr/bin/env python

import subprocess
import re
import optparse
import random

def parse_args():
    parser = optparse.OptionParser()
    parser.add_option("-f", "--file", dest="file", help="Path to the Java file to analyze")
    parser.add_option("-b", "--benchmark", dest="benchmark", help="To run the benchmark")
    (options, args) = parser.parse_args()
    return options


def convert_java_to_class(java_file_path):
    print(f"Converting {java_file_path} to class file...")
    subprocess.run(["javac", java_file_path], capture_output=True, text=True)


def run_jbmc(java_file_path):
    convert_java_to_class(java_file_path)
    print(f"Running JBMC on {java_file_path}...")
    class_file_path = java_file_path.replace(".java", "")
    result = subprocess.run(["jbmc", class_file_path, "--trace"], capture_output=True, text=True)
    return result.stdout


def run_jbmc_on_jar(jar_file_path):
    try:
        print(f"Running JBMC on {jar_file_path}...")
        result = subprocess.run(["jbmc", "-jar", jar_file_path, "--main-class", "Main", "--unwind", "10", "--trace"], capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        print(f"Error running JBMC: {e}")
        return None


def extract_null_pointer_error_details(jbmc_output):
    pattern = r'(?: Null pointer check: FAILURE)(\w*)'
    matches = re.search(pattern, jbmc_output)

    if matches:
        variable_name = re.search(r"(?:\!\(\(struct java.lang.Object \*\)anonlocal::1)(\w*)", jbmc_output)
        return { 'hasError': True, 'message': "Null Pointer Exception detected!", 'variable': variable_name.group(1) }
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
        variable_name = re.search(r"(?:anonlocal::2)(\w*)", jbmc_output)
        return { 'hasError': True, 'message': 'Divide by Zero Exception detected!', 'variable': variable_name.group(1) }
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
    pattern = r'Array index should be < length: FAILURE'
    matches = re.search(pattern, jbmc_output)

    if matches:
        variable_name = re.search(r"(?:\(\(struct java::array\[reference\] \*\)arg0a\)->length < \(\(struct java::array\[int\] \*\)anonlocal::2)(\w*)", jbmc_output)
        array_size = random.randint(1, 10)
        return { 'hasError': True, 'message': "Array Index Out of Bounds Exception detected!", 'variable': variable_name, 'index': array_size+1, 'array_size': array_size }
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


def main(java_file_path, benchmaring_mode=False):
    if(benchmaring_mode):
        jbmc_output = run_jbmc_on_jar(java_file_path)
    else:
        jbmc_output = run_jbmc(java_file_path)

    benchmark_object = { 'hasError': None, 'message': "No errors found" }

    if jbmc_output:
        print("Received JBMC output", jbmc_output)

        if "VERIFICATION FAILED" not in jbmc_output:
            benchmark_object["message"] = "No errors found, verification successful."
            benchmark_object["hasError"] = False

        else:
            error_detected = False
            for error_extract_func, error_generate_func in [
                (extract_null_pointer_error_details, generate_null_pointer_exception_code),
                (extract_divide_by_zero_error_details, generate_divide_by_zero_exception_code),
                (extract_array_index_out_of_bounds_details, generate_array_index_out_of_bounds_exception_code)
            ]:
                error_details = error_extract_func(jbmc_output)

                if error_details['hasError']:
                    java_code = error_generate_func(error_details)
                    file_name = java_file_path.replace(".java", "") + "Exception.java"
                    write_code_to_file(java_code, file_name)
                    error_detected = True
                    benchmark_object["hasError"] = False
                    benchmark_object["message"] = error_details['message']
                    benchmark_object["fileName"] = file_name
                    break

            if not error_detected:
                print("Unknown Error Detected")
                benchmark_object["hasError"] = False
                benchmark_object["message"] = "Unknown error detected"
                benchmark_object["unknown"] = True
    else:
        benchmark_object["message"] = "No output received from JBMC"
        benchmark_object["hasError"] = 'Unknown'

    print(benchmark_object)
    return benchmark_object


if __name__ == "__main__":
    options = parse_args()
    if options.file:
        print(f"Analyzing {options.file}...")
        main(options.file, options.benchmark,)
    else:
        print("Required files not provided. Exiting...")
