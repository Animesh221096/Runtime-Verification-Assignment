#include<iostream>
#include<stdlib.h>
#include<pthread.h>
#include<time.h>
using namespace std;

void sleep_ms(unsigned long milliseconds)
{
	struct timespec ts;
	ts.tv_sec = milliseconds / 1000ul;
	ts.tv_nsec = (milliseconds % 1000ul) * 1000000;
	nanosleep(&ts, NULL);
}

// $TO_INSTRUMENT$
bool is_T0_running;
// $TO_INSTRUMENT$
bool is_T0_waiting_to_enter_station;
// $TO_INSTRUMENT$
bool is_T0_in_station;
// $TO_INSTRUMENT$
bool is_T1_running;
// $TO_INSTRUMENT$
bool is_T1_waiting_to_enter_station;
// $TO_INSTRUMENT$
bool is_T1_in_station;

void *train_logic(void *train_number)
{
	int my_number = *(int *)train_number;
	bool *is_T_running;
	bool *is_T_in_station;
	bool *is_T_waiting_to_enter_station;
	if(my_number == 0)
	{
		is_T_running = &is_T0_running;
		is_T_waiting_to_enter_station = &is_T0_waiting_to_enter_station;
		is_T_in_station = &is_T0_in_station;
	}
	else if(my_number == 1)
	{
		is_T_running = &is_T1_running;
		is_T_waiting_to_enter_station = &is_T1_waiting_to_enter_station;
		is_T_in_station = &is_T1_in_station;
	}
	int num_station_visits = 0;
	while(num_station_visits < 10)
	/*
	 * Note that typically we study systems that run infinitely.
	 * However, for the sake of this laboratory study, we will
	 * study finite runs.
	 */
	{
		//Run for some time in the range [3, 5] seconds. Running time in multiples of 100 milliseconds.
		*is_T_running = true;
		*is_T_in_station = false;
		*is_T_waiting_to_enter_station = false;
		cout << "train " << my_number << " : " << *is_T_running << " : " << *is_T_waiting_to_enter_station << " : " << *is_T_in_station << "\n";
		sleep_ms(3000 + clock()%21 * 100);

		//Wait to enter station
		*is_T_running = false;
		*is_T_in_station = false;
		*is_T_waiting_to_enter_station = true;
		cout << "train " << my_number << " : " << *is_T_running << " : " << *is_T_waiting_to_enter_station << " : " << *is_T_in_station << "\n";

		//Stand in the station for 1 second
		*is_T_running = false;
		*is_T_in_station = true;
		*is_T_waiting_to_enter_station = false;
		cout << "train " << my_number << " : " << *is_T_running << " : " << *is_T_waiting_to_enter_station << " : " << *is_T_in_station << "\n";
		sleep_ms(1000);

		num_station_visits++;
	}

	return NULL;
}

int main()
{
	pthread_t thread0, thread1;
	int  iret0, iret1;
	int thread_number0 = 0, thread_number1 = 1;

	cout << "train number"  << " : " << "is_T_running" << " : " << "is_T_waiting_to_enter_station" << " : " << "is_T_in_station" << "\n";


	iret0 = pthread_create(&thread0, NULL, train_logic, &thread_number0);
	if(iret0)
	{
		fprintf(stderr,"Error - pthread_create() return code: %d\n",iret0);
		exit(EXIT_FAILURE);
	}
	iret1 = pthread_create(&thread1, NULL, train_logic, &thread_number1);
	if(iret1)
	{
		fprintf(stderr,"Error - pthread_create() return code: %d\n",iret1);
		exit(EXIT_FAILURE);
	}

	pthread_join(thread0, NULL);
	pthread_join(thread1, NULL);

	exit(EXIT_SUCCESS);
}
