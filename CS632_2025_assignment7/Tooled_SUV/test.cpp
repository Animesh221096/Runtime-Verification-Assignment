#include <iostream>
#include <string>
#include <cstring>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>

int main() {
    int sock;
    struct sockaddr_in server;
    char server_ip[] = "127.0.0.1"; // Change this to the server's IP if needed
    int port = 51717; // Change this to the port number used by the server

    // Create socket
    sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock == -1) {
        std::cerr << "Could not create socket" << std::endl;
        return 1;
    }

    server.sin_family = AF_INET;
    server.sin_port = htons(port);
    server.sin_addr.s_addr = inet_addr(server_ip);

    // Connect to remote server
    if (connect(sock, (struct sockaddr *)&server, sizeof(server)) < 0) {
        std::cerr << "Connection failed" << std::endl;
        return 1;
    }

    std::cout << "Connected to server." << std::endl;

    while (true) {
        std::string user_input;
        std::cout << "Enter input to send to the server (or 'exit' to quit): ";
        std::getline(std::cin, user_input);

        // Check for exit condition
        if (user_input == "exit") {
            break;
        }

        // Send data to server
        if (send(sock, user_input.c_str(), user_input.length(), 0) < 0) {
            std::cerr << "Send failed" << std::endl;
            break;
        }

        // Optionally, you can print a confirmation message
        std::cout << "Sent: " << user_input << std::endl;
    }

    close(sock);
    return 0;
}
