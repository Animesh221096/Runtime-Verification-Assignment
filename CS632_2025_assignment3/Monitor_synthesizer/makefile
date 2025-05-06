# Python script name
PYTHON_SCRIPT = monitor_tool.py

# Default values for parameters
PORT = 51717
OUTPUT_CPP = /home/ani/Documents/Runtime_Verification/CS632_2025_assignment3/Monitor/monitor.cpp

# Target with hardcoded parameters
run_tool_local_test:
	python3 $(PYTHON_SCRIPT) $(PORT) $(OUTPUT_CPP)

# Target that accepts parameters from command line
run_tool:
	@if [ -z "$(port)" ] || [ -z "$(output_cpp)" ]; then \
		echo "Usage: make run_tool port=<port> output_cpp=<output_cpp>"; \
		exit 1; \
	fi
	python3 $(PYTHON_SCRIPT) $(port) $(output_cpp)

# Help target
help:
	@echo "Available targets:"
	@echo "  run_tool_local_test : Run the script with hardcoded parameters"
	@echo "  run_tool            : Run the script with parameters from command line"
	@echo "    Usage: make run_tool port=<port> output_cpp=<output_cpp>"
	@echo "  help                : Show this help message"

.PHONY: run_tool_local_test run_tool help
