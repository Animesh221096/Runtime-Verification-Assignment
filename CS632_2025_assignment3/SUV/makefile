build_racy_logic: train_station_simulator_racy_logic.cpp
	g++ train_station_simulator_racy_logic.cpp -o train_station_simulator_racy_logic.out

run_racy_logic: build_racy_logic
	./train_station_simulator_racy_logic.out


build: train_station_simulator.cpp
	g++ train_station_simulator.cpp -o train_station_simulator.out

run: build
	./train_station_simulator.out

clean:
	rm *.out