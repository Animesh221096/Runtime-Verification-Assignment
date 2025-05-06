# Python script name
PYTHON_SCRIPT = tool.py

# Default values for parameters
INPUT_CPP = /home/ani/Documents/Runtime_Verification/CS632_2025_assignment2/SUV/train_station_simulator.cpp
SAMPLING_INTERVAL = 50
OUTPUT_CPP = /home/ani/Documents/Runtime_Verification/CS632_2025_assignment2/Tooled_SUV/tooled_file.cpp
OUTPUT_TXT = /home/ani/Documents/Runtime_Verification/CS632_2025_assignment2/Tooled_SUV/output.txt

# Target with hardcoded parameters
run_tool_local_test:
	python3 $(PYTHON_SCRIPT) $(INPUT_CPP) $(SAMPLING_INTERVAL) $(OUTPUT_CPP) $(OUTPUT_TXT)

# Target that accepts parameters from command line
run_tool:
	@if [ -z "$(input_cpp)" ] || [ -z "$(sampling_interval)" ] || [ -z "$(output_cpp)" ] || [ -z "$(output_txt)" ]; then \
		echo "Usage: make run_with_params input_cpp=<input_cpp> sampling_interval=<sampling_interval> output_cpp=<output_cpp> output_txt=<output_txt>"; \
		exit 1; \
	fi
	python3 $(PYTHON_SCRIPT) $(input_cpp) $(sampling_interval) $(output_cpp) $(output_txt)

# Help target
help:
	@echo "Available targets:"
	@echo "  run_local_test      : Run the script with hardcoded parameters"
	@echo "  run                 : Run the script with parameters from command line"
	@echo "    Usage: make run_with_params input_cpp=<input_cpp> sampling_interval=<sampling_interval> output_cpp=<output_cpp> output_txt=<output_txt>"
	@echo "  help                : Show this help message"

.PHONY: run_tool_local_test run_tool help
