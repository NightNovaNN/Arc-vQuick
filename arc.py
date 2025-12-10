import sys

# ========================================================
# AST NODES
# ========================================================

class AST_Target:
    def __init__(self, lang, filename):
        self.lang = lang
        self.filename = filename

class AST_Assign:
    def __init__(self, name, value):
        self.name = name
        self.value = value

class AST_Echo:
    def __init__(self, value):
        self.value = value

class AST_Inline:
    def __init__(self, lang, code):
        self.lang = lang
        self.code = code


# ========================================================
# BRACE FIXER (SMART INLINE MODE) 😭🔥
# ========================================================

def balance_braces(code):
    """
    Automatically fixes missing closing braces in inline C blocks.
    Also returns warnings if things look sus.
    """
    text = code.split("\n")
    open_braces = 0

    for line in text:
        open_braces += line.count("{")
        open_braces -= line.count("}")

    warnings = []

    if open_braces > 0:
        warnings.append(f"[Arc Warning] Inline block missing {open_braces} closing brace(s). Auto-fixing.")
        text.append("}" * open_braces)

    if open_braces < 0:
        warnings.append("[Arc Warning] More closing braces than opening braces. Code may break.")

    return "\n".join(text), warnings


# ========================================================
# PARSER (super robust)
# ========================================================

def parse(lines):
    ast = []
    inline_mode = False
    inline_lang = None
    inline_buffer = []

    for raw in lines:
        line = raw.strip()

        if not line or line.startswith("#"):
            continue

        # start inline block
        if not inline_mode and line.startswith("inline_") and line.endswith("{"):
            inline_lang = line.split("_", 1)[1].split("{")[0].strip()
            inline_mode = True
            inline_buffer = []
            continue

        # end inline block
        if inline_mode and line == "}":
            fixed_code, warns = balance_braces("\n".join(inline_buffer))
            for w in warns:
                print(w)
            ast.append(AST_Inline(inline_lang, fixed_code))
            inline_mode = False
            inline_lang = None
            inline_buffer = []
            continue

        # inside inline
        if inline_mode:
            inline_buffer.append(raw.rstrip("\n"))
            continue

        # target
        if line.startswith("tp "):
            parts = line.split()
            if len(parts) != 4:
                raise Exception("Invalid tp syntax.")
            _, lang, _, filename = parts
            ast.append(AST_Target(lang, filename))
            continue

        # echo
        if line.startswith("echo "):
            ast.append(AST_Echo(line[5:].strip()))
            continue

        # variable assign: x 10
        parts = line.split(maxsplit=1)
        if len(parts) == 2:
            ast.append(AST_Assign(parts[0], parts[1]))
            continue

        # ignore stray brace
        if line == "}":
            continue

        raise Exception("Unknown syntax: " + line)

    return ast


# ========================================================
# BACKEND: PYTHON
# ========================================================

def emit_python(ast):
    out = []

    for node in ast:
        if isinstance(node, AST_Assign):
            out.append(f"{node.name} = {node.value}")

        elif isinstance(node, AST_Echo):
            out.append(f"print({node.value})")

        elif isinstance(node, AST_Inline):
            out.append("# inline block ignored")
            for ln in node.code.split("\n"):
                out.append("# " + ln)

    return "\n".join(out)


# ========================================================
# BACKEND: C (smart printing + brace fixer)
# ========================================================

def emit_c(ast):
    out = ["#include <stdio.h>\n"]

    var_types = {}  # track string/int

    for node in ast:
        if isinstance(node, AST_Assign):
            val = node.value

            if val.startswith('"') and val.endswith('"'):
                var_types[node.name] = "string"
                out.append(f'char* {node.name} = {val};')
            else:
                var_types[node.name] = "int"
                out.append(f'int {node.name} = {val};')

        elif isinstance(node, AST_Echo):
            val = node.value

            # literal string
            if val.startswith('"') and val.endswith('"'):
                out.append(f'printf("%s\\n", {val});')
                continue

            # known variable
            if val in var_types:
                if var_types[val] == "string":
                    out.append(f'printf("%s\\n", {val});')
                else:
                    out.append(f'printf("%d\\n", {val});')
                continue

            # fallback
            out.append(f'printf("%d\\n", {val});')

        elif isinstance(node, AST_Inline):
            out.append(node.code)

    return "\n".join(out)


# ========================================================
# BUILD SYSTEM
# ========================================================

def build(ast):
    target = None
    for node in ast:
        if isinstance(node, AST_Target):
            target = node
            break

    if not target:
        raise Exception("Missing target: tp C as out.c")

    if target.lang == "Py":
        code = emit_python(ast)
    elif target.lang == "C":
        code = emit_c(ast)
    else:
        raise Exception("Unknown backend: " + target.lang)

    with open(target.filename, "w") as f:
        f.write(code)

    print("Generated →", target.filename)


# ========================================================
# CLI
# ========================================================

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: python arc.py file.arc")
        sys.exit(1)

    with open(sys.argv[1], "r") as f:
        lines = f.readlines()

    ast = parse(lines)
    build(ast)
