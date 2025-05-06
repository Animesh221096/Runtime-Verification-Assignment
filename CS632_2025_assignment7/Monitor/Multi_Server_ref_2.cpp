#include <iostream>
#include <fstream>
#include <cstring>
#include <cstdlib>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>

#include <sstream>
#include <vector>

void error(const char *msg)
{
    perror(msg);
    exit(1);
}

bool EvaluateOutput(const std::string &inputString, int num_of_booleans, int num_of_integers,
                    bool *booleanArray, int *integerArray)
{
    // Split the input string by commas
    std::stringstream ss(inputString);
    std::string token;
    std::vector<std::string> tokens;

    while (std::getline(ss, token, ','))
    {
        tokens.push_back(token);
    }

    // Check if we have enough tokens
    if (tokens.size() < (num_of_booleans + num_of_integers))
    {
        std::cerr << "Error: Not enough values provided." << std::endl;
        return false; // or handle the error as needed
    }

    // Process boolean values
    for (int i = 0; i < num_of_booleans; i++)
    {
        if (tokens[i + 1] == "1")
        {
            booleanArray[i] = true;
        }
        else if (tokens[i + 1] == "0")
        {
            booleanArray[i] = false;
        }
        else
        {
            std::cerr << i + 1 << " " << tokens[i+1] << " Error: Invalid character for boolean value. Expected '0' or '1'." << std::endl;
            return false; // or handle the error as needed
        }
    }

    // Process integer values
    for (int i = 0; i < num_of_integers; i++)
    {
        try
        {
            integerArray[i] = std::stoi(tokens[num_of_booleans + i]);
        }
        catch (const std::invalid_argument &)
        {
            std::cerr << "Error: Invalid integer value." << std::endl;
            return false; // or handle the error as needed
        }
        catch (const std::out_of_range &)
        {
            std::cerr << "Error: Integer value out of range." << std::endl;
            return false; // or handle the error as needed
        }
    }

    // Example condition: return true if the third boolean and the sixth boolean are both true
    // return ( (booleanArray[2] && booleanArray[5]) || (integerArray[0] < 0) || (integerArray[1] < 0) || ((booleanArray[2] || booleanArray[5]) && (integerArray[0] + integerArray[1] > integerArray[2]) ) );
    return ( (integerArray[0] < 0) || (integerArray[1] < 0) || ((booleanArray[2] || booleanArray[5]) && (integerArray[0] + integerArray[1] > integerArray[2]) ) );
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

    int num_of_booleans = 6;
    int num_of_integers = 2;

    bool booleanArray[6];

    int integerArray[2];
    bool Verdict;

    while (true)
    {
        bzero(buffer, 256);
        n = read(newsockfd, buffer, 255);
        if (n <= 0)
        {
            // If n is 0, the client has closed the connection
            break;
        }

        // Process the received boolean values
        Verdict = EvaluateOutput(buffer, num_of_booleans, num_of_integers, booleanArray, integerArray);

        std::cout << "Received booleans: " << buffer << ", " << Verdict << std::endl; // Print all booleans received

        // Log the received data to the file
        logFile << buffer << ", " << Verdict << std::endl; // Write to the file
        logFile.flush();                                   // Ensure data is written to the file immediately

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
