import json
import random
import os

def add_random_latency_to_json(input_filename, output_filename):
    """
    Adds random latency values to the 'links' in an existing JSON file.

    Args:
      input_filename: The name of the input JSON file.
      output_filename: The name of the output JSON file.
    """

    latency_values = [10, 30, 50, 100, 300]

    try:
        with open(input_filename, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Input file '{input_filename}' not found.")
        return  # Exit the function if the file is not found

    for link in data['links']:
        link['latency'] = random.choice(latency_values)  # Simplified assignment

    with open(output_filename, 'w') as f:
        json.dump(data, f, indent=2)  # Use indent for pretty printing

if __name__ == "__main__":
    input_filename = input("Enter the input filename: ")
    output_filename = input("Enter the output filename: ")
    add_random_latency_to_json(input_filename, output_filename)