import os
import sys
import argparse

def create_monitor_cpp(portno, output_path, num_of_booleans):
    lib_required = f"""#include <iostream>
#include <fstream>
#include <cstring>
#include <cstdlib>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>

void error(const char *msg)
{{
    perror(msg);
    exit(1);
}}

bool EvaluateOutput(const std::string &inputString, int num_of_booleans)
{{
    size_t commaPos = inputString.find(',');

    // Extract the two values based on the position of the comma
    std::string result[2];
    result[0] = inputString.substr(0, commaPos);
    result[1] = inputString.substr(commaPos + 1);

    // Separate the second value into individual characters
    bool secondValueBits[num_of_booleans];
    for (int i = 0; i < num_of_booleans; i++)
    {{
        secondValueBits[i] = (result[1][i] == '1');
    }}

    return (secondValueBits[2] && secondValueBits[5]);
}}

int main(int argc, char *argv[])
{{
    int sockfd, newsockfd;
    socklen_t clilen;
    char buffer[256];
    struct sockaddr_in serv_addr, cli_addr;
    int n;

    // Check for port number argument
    // if (argc < 2)
    // {{
    //    std::cerr << "ERROR, no port provided" << std::endl;
    //    exit(1);
    // }}

    // Create socket
    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0)
    {{
        error("ERROR opening socket");
    }}

    // Set up the server address structure
    bzero((char *)&serv_addr, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_addr.s_addr = INADDR_ANY;
    serv_addr.sin_port = htons({portno}); // Use the parsed port number

    // Bind the socket
    if (bind(sockfd, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0)
    {{
        error("ERROR on binding");
    }}

    // Listen for incoming connections
    listen(sockfd, 5);
    clilen = sizeof(cli_addr);
    newsockfd = accept(sockfd, (struct sockaddr *)&cli_addr, &clilen);
    if (newsockfd < 0)
    {{
        error("ERROR on accept");
    }}

    // Open a file to log received data using std::ofstream
    std::ofstream logFile("received_data.txt", std::ios::out | std::ios::trunc); // Open in append mode
    if (!logFile.is_open())
    {{
        error("ERROR opening file for writing");
    }}

    int num_of_booleans = {num_of_booleans};
    bool Verdict;

    while (true) {{
        bzero(buffer, 256);
        n = read(newsockfd, buffer, 255);
        if (n <= 0) {{
            // If n is 0, the client has closed the connection
            break;
        }}

        // Process the received boolean values
        Verdict = EvaluateOutput(buffer, num_of_booleans);
        std::cout << "Received data: " << buffer << ", Verdict: " << Verdict << std::endl; // Print all booleans received

        // Log the received data to the file
        logFile << buffer << ", " << Verdict << std::endl; // Write to the file
        logFile.flush(); // Ensure data is written to the file immediately

        // Send a response back to the client
        n = write(newsockfd, "Received", 8);
        if (n < 0)
        {{
            error("ERROR writing to socket");
        }}
    }}

    // Clean up
    logFile.close(); // Close the log file
    close(newsockfd);
    close(sockfd);
    return 0;
}}
"""

    # Write the generated C++ code to the specified output path
    with open(output_path, 'w') as f:
        f.write(lib_required)
    print(f"C++ code has been written to {output_path}")

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Create a C++ TCP server monitor.')
    parser.add_argument('port', type=int, help='Port number for the server to listen on')
    parser.add_argument('output_path', type=str, help='Absolute path to the output file for the C++ code')
    parser.add_argument('num_of_booleans', type=int, help='Number of boolean values to expect')

    # Parse the arguments
    args = parser.parse_args()

    # Validate the output path
    if not os.path.isabs(args.output_path):
        print("ERROR: The output path must be an absolute path.")
        sys.exit(1)

    # Call the function to create the C++ code with the provided port number, output path, and number of booleans
    create_monitor_cpp(args.port, args.output_path, args.num_of_booleans)

if __name__ == '__main__':
    main()

