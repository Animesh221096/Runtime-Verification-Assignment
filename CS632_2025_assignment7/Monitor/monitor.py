import socket
import threading


import re
from pprint import pprint
from pydantic import BaseModel, ValidationError
from typing import Dict
import subprocess


def ltl2ba_to_dict(ltl2ba_output):
    # Initialize the dictionary
    state_dict = {}
    
    # Split the output into lines
    lines = ltl2ba_output.strip().splitlines()
    
    # Initialize variables
    current_state = None
    
    for line in lines:
        line = line.strip()
        
        # Match state definitions
        state_match = re.match(r'(\w+):', line)
        if state_match:
            current_state = state_match.group(1)
            state_dict[current_state] = {'transitions': [], 'markers': []}  # Initialize with a transitions list
            continue
        
        # Match transitions
                
        skip_match = re.match(r'skip', line)
        if skip_match:
            state_dict[current_state]['transitions'].append(('(1)', current_state))
            continue
        
        transition_match = re.match(r'::\s*(.*?)\s*->\s*goto\s*(\w+)', line)
        if transition_match and current_state is not None:
            condition = transition_match.group(1)
            next_state = transition_match.group(2)
            # Append the transition as a dictionary
            state_dict[current_state]['transitions'].append((condition, next_state))
    
    return state_dict

""" ---- ---- ---- ---- X ---- ---- ---- ----"""

def has_cycle_or_self_loop(state, state_dict, visited, stack):
    
    # Perform DFS to find cycles
    visited.add(state)
    stack.add(state)
    
    if not state_dict.get(state, {}).get('transitions', []):
        return False
    
    for _, next_state in state_dict.get(state, {}).get('transitions', []):
        if next_state not in visited:
            if has_cycle_or_self_loop(next_state, state_dict, visited, stack):
                return True
        elif next_state in stack:
            return True
    
    stack.remove(state)
    return False

def mark_accept_state_with_cycles(state_dict):
    Marked_dict = state_dict.copy()
    
    set_of_accepting_state = {state: transitions for state, transitions in state_dict.items() if 'accept' in state}
    
    for state in set_of_accepting_state:
        visited = set()
        stack = set()
        if has_cycle_or_self_loop(state, state_dict, visited, stack):
            Marked_dict[state]["markers"].append("Accept with Loop")
    
    return Marked_dict

""" ---- ---- ---- ---- X ---- ---- ---- ----"""

def can_reach_accepting_states(start_state, state_dict, nba_accepting_states):
    # Use a stack for DFS
    stack = [start_state]
    visited = set()

    while stack:
        current_state = stack.pop()
        
        # If we reach an accepting state, return True
        if current_state in nba_accepting_states:
            return True
        
        # Mark the current state as visited
        if current_state not in visited:
            visited.add(current_state)
            # Add all reachable states from the current state to the stack
            for next_state in state_dict.get(current_state, {}).get('transitions', []):
                next_state_name = next_state[1]
                if next_state_name not in visited:
                    stack.append(next_state_name)

    # If we exhaust all reachable states without finding an accepting state, return False
    return False

def mark_reachable_states(state_dict):

    # Identify accepting states
    nba_accepting_states = {state for state in state_dict if any("Accept with Loop" in marker for marker in state_dict[state]['markers'])}
    
    # Set to hold all reachable states
    Marked_reachable_states = state_dict.copy()
    
    # Check reachability from each accepting state
    for start_state in Marked_reachable_states:
        if can_reach_accepting_states(start_state, state_dict, nba_accepting_states):
            Marked_reachable_states[start_state]['markers'].append("Can Reach Accepting State With Loop")
    

    return Marked_reachable_states

""" ---- ---- ---- ---- X ---- ---- ---- ----"""

def remove_non_reachable_states(state_dict):
    # Create a new dictionary to hold only the states that have the marker
    filtered_states = {}
    
    # First, identify the states that should be kept
    for state, transitions in state_dict.items():
        if any("Can Reach Accepting State With Loop" in marker for marker in transitions['markers']):
            filtered_states[state] = transitions
    
    # Now, update the transitions of the remaining states
    for state in filtered_states:
        # Filter transitions to only include those that lead to the remaining states
        filtered_states[state]['transitions'] = [
            next_state for next_state in state_dict[state]['transitions']
            if next_state[1] in filtered_states
        ]
    
    return filtered_states

""" ---- ---- ---- ---- X ---- ---- ---- ----"""

def find_initial_state(nba):
    # Search for the initial state that contains "init"
    for state in nba:
        if 'init' in state:
            return state
    return None  # Return None if no initial state is found


def run_nba(nba, not_nba, atomic_propositions):
    # Set of active states
    
    Output = {"nba" : True, "not_nba" : True}
    
    nba_initial_state = find_initial_state(nba)    
    if nba_initial_state is None:
        print("No initial state found in nba")
        Output['nba'] = False
    
    not_nba_initial_state = find_initial_state(not_nba)    
    if not_nba_initial_state is None:
        print("No initial state found in not_nba")
        Output['not_nba'] = False
        
    if (not Output['nba']) and (not Output["not_nba"]):
        yield Output
    
    nba_active_states = {nba_initial_state}
    not_nba_active_states = {not_nba_initial_state}
    
    nba_accepting_states = {state for state, transitions in nba.items() if 'Accept with Loop' in transitions['markers']}
    not_nba_accepting_states = {state for state, transitions in nba.items() if 'Accept with Loop' in transitions['markers']}
    
    # Process each atomic proposition
    for prop in atomic_propositions:
        nba_next_active_states = set()
        not_nba_next_active_states = set()
        
        # Transition to the next states based on the current active states
        for nba_state, not_nba_state in zip(nba_active_states, not_nba_active_states):
            for nba_condition, nba_next_state, not_nba_condition, not_nba_next_state in zip(nba.get(nba_state, {}).get('transitions', []), not_nba.get(not_nba_state, {}).get('transitions', [])):
                # Check if the condition matches the current atomic proposition
                if nba_condition == '(1)' or prop in nba_condition:  # Assuming condition can be a simple match
                    nba_next_active_states.add(nba_next_state)
                    
                if not_nba_condition == '(1)' or prop in not_nba_condition:  # Assuming condition can be a simple match
                    not_nba_next_active_states.add(not_nba_next_state)
        
        # Update active states
        nba_active_states = nba_next_active_states
        not_nba_active_states = not_nba_next_active_states
        
        # If there are no active states left, we can stop early
        if not nba_active_states and not not_nba_active_states:
            break
    
    # Check if any of the active states are accepting states
    Output["nba"] = nba_active_states & nba_accepting_states
    Output["not_nba"] = not_nba_active_states & not_nba_accepting_states
    
    yield Output

""" ---- ---- ---- ---- X ---- ---- ---- ----"""


def handle_client_connection(client_socket, num_of_booleans, nba, not_nba):
    log_file = open("received_data.txt", "a")  # Open in append mode
    
    Output = {"nba": True, "not_nba": True}
    
    nba_initial_state = find_initial_state(nba)    
    if nba_initial_state is None:
        print("No initial state found in nba")
        Output['nba'] = False
    
    not_nba_initial_state = find_initial_state(not_nba)    
    if not_nba_initial_state is None:
        print("No initial state found in not_nba")
        Output['not_nba'] = False
        
    nba_active_states = {nba_initial_state}
    not_nba_active_states = {not_nba_initial_state}
    
    nba_accepting_states = {state for state, transitions in nba.items() if 'Accept with Loop' in transitions['markers']}
    not_nba_accepting_states = {state for state, transitions in nba.items() if 'Accept with Loop' in transitions['markers']}
    
    while True:
        print()
        print("---- ---- ---- ---- X ---- ---- ---- ----")
        print()
        print(nba_active_states)
        print(not_nba_active_states)
        print()
        
        buffer = client_socket.recv(256).decode('utf-8')
        if not buffer:
            # If buffer is empty, the client has closed the connection
            break

        tokens = buffer.split(',')
        
        # Check if we have enough tokens
        if len(tokens) - 1 < num_of_booleans:
            print("Error: Not enough values provided.")
            continue  # Skip to the next iteration if not enough tokens
            
        boolean_dict = {f"b{i}": tokens[i + 1] for i in range(len(tokens) - 1)}
        
        print(boolean_dict)
        
        nba_next_active_states = set()
        not_nba_next_active_states = set()
                
        # Transition to the next states based on the current active states
        for nba_state in nba_active_states:
            for condition, next_state in nba[nba_state]['transitions']:
                # Check if the condition matches the current boolean values
                if evaluate_condition(condition, boolean_dict):
                    nba_next_active_states.add(next_state)
        
        for not_nba_state in not_nba_active_states:
            for condition, next_state in not_nba[not_nba_state]['transitions']:
                # Check if the condition matches the current boolean values
                if evaluate_condition(condition, boolean_dict):
                    not_nba_next_active_states.add(next_state)
        
        # Update active states
        nba_active_states = nba_next_active_states
        not_nba_active_states = not_nba_next_active_states
        
        # Check if any of the active states are accepting states
        Output["nba"] = bool(nba_active_states & nba_accepting_states)
        Output["not_nba"] = bool(not_nba_active_states & not_nba_accepting_states)

        verdict = Output

        print(f"Received booleans: {buffer}, {verdict}")  # Print all booleans received
        
        # Check for acceptance
        if 'accept_all' in nba_active_states:
            print("The A NBA has accepted.")
        elif not nba_active_states:
            print("The A NBA has rejected.")
            
        # Check for acceptance
        if 'accept_all' in not_nba_active_states:
            print("The A not NBA has accepted.")
        elif not not_nba_active_states:
            print("The A not NBA has rejected.")

        # Log the received data to the file
        log_file.write(f"{buffer}, {verdict}\n")  # Write to the file
        log_file.flush()  # Ensure data is written to the file immediately

        # Send a response back to the client
        client_socket.sendall(b"Received")

    log_file.close()  # Close the log file
    client_socket.close()  # Close the client socket

def evaluate_condition(condition, boolean_dict):
    # Replace C-style boolean operators with Python equivalents
    python_expression = condition.replace('&&', ' and ') \
                                 .replace('||', ' or ') \
                                 .replace('!', ' not ')
    
    # Replace boolean variables with their values from the boolean_dict
    for key, value in boolean_dict.items():
        python_expression = python_expression.replace(key, str(value))
    
    # Evaluate the expression safely
    try:
        return eval(python_expression)
    except Exception as e:
        print(f"Error evaluating expression '{python_expression}': {e}")
        return False



def main(port, num_of_booleans, ltl_property):

    print(f"\n---- ---- ---- ---- X ---- ---- ---- ----\n\nProcessing LTL property: {ltl_property}")
    
    try:
        # Run the ltl2ba tool
        result_phi = subprocess.run(['./ltl2ba', '-f', ltl_property], capture_output=True, text=True, check=True)
        LTL2BA_Output_phi = result_phi.stdout  # Get the output from the command
        print(LTL2BA_Output_phi)
        
        result_not_phi = subprocess.run(['./ltl2ba', '-f', f"!({ltl_property})"], capture_output=True, text=True, check=True)
        LTL2BA_Output_not_phi = result_not_phi.stdout  # Get the output from the command
        print(LTL2BA_Output_not_phi)
        
        print()
        
        # Convert the LTL2BA output to a dictionary
        NBA_for_phi = ltl2ba_to_dict(LTL2BA_Output_phi)
        print("NBA for phi")
        pprint(NBA_for_phi)
        
        # Convert the LTL2BA output to a dictionary
        NBA_for_not_phi = ltl2ba_to_dict(LTL2BA_Output_not_phi)
        print("NBA for not phi")
        pprint(NBA_for_not_phi)
        
        print()
        
        # Continue with the rest of the processing as before...
        Intermidiate_NBA_for_phi = mark_accept_state_with_cycles(NBA_for_phi)
        print("NBA for phi with marked accept state which are part of a cycle")
        pprint(Intermidiate_NBA_for_phi)
        
        # Continue with the rest of the processing as before...
        Intermidiate_NBA_for_not_phi = mark_accept_state_with_cycles(NBA_for_not_phi)
        print("NBA for not phi with marked accept state which are part of a cycle")
        pprint(Intermidiate_NBA_for_not_phi)
        
        print()
        
        Intermidiate_NBA_for_A_phi = mark_reachable_states(Intermidiate_NBA_for_phi)
        print("Intermidiate NBA for A_phi")
        pprint(Intermidiate_NBA_for_A_phi)
        
        Intermidiate_NBA_for_A_not_phi = mark_reachable_states(Intermidiate_NBA_for_not_phi)
        print("Intermidiate NBA for A_not_phi")
        pprint(Intermidiate_NBA_for_A_not_phi)
        
        print()
        
        NBA_for_A_phi = remove_non_reachable_states(Intermidiate_NBA_for_A_phi)
        print("Final NBA for A_phi after removing non-reachable states")
        pprint(NBA_for_A_phi)
        
        NBA_for_A_not_phi = remove_non_reachable_states(Intermidiate_NBA_for_A_not_phi)
        print("Final NBA for A_phi after removing non-reachable states")
        pprint(NBA_for_A_not_phi)
        
        print()
        
        print(f"\n---- ---- ---- ---- X ---- ---- ---- ----\n\nProcessed LTL property: {ltl_property}")
    
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while processing LTL property '{ltl_property}': {e.stderr}")

    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', port))
    server_socket.listen(1)
    print(f"Server listening on port {port}")

    client_socket, addr = server_socket.accept()
    print(f"Connection from {addr}")
    handle_client_connection(client_socket, num_of_booleans, NBA_for_A_phi, NBA_for_A_not_phi)

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("ERROR, no port or number of booleans provided")
        sys.exit(1)

    port_number = int(sys.argv[1])
    num_of_booleans = int(sys.argv[2])
    ltl_property = sys.argv[3]
    main(port_number, num_of_booleans, ltl_property)