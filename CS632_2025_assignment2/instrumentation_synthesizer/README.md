Instrumentation Synthesizer code goes here

├── Assignment1.pdf
├── Assignment2.pdf
├── instrumentation_synthesizer
│   ├── makefile
│   ├── README
│   └── tool.py
├── Monitor_synthesizer
│   └── README
├── README.md
├── SUV
│   ├── makefile
│   ├── train_station_simulator.cpp
│   └── train_station_simulator_racy_logic.cpp
└── Tooled_SUV
    ├── makefile
    └── train_station_simulator_ref.cpp

The Python script `tool.py` accepts the following command-line arguments:

- `input_cpp`: Path to the input C++ file to be instrumented.
- `sampling_interval`: Sampling interval in milliseconds.
- `output_cpp`: Path for the output instrumented C++ file.
- `output_txt`: Path for the output text file where variable values will be logged.

before running the make file make sure the SUV is in the deafult format as after Ctrl + Shift + I in VS Code

Run with Custom Parameters:

make run input_cpp=<path_to_input_cpp> sampling_interval=<interval> output_cpp=<path_to_output_cpp> output_txt=<path_to_output_txt>

Replace <path_to_input_cpp>, <interval>, <path_to_output_cpp>, and <path_to_output_txt> with your desired values.

then compile and run the generated <output_cpp>