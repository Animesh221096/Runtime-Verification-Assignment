#include <iostream>
#include <stdlib.h>
#include <pthread.h>
#include <time.h>

#include <cmath>

using namespace std;

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
// pthread_mutex_t station_mutex = PTHREAD_MUTEX_INITIALIZER;

// $TO_INSTRUMENT$
int Steel_Shed = 0;
// $TO_INSTRUMENT$
int Coal_Shed = 0;
// $TO_INSTRUMENT$
int num_of_shed = 5;

// int shed_content = 0; // +2 for steel, -2 for coal

/*

    0   1

    E   E   0
    E   S   1
    E   C   -1

    S   S   2
    S   C   0

    C   C   -2

*/

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
        cout << (my_number == 1 ? "    " : "") << "train " << my_number << (my_number == 0 ? "    " : "") << " :   " << *is_T_running << "   :   " << *is_T_waiting_to_enter_station << "   :   " << *is_T_in_station << "\n";
        sleep_ms(3000 + (clock() % 21) * 100 * (1 + 9 * (my_number == 1)));
        // Wait to enter the station
        *is_T_running = false;
        *is_T_in_station = false;
        *is_T_waiting_to_enter_station = true;
        cout << (my_number == 1 ? "    " : "") << "train " << my_number << (my_number == 0 ? "    " : "") << " :   " << *is_T_running << "   :   " << *is_T_waiting_to_enter_station << "   :   " << *is_T_in_station << "\n";

        // Acquire the mutex to enter the station

        if (my_number == 0) // Train 0 brings steel
        {
            Steel_Shed += 1; // Unload steel
            Coal_Shed -= 1 - (Coal_Shed == 0);
            // cout << "\n\tTrain 0 unloaded steel. Shed content: " << shed_content << "\n\n";
            break;
        }
        else if (my_number == 1) // Train 1 brings coal
        {
            Coal_Shed += 1; // Unload coal
            Steel_Shed -= 1 - (Steel_Shed == 0);
            // cout << "\n\tTrain 1 unloaded coal. Shed content: " << shed_content << "\n\n";
            break;
        }

        // Now in the station (Only one train can be in the station at a time)
        *is_T_running = false;
        *is_T_in_station = true;
        *is_T_waiting_to_enter_station = false;
        cout << (my_number == 1 ? "    " : "") << "train " << my_number << (my_number == 0 ? "    " : "") << " :   " << *is_T_running << "   :   " << *is_T_waiting_to_enter_station << "   :   " << *is_T_in_station << "   :  " << num_station_visits + 1 << "  :  " << Steel_Shed << "  :  " << Coal_Shed << "\n";
        sleep_ms(1000); // Stand in the station for 1 second

        // Release the mutex after leaving the station
        // pthread_mutex_unlock(&station_mutex);

        num_station_visits++;
    }

    return NULL;
}

int main()
{
    pthread_t thread0, thread1;
    int iret0, iret1;
    int thread_number0 = 0, thread_number1 = 1;

    cout << "t_num     " << "  : " << "isT_r" << " : " << "isT_w" << " : " << "isT_s" << " : " << "S_V" << " : " << "S_S" << " : " << "C_S" << "\n";

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
    // pthread_mutex_destroy(&station_mutex);

    exit(EXIT_SUCCESS);
}
