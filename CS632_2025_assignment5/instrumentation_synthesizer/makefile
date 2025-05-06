# Python script name
PYTHON_SCRIPT = instrumentation_tool.py

INPUT_CPP = /home/ani/Documents/Runtime_Verification/CS632_2025_assignment5/SUV/train_station_simulator_racy_SHED.cpp
OUTPUT_CPP = /home/ani/Documents/Runtime_Verification/CS632_2025_assignment5/Tooled_SUV/tooled_file_socket_racy_SHED.cpp
OUTPUT_TXT = /home/ani/Documents/Runtime_Verification/CS632_2025_assignment5/Tooled_SUV/output_from_tooled_racy_SHED.txt


# Default values for parameters
# INPUT_CPP = /home/ani/Documents/Runtime_Verification/CS632_2025_assignment5/SUV/train_station_simulator_SHED.cpp
SAMPLING_INTERVAL = 50
# OUTPUT_CPP = /home/ani/Documents/Runtime_Verification/CS632_2025_assignment5/Tooled_SUV/tooled_file_socket_SHED.cpp
# OUTPUT_TXT = /home/ani/Documents/Runtime_Verification/CS632_2025_assignment5/Tooled_SUV/output_from_tooled_SHED.txt
HOSTNAME = ani-Dell-G15-5510
PORT = 51717

# Target with hardcoded parameters
run_local_test:
	python3 $(PYTHON_SCRIPT) $(INPUT_CPP) $(SAMPLING_INTERVAL) $(OUTPUT_CPP) $(OUTPUT_TXT) $(HOSTNAME) $(PORT)

# Target that accepts parameters from command line
run:
	@if [ -z "$(input_cpp)" ] || [ -z "$(sampling_interval)" ] || [ -z "$(output_cpp)" ] || [ -z "$(output_txt)" ] || [ -z "$(hostname)" ] || [ -z "$(port)" ]; then \
		echo "Usage: make run_with_params input_cpp=<input_cpp> sampling_interval=<sampling_interval> output_cpp=<output_cpp> output_txt=<output_txt> hostname=<hostname> port=<port>"; \
		exit 1; \
	fi
	python3 $(PYTHON_SCRIPT) $(input_cpp) $(sampling_interval) $(output_cpp) $(output_txt) $(hostname) $(port)

# Help target
help:
	@echo "Available targets:"
	@echo "  run_local_test      : Run the script with hardcoded parameters"
	@echo "  run                 : Run the script with parameters from command line"
	@echo "    Usage: make run_with_params input_cpp=<input_cpp> sampling_interval=<sampling_interval> output_cpp=<output_cpp> output_txt=<output_txt> hostname=<hostname> port=<port>"
	@echo "  help                : Show this help message"

.PHONY: run_local_test run help
