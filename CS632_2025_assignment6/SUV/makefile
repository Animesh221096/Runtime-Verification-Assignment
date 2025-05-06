build_racy_logic: train_station_simulator_racy_logic.cpp
	g++ train_station_simulator_racy_logic.cpp -o train_station_simulator_racy_logic.out

run_racy_logic: build_racy_logic
	./train_station_simulator_racy_logic.out


build_SHED: train_station_simulator_SHED.cpp
	g++ train_station_simulator_SHED.cpp -o train_station_simulator_SHED.out

run_SHED: build_SHED
	./train_station_simulator_SHED.out



build_racy_SHED: train_station_simulator_racy_SHED.cpp
	g++ train_station_simulator_racy_SHED.cpp -o train_station_simulator_racy_SHED.out

run_racy_SHED: build_racy_SHED
	./train_station_simulator_racy_SHED.out



build: train_station_simulator.cpp
	g++ train_station_simulator.cpp -o train_station_simulator.out

run: build
	./train_station_simulator.out

clean:
	rm *.out