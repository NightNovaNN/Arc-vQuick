import re
import sys

variables = {}

def evaluate(expr):
    """Evaluates numbers, variables, and math expressions."""
    expr = expr.strip()

    # If it's quoted, treat as string literal
    if (expr.startswith('"') and expr.endswith('"')):
        return expr.strip('"')

    # If it's a standalone variable
    if expr in variables:
        return variables[expr]

    try:
        return eval(expr, {}, variables)
    except:
        return expr


def execute_single(cmd):
    """Executes one Arc command (no multi-statements)."""
    tokens = cmd.split()

    if not tokens:
        return False

    # PRINT
    if tokens[0] == "print":
        parts = cmd[6:].strip().split()
        print(*[evaluate(p) for p in parts])

    # VARIABLE ASSIGNMENT
    elif tokens[0] == "var":
        var_name = tokens[1]
        expr = cmd.split("=", 1)[1].strip()
        variables[var_name] = evaluate(expr)

    # IF
    elif tokens[0] == "if":
        condition, body = cmd.split(":", 1)
        condition = condition[3:].strip()
        if eval(condition, {}, variables):
            execute_line(body.strip())
            return True
        return False

    # ELSE
    elif tokens[0] == "else":
        body = cmd.split(":", 1)[1].strip()
        execute_line(body)

    # WHILE
    elif tokens[0] == "while":
        condition, body = cmd.split(":", 1)
        condition = condition[6:].strip()
        body = body.strip()

        while eval(condition, {}, variables):
            execute_line(body)

    return False


def execute_line(line, skip_else=False):
    """Supports multiple commands on the same line."""
    # Split on commands inside a single line
    parts = re.split(r'\b(?=print|var|if|else|while\b)', line)

    for p in parts:
        p = p.strip()
        if not p:
            continue

        if p.startswith("else") and skip_else:
            continue

        result = execute_single(p)

        # result=True means IF executed successfully
        if p.startswith("if"):
            skip_else = result

    return skip_else


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

    global variables
    variables = {}

    for line in test_code:
        print(">>", line)
        execute_line(line)

    print("\nArc Self-Test Complete.")


if __name__ == "__main__":
    run_arc_tests()
