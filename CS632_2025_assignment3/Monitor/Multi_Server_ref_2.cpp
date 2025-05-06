#include <iostream>
#include <fstream>
#include <cstring>
#include <cstdlib>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>

void error(const char *msg)
{
    perror(msg);
    exit(1);
}

int main(int argc, char *argv[])
{
    int sockfd, newsockfd, portno;
    socklen_t clilen;
    char buffer[256];
    struct sockaddr_in serv_addr, cli_addr;
    int n;

    // Check for port number argument
    if (argc < 2)
    {
        std::cerr << "ERROR, no port provided" << std::endl;
        exit(1);
    }

    // Create socket
    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0)
    {
        error("ERROR opening socket");
    }

    // Set up the server address structure
    bzero((char *)&serv_addr, sizeof(serv_addr));
    portno = atoi(argv[1]);
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_addr.s_addr = INADDR_ANY;
    serv_addr.sin_port = htons(portno);

    // Bind the socket
    if (bind(sockfd, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0)
    {
        error("ERROR on binding");
    }

    // Listen for incoming connections
    listen(sockfd, 5);
    clilen = sizeof(cli_addr);
    newsockfd = accept(sockfd, (struct sockaddr *)&cli_addr, &clilen);
    if (newsockfd < 0)
    {
        error("ERROR on accept");
    }

    // Open a file to log received data using std::ofstream
    std::ofstream logFile("received_data.txt", std::ios::app); // Open in append mode
    if (!logFile.is_open())
    {
        error("ERROR opening file for writing");
    }

    while (true) {
        bzero(buffer, 256);
        n = read(newsockfd, buffer, 255);
        if (n <= 0) {
            // If n is 0, the client has closed the connection
            break;
        }

        // Process the received boolean values
        std::cout << "Received booleans: " << buffer << std::endl; // Print all booleans received

        // Log the received data to the file
        logFile << buffer << std::endl; // Write to the file
        logFile.flush(); // Ensure data is written to the file immediately

        // Send a response back to the client
        n = write(newsockfd, "Received", 8);
        if (n < 0)
        {
            error("ERROR writing to socket");
        }
    }

    // Clean up
    logFile.close(); // Close the log file
    close(newsockfd);
    close(sockfd);
    return 0;
}
