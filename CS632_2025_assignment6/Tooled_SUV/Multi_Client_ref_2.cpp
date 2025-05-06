#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>

void error(const char *msg)
{
    perror(msg);
    exit(0);
}

int main(int argc, char *argv[])
{
    int sockfd, portno, n;
    struct sockaddr_in serv_addr;
    struct hostent *server;

    char buffer[256];
    const int num_booleans = 6; // Predetermined number of booleans to send
    // if (argc < 3)
    // {
    //     fprintf(stderr, "usage %s hostname port\n", argv[0]);
    //     exit(0);
    // }
    // portno = atoi(argv[2]);
    portno = 51717;
    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0)
    {
        error("ERROR opening socket");
    }
    // server = gethostbyname(argv[1]);
    server = gethostbyname("ani-Dell-G15-5510");
    if (server == NULL)
    {
        fprintf(stderr, "ERROR, no such host\n");
        exit(0);
    }
    bzero((char *)&serv_addr, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
    memcpy((char *)&serv_addr.sin_addr.s_addr, (char *)server->h_addr, server->h_length);
    serv_addr.sin_port = htons(portno);
    if (connect(sockfd, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0)
    {
        error("ERROR connecting");
    }

    while (1) {
        // Prepare the buffer to send boolean values
        bzero(buffer, 256);
        printf("Enter %d boolean values (0 or 1) separated by spaces: ", num_booleans);
        
        for (int i = 0; i < num_booleans; i++) {
            int value;
            scanf("%d", &value);
            // Validate input
            if (value != 0 && value != 1) {
                printf("Invalid input. Please enter 0 or 1.\n");
                i--; // Decrement i to repeat this iteration
                continue;
            }
            // Append the boolean value to the buffer
            if (i > 0) {
                strcat(buffer, " "); // Add a space before the next value
            }
            char value_str[2];
            snprintf(value_str, sizeof(value_str), "%d", value);
            strcat(buffer, value_str);
        }

        // Send the boolean values to the server
        n = write(sockfd, buffer, strlen(buffer));
        if (n < 0)
        {
            error("ERROR writing to socket");
        }

        // Read the response from the server
        bzero(buffer, 256);
        n = read(sockfd, buffer, 255);
        if (n < 0)
        {
            error("ERROR reading from socket");
        }
        printf("Server response: %s\n", buffer);
    }

    close(sockfd);
    return 0;
}
