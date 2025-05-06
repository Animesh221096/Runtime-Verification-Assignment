#include <iostream>
#include <stdlib.h>
#include <pthread.h>
#include <time.h>
#include <atomic>
#include <cstring>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>
#include <unistd.h>
#include <fstream>

using namespace std;

void *logVariables(void *Thread_Number);
atomic<bool> logging_active(true);

// Function to sleep for a specified time in milliseconds
void sleep_ms(unsigned long milliseconds)
{
    struct timespec ts;
    ts.tv_sec = milliseconds / 1000ul;
    ts.tv_nsec = (milliseconds % 1000ul) * 1000000;
    nanosleep(&ts, NULL);
}

// Global flags to track train state (shared between threads)
// $TO_INSTRUMENT$
bool is_T0_running = false;
// $TO_INSTRUMENT$
bool is_T0_waiting_to_enter_station = false;
// $TO_INSTRUMENT$
bool is_T0_in_station = false;

// $TO_INSTRUMENT$
bool is_T1_running = false;
// $TO_INSTRUMENT$
bool is_T1_waiting_to_enter_station = false;
// $TO_INSTRUMENT$
bool is_T1_in_station = false;

// Mutex to control access to the station
pthread_mutex_t station_mutex = PTHREAD_MUTEX_INITIALIZER;

void *train_logic(void *train_number)
{
    int my_number = *(int *)train_number;
    bool *is_T_running;
    bool *is_T_in_station;
    bool *is_T_waiting_to_enter_station;

    // Select the correct train flags based on train number
    if (my_number == 0)
    {
        is_T_running = &is_T0_running;
        is_T_waiting_to_enter_station = &is_T0_waiting_to_enter_station;
        is_T_in_station = &is_T0_in_station;
    }
    else if (my_number == 1)
    {
        is_T_running = &is_T1_running;
        is_T_waiting_to_enter_station = &is_T1_waiting_to_enter_station;
        is_T_in_station = &is_T1_in_station;
    }

    int num_station_visits = 0;
    while (num_station_visits < 10)
    {
        // Run for some time (3-5 seconds)
        *is_T_running = true;
        *is_T_in_station = false;
        *is_T_waiting_to_enter_station = false;
        cout << "train " << my_number << " :   " << *is_T_running << "   :   " << *is_T_waiting_to_enter_station << "   :   " << *is_T_in_station << "\n";
        sleep_ms(3000 + clock() % 21 * 100);

        // Wait to enter the station
        *is_T_running = false;
        *is_T_in_station = false;
        *is_T_waiting_to_enter_station = true;
        cout << "train " << my_number << " :   " << *is_T_running << "   :   " << *is_T_waiting_to_enter_station << "   :   " << *is_T_in_station << "\n";

        // Acquire the mutex to enter the station
        pthread_mutex_lock(&station_mutex);

        // Now in the station (Only one train can be in the station at a time)
        *is_T_running = false;
        *is_T_in_station = true;
        *is_T_waiting_to_enter_station = false;
        cout << "train " << my_number << " :   " << *is_T_running << "   :   " << *is_T_waiting_to_enter_station << "   :   " << *is_T_in_station << "   : " << num_station_visits + 1 << "\n";
        sleep_ms(1000); // Stand in the station for 1 second

        // Release the mutex after leaving the station
        pthread_mutex_unlock(&station_mutex);

        num_station_visits++;
    }

    return NULL;
}

int main()
{
    pthread_t log_thread;
    int iret_log;
    int log_thread_number = 2147483647;

    // Create threads for logger
    iret_log = pthread_create(&log_thread, NULL, logVariables, &log_thread_number);
    if (iret_log)
    {
        fprintf(stderr, "Error - pthread_create() return code: %d\n", iret_log);
        exit(EXIT_FAILURE);
    }

    pthread_t thread0, thread1;
    int iret0, iret1;
    int thread_number0 = 0, thread_number1 = 1;

    cout << "t_num " << "  : " << "isT_r" << " : " << "isT_w" << " : " << "isT_s" << " : " << "Station_Visit" << "\n";

    sleep_ms(10);

    // Create threads for train 0 and train 1
    iret0 = pthread_create(&thread0, NULL, train_logic, &thread_number0);
    if (iret0)
    {
        fprintf(stderr, "Error - pthread_create() return code: %d\n", iret0);
        exit(EXIT_FAILURE);
    }

    iret1 = pthread_create(&thread1, NULL, train_logic, &thread_number1);
    if (iret1)
    {
        fprintf(stderr, "Error - pthread_create() return code: %d\n", iret1);
        exit(EXIT_FAILURE);
    }

    // Wait for both threads to finish execution
    pthread_join(thread0, NULL);
    pthread_join(thread1, NULL);

    // Destroy the mutex after use
    pthread_mutex_destroy(&station_mutex);

    logging_active = false;
    pthread_join(log_thread, NULL);

    exit(EXIT_SUCCESS);
}

int create_socket(const char *hostname, int port)
{
    int sockfd;
    struct sockaddr_in serv_addr;
    struct hostent *server;

    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0)
    {
        perror("ERROR opening socket");
        exit(EXIT_FAILURE);
    }

    server = gethostbyname(hostname);
    if (server == NULL)
    {
        fprintf(stderr, "ERROR, no such host\n");
        exit(EXIT_FAILURE);
    }

    bzero((char *)&serv_addr, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
    memcpy((char *)&serv_addr.sin_addr.s_addr, (char *)server->h_addr, server->h_length);
    serv_addr.sin_port = htons(port);

    if (connect(sockfd, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0)
    {
        perror("ERROR connecting");
        exit(EXIT_FAILURE);
    }

    return sockfd;
}

void *logVariables(void *Thread_Number)
{
    int my_number = *(int *)Thread_Number;
    int sample_index = 0;
    int sockfd = create_socket("localhost", 51717); // Change to your server's hostname and port
    std::ofstream outFile("/home/ani/Documents/Runtime_Verification/CS632_2025_assignment3/Tooled_SUV/output_from_tooled.txt"); // Create an output file stream

    if (!outFile.is_open())
    {
        std::cerr << "Unable to open file for writing." << std::endl;
        return NULL;
    }

    outFile << "Observations" << std::endl;

    while (logging_active)
    {
        sleep_ms(50);
        string data = to_string(sample_index) + ", " +
                      to_string(is_T0_running) + ", " +
                      to_string(is_T0_waiting_to_enter_station) + ", " +
                      to_string(is_T0_in_station) + ", " +
                      to_string(is_T1_running) + ", " +
                      to_string(is_T1_waiting_to_enter_station) + ", " +
                      to_string(is_T1_in_station) + "\n";

        sample_index++;
        // Send the data over the network
        int n = send(sockfd, data.c_str(), data.length(), 0);
        if (n < 0)
        {
            perror("ERROR sending data");
            break; // Exit if sending fails
        }

        // Log the data to the file
        outFile << data;

        // Flush the output file to ensure data is written
        outFile.flush();

    }
    close(sockfd);   // Close the socket when done
    outFile.close(); // Close the output file

    return NULL;
    
}
