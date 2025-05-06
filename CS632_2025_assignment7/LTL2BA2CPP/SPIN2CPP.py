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

def can_reach_accepting_states(start_state, state_dict, accepting_states):
    # Use a stack for DFS
    stack = [start_state]
    visited = set()

    while stack:
        current_state = stack.pop()
        
        # If we reach an accepting state, return True
        if current_state in accepting_states:
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
    accepting_states = {state for state in state_dict if any("Accept with Loop" in marker for marker in state_dict[state]['markers'])}
    
    # Set to hold all reachable states
    Marked_reachable_states = state_dict.copy()
    
    # Check reachability from each accepting state
    for start_state in Marked_reachable_states:
        if can_reach_accepting_states(start_state, state_dict, accepting_states):
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

def main():
    
    # ltl_properties = ["[]p", "![]p", "[]!p", "<>p", "!<>p", "<>!p", "p U q", "[] (p -> <> q)", "[]<>p && []<>q && [](!(p && q))",
    #                   "[]<>p", "!([]<>p)", "<>[]p", "!(<>[]p)",
    #                   "(train_0_in_station -> <> (num_of_steel_shed_more_than_0 || num_of_empty_shed_more_than_0)) && (train_1_in_station -> <> (num_of_coal_shed_more_than_0 || num_of_empty_shed_more_than_0))",
    #                   "!(train_0_in_station -> <> (num_of_steel_shed_more_than_0 || num_of_empty_shed_more_than_0)) && (train_1_in_station -> <> (num_of_coal_shed_more_than_0 || num_of_empty_shed_more_than_0))"]

    ltl_properties = ["(b2 -> <> (b6 || b8)) && (b1 -> <>(b7 || b8))"]
    
    for property in ltl_properties:
        temp = ltl_properties.pop()
        neg_temp = f"!({temp})"
        ltl_properties.append([temp, neg_temp])


    for property in ltl_properties:
        for i in range(len(property)):
            formula_string = property[i]
            print(f"\n---- ---- ---- ---- X ---- ---- ---- ----\n\nProcessing LTL property: {formula_string}")
            
            if i == 1:
                nba_label = "not phi"
            else:
                nba_label = "phi"
            
            try:
                # Run the ltl2ba tool
                result = subprocess.run(['./ltl2ba', '-f', formula_string], capture_output=True, text=True, check=True)
                LTL2BA_Output = result.stdout  # Get the output from the command
                print(LTL2BA_Output)
                
                print()
                
                # Convert the LTL2BA output to a dictionary
                NBA_for_phi = ltl2ba_to_dict(LTL2BA_Output)
                print(f"NBA for {nba_label}")
                pprint(NBA_for_phi)
                
                print()
                
                # Continue with the rest of the processing as before...
                Intermidiate_NBA_for_phi = mark_accept_state_with_cycles(NBA_for_phi)
                print(f"NBA for {nba_label} with marked accept state which are part of a cycle")
                pprint(Intermidiate_NBA_for_phi)
                
                print()
                
                Intermidiate_NBA_for_A_phi = mark_reachable_states(Intermidiate_NBA_for_phi)
                print(f"Intermidiate NBA for A_{nba_label}")
                pprint(Intermidiate_NBA_for_A_phi)
                
                print()
                
                NBA_for_A_phi = remove_non_reachable_states(Intermidiate_NBA_for_A_phi)
                print(f"Final {nba_label} for A_{nba_label} after removing non-reachable states")
                pprint(NBA_for_A_phi)
                
                print()
            
            except subprocess.CalledProcessError as e:
                print(f"Error occurred while processing LTL property '{formula_string}': {e.stderr}")

if __name__ == "__main__":
    main()



# Algorithm 1: Monitoring sequences using Automata
# Let us assume that the property φ is monitorable
# To give a satisfy verdict                                             To give a refute verdict

# 1.Construct the NBA for ¬φ                                            Construct the NBA for φ

# 2.States, from which one cannot reach a cycle that contains an accepting state, are deleted.

# 3.Let us call this NBA A¬φ                                            Let us call this NBA Aφ

# 4.On-the-fly exercise of the automaton:
# Let the current set of active states be the set of initial states. For each event in the trace e, the new set of
# active states is determined.

# 5.If the current set of active states is empty, then                  If the current set of active states is empty, then
# the given prefix is good, that is, φ is satisfied.                    the given prefix is bad, that is, φ is refuted.



# Example: ♢p ∨ ◻q