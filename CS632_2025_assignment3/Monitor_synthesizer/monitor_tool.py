import re
import sys
import argparse
import os

def create_monitor_cpp(portno, output_path):
    lib_required = f"""
#include <iostream>
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

int main(int argc, char *argv[])
{{
    int sockfd, newsockfd;
    socklen_t clilen;
    char buffer[256];
    struct sockaddr_in serv_addr, cli_addr;
    int n;

    // Check for port number argument
    if (argc < 2)
    {{
        std::cerr << "ERROR, no port provided" << std::endl;
        exit(1);
    }}

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
    std::ofstream logFile("received_data.txt", std::ios::app); // Open in append mode
    if (!logFile.is_open())
    {{
        error("ERROR opening file for writing");
    }}

    while (true) {{
        bzero(buffer, 256);
        n = read(newsockfd, buffer, 255);
        if (n <= 0) {{
            // If n is 0, the client has closed the connection
            break;
        }}

        // Process the received boolean values
        std::cout << "Received booleans: " << buffer << std::endl; // Print all booleans received

        // Log the received data to the file
        logFile << buffer << std::endl; // Write to the file
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

    # Parse the arguments
    args = parser.parse_args()

    # Validate the output path
    if not os.path.isabs(args.output_path):
        print("ERROR: The output path must be an absolute path.")
        sys.exit(1)

    # Call the function to create the C++ code with the provided port number and output path
    create_monitor_cpp(args.port, args.output_path)

if __name__ == '__main__':
    main()
