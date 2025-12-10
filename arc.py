import re
import sys

variables = {}

def evaluate(expression):
    """Evaluates numbers, variables, and math operations."""
    try:
        return eval(expression, {}, variables)
    except:
        return expression.strip('"')

def execute_line(line, skip_else=False):
    """Executes a single Arc command."""
    tokens = line.split()

    if not tokens:
        return  # Ignore empty lines

    if tokens[0] == "print":
        print(*[evaluate(token) for token in tokens[1:]])

    elif tokens[0] == "var":
        var_name = tokens[1]
        variables[var_name] = evaluate(" ".join(tokens[3:]))

    elif tokens[0] == "if":
        if ":" in tokens:
            colon_index = tokens.index(":")
            condition = " ".join(tokens[1:colon_index])
            body = " ".join(tokens[colon_index + 1:])
            
            if eval(condition, {}, variables):
                execute_line(body)
                return True  # If condition is true, return to avoid `else`
    
    elif tokens[0] == "else" and not skip_else:
        if ":" in tokens:
            colon_index = tokens.index(":")
            body = " ".join(tokens[colon_index + 1:])
            execute_line(body)

    elif tokens[0] == "while":
        if ":" in tokens:
            colon_index = tokens.index(":")
            condition = " ".join(tokens[1:colon_index])
            body = " ".join(tokens[colon_index + 1:])

            while eval(condition, {}, variables):
                execute_line(body)

def run_arc_file(filename):
    """Reads and executes an Arc script file."""
    try:
        with open(filename, "r") as file:
            lines = file.readlines()
        
        skip_else = False
        for line in lines:
            line = line.strip()
            if line.startswith("if"):
                skip_else = execute_line(line)
            elif line.startswith("else"):
                execute_line(line, skip_else)
            else:
                execute_line(line)

    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")


def run_arc_tests():
    print("Running Arc Self-Test...\n")

    test_code = [
        'print "Test 1: Printing works!"',
        'var x = 10',
        'print "x =" x',
        'if x > 5: print "IF works!"',
        'else: print "IF FAILED"',
        'var y = 1',
        'while y < 4: print "Loop:" y var y = y + 1',
        'print "Final y =" y'
    ]

    # Reset variables for clean test
    global variables
    variables = {}

    for line in test_code:
        print(">>", line)
        execute_line(line)

    print("\nArc Self-Test Complete.")

if __name__ == "__main__":
    run_arc_tests()
