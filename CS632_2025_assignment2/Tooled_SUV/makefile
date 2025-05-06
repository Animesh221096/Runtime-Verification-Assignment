# Makefile for compiling and running tooled_file.cpp

# Compiler
CXX = g++

# Compiler flags
CXXFLAGS = -Wall -Wextra -std=c++11

# Source file
SRC = tooled_file.cpp

# Output executable
OUTPUT = tooled

# Default target
all: $(OUTPUT)

# Rule to compile the source file
$(OUTPUT): $(SRC)
	$(CXX) $(CXXFLAGS) -o $(OUTPUT) $(SRC)

# Rule to run the executable
run: $(OUTPUT)
	./$(OUTPUT)

# Clean up generated files
clean:
	rm -f $(OUTPUT)

.PHONY: all run clean
