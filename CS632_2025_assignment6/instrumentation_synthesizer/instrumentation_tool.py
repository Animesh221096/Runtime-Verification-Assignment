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
    
    parser.add_argument('hostname', type=str, 
                        help='Hostname for the socket connection')
    parser.add_argument('port', type=int, 
                        help='Port number for the socket connection')

    # Parse the arguments
    return parser.parse_args()



def instrument_cpp_file(input_file, sampling_interval, output_cpp, output_txt, hostname, port):    # Read the input C++ file
    with open(input_file, 'r') as f:
        lines = f.readlines()

    variables_to_instrument = []



    new_libs_to_add = f"""#include <iostream>
#include <stdlib.h>
#include <pthread.h>
#include <time.h>
#include <atomic>
#include <cstring>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>
#include <unistd.h>
#include <fstream>\n
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
            if i + 1 < len(lines):  # Ensure there is a next line
                variable_line = lines[i + 1].strip()
                # Extract the variable name for both bool and int types
                match = re.search(r'\b(int|bool)\s+(\w+)\s*=\s*(true|false|\d+);\s*', variable_line)
                if match:
                    variables_to_instrument.append(match.group(2))  # Append the variable name



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



    join_log_thread = f"""\n    logging_active = false;
    pthread_join(log_thread, NULL);\n"""

    for i, line in enumerate(lines):
        if "exit(EXIT_SUCCESS);" in line:
            lines.insert(i-1, join_log_thread)
            break

    lines.append("")


    socket_code = f"""
int create_socket(const char *hostname, int port)
{{
    int sockfd;
    struct sockaddr_in serv_addr;
    struct hostent *server;

    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0)
    {{
        perror("ERROR opening socket");
        exit(EXIT_FAILURE);
    }}

    server = gethostbyname(hostname);
    if (server == NULL)
    {{
        fprintf(stderr, "ERROR, no such host\\n");
        exit(EXIT_FAILURE);
    }}

    bzero((char *)&serv_addr, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
    memcpy((char *)&serv_addr.sin_addr.s_addr, (char *)server->h_addr, server->h_length);
    serv_addr.sin_port = htons(port);

    if (connect(sockfd, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0)
    {{
        perror("ERROR connecting");
        exit(EXIT_FAILURE);
    }}

    return sockfd;
}}
"""
    
    lines.insert(-1, socket_code)


    # Create the instrumentation code to inject
    instrumentation_code = f"""
void *logVariables(void *Thread_Number)
{{
    int my_number = *(int *)Thread_Number;
    int sample_index = 0;
    int sockfd = create_socket("{hostname}", {port});
    std::ofstream outFile("{output_txt}");

    if (!outFile.is_open())
    {{
        std::cerr << "Unable to open file for writing." << std::endl;
        return NULL;
    }}

    outFile << "Observations" << std::endl;

    while (logging_active)
    {{
        sleep_ms({sampling_interval});
        
        string data = """

    # Add the instrumented variables to the logging code
    instrumentation_code += f"""to_string(sample_index) + "," +\n"""

    for var in variables_to_instrument:
        instrumentation_code += f"""            to_string({var}) + "," + \n"""
    


    instrumentation_code = instrumentation_code.rstrip("\",\" +\n")

    instrumentation_code += """;\n"""


    # instrumentation_code += "std::endl;\n "
    instrumentation_code += f"""
        sample_index++;
        // Send the data over the network
        int n = send(sockfd, data.c_str(), data.length(), 0);
        if (n < 0)
        {{
            perror("ERROR sending data");
            break; // Exit if sending fails
        }}

        // Log the data to the file
        outFile << data + "\\n";

        // Flush the output file to ensure data is written
        outFile.flush();
        
    }}
    close(sockfd);
    outFile.close();

    return NULL;

}}
"""

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
    hostname = args.hostname
    port = args.port

    print(f'Input C++ file: {input_cpp}')
    print(f'Sampling interval: {sampling_interval} ms')
    print(f'Output C++ file: {output_cpp}')
    print(f'Output text file: {output_txt}')
    print(f'Hostname: {hostname}')
    print(f'Port: {port}')

    instrument_cpp_file(input_cpp, sampling_interval, output_cpp, output_txt, hostname, port)


if __name__ == '__main__':
    main()


