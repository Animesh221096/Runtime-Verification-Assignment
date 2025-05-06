import re
import sys

import argparse

def parse_arguments():
    """Parse command-line arguments."""
    # Create the parser
    parser = argparse.ArgumentParser(description='Instrument a C++ file for variable sampling.')

    # Add arguments
    parser.add_argument('input_cpp', type=str, 
                        help='C++ file with variables to instrument')
    parser.add_argument('sampling_interval', type=int, 
                        help='Sampling interval in milliseconds')
    parser.add_argument('output_cpp', type=str, 
                        help='Output file to write the instrumented C++')
    parser.add_argument('output_txt', type=str, 
                        help='Output text file for variable values')

    # Parse the arguments
    return parser.parse_args()



def instrument_cpp_file(input_file, sampling_interval, output_cpp, output_txt):
    # Read the input C++ file
    with open(input_file, 'r') as f:
        lines = f.readlines()

    variables_to_instrument = []



    new_libs_to_add = f"""
#include <fstream>
#include <string>
#include <iomanip>
#include <atomic>\n
"""
    lines.insert(0, new_libs_to_add)



    for i, line in enumerate(lines):
        if "using namespace std;" in line:
            lines.insert(i+1, f"\nvoid *logVariables(void *Thread_Number);\n")
            lines.insert(i+2, f"atomic<bool> logging_active(true);\n")
            

    
    # Find the global variables marked for instrumentation
    for i, line in enumerate(lines):
        if "$TO_INSTRUMENT$" in line:
            # The next line should contain the variable declaration
            variable_line = lines[i + 1].strip()
            # Extract the variable name (assuming it's a boolean)
            match = re.search(r'\bbool\s+(\w+)\s*=\s*(true|false);\s*', variable_line)
            if match:
                variables_to_instrument.append(match.group(1))



    init_log_tread = f"""    pthread_t log_thread;
    int iret_log;
    int log_thread_number = 2147483647;

    // Create threads for logger
    iret_log = pthread_create(&log_thread, NULL, logVariables, &log_thread_number);
    if (iret_log)
    {{
        fprintf(stderr, "Error - pthread_create() return code: %d\\n", iret_log);
        exit(EXIT_FAILURE);
    }}\n
"""

    for i, line in enumerate(lines):
        if "int main()" in line:
            if "{" in lines[i+1]:
                i += 1

            lines.insert(i+1, init_log_tread)

    lines.append("")

    join_log_thread = f"""\n    logging_active = false;
    pthread_join(log_thread, NULL);\n"""

    for i, line in enumerate(lines):
        if "exit(EXIT_SUCCESS);" in line:
            lines.insert(i-1, join_log_thread)
            break


    # Create the instrumentation code to inject
    instrumentation_code = f"""
void *logVariables(void *Thread_Number)
{{
    int my_number = *(int *)Thread_Number;
    int sample_index = 0;
    std::ofstream outFile("{output_txt}"); // Create an output file stream

    if (outFile.is_open())
    {{
        outFile << "Observations" << std::endl;
        while (logging_active)
        {{
            sleep_ms({sampling_interval});
            outFile << """
    
    # Add the instrumented variables to the logging code
    for var in variables_to_instrument:
        instrumentation_code += f"""{var} << ", " << """

    instrumentation_code += "std::endl;\n "
    instrumentation_code += f"""
            sample_index++;
        }}
        outFile.close();
    }}
    else
    {{
        std::cerr << "Unable to open file for writing." << std::endl;
    }}

    return NULL;

}}"""

    lines.insert(-1, instrumentation_code)


    with open(output_cpp, 'w') as f:
        f.writelines(lines)



def main():
    # Call the argument parser function
    args = parse_arguments()

    # Access the arguments
    input_cpp = args.input_cpp
    sampling_interval = args.sampling_interval
    output_cpp = args.output_cpp
    output_txt = args.output_txt

    # input_cpp = "/home/ani/Documents/Runtime_Verification/CS632_2025_assignment2/SUV/train_station_simulator.cpp"
    # sampling_interval = 50
    # output_cpp = "/home/ani/Documents/Runtime_Verification/CS632_2025_assignment2/Tooled_SUV/tooled_file_3.cpp"
    # output_txt = "/home/ani/Documents/Runtime_Verification/CS632_2025_assignment2/Tooled_SUV/output.txt"

    print(f'Input C++ file: {input_cpp}')
    print(f'Sampling interval: {sampling_interval} ms')
    print(f'Output C++ file: {output_cpp}')
    print(f'Output text file: {output_txt}')

    
    instrument_cpp_file(input_cpp, sampling_interval, output_cpp, output_txt)



if __name__ == '__main__':
    main()


