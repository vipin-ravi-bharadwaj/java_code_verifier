# Java Analysis Tool README

## Overview
This Python script is designed to automate the process of compiling Java files, running JBMC (Java Bounded Model Checker) on them, and identifying common runtime errors such as null pointer exceptions, divide by zero errors, and array index out of bounds exceptions. The script can handle individual Java files or Java archives (JARs) for more comprehensive analysis.

## Dependencies
- **Python 3.x**: Ensure Python 3 is installed on your system.
- **Java Development Kit (JDK)**: Required for compiling Java files and running Java applications.
- **JBMC**: Java Bounded Model Checker, used for verifying Java bytecode.

## Setup
1. **Install Python**: Download and install Python from [python.org](https://www.python.org/downloads/).
2. **Install JDK**: ```sudo apt install openjdk-8-jdk```
3. **Install JBMC**: ```sudo apt install jbmc```

## Usage
The script can be executed from the command line with several options to customize its behavior:

### Command Line Arguments
- `-f` or `--file`: Specify the path to the Java file or JAR to analyze.
- `-p` or `--print-statements`: Enable printing detailed steps of the process.
- `-b` or `--benchmark`: Run the tool in benchmark mode for performance testing.

### Example Commands
1. **Analyzing a single Java file with detailed output:**
   ```bash
   python parse_output.py -f path/to/MyProgram.java -p true
   ```
2. **Running in benchmark mode with a JAR file:**
   ```bash
   python parse_output.py -f path/to/MyApplication.jar -b true
   ```

### Scripts Functions
- **Main Functions**:
  - `convert_java_to_class()`: Compiles a Java file into a `.class` file.
  - `run_jbmc()`: Runs JBMC on a single `.class` file.
  - `run_jbmc_on_jar()`: Runs JBMC directly on a JAR file.

- **Error Detection Functions**:
  - `extract_null_pointer_error_details()`: Extracts details if a null pointer exception is detected.
  - `extract_divide_by_zero_error_details()`: Checks for divide by zero errors.
  - `extract_array_index_out_of_bounds_details()`: Looks for array index out of bounds errors.

- **Code Generation Functions**:
  - Generates minimal reproducible Java code snippets that demonstrate the identified errors.

### Output
The script generates output files for each type of error detected, containing a minimal Java program that will throw the corresponding error when executed. This is helpful for debugging and verifying that the fixes are effective.
