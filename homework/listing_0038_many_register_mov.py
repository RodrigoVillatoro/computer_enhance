# 1000100111011001
# 100010  0  1  11   011  001
# op      d  w  mod  reg  r/m

from pathlib import Path

# Get homework's input file
script_stem = Path(__file__).stem
repo_root = Path(__file__).resolve().parent.parent
input_path = repo_root / "perfaware" / "part1" / script_stem

def register_name(code, w):
    # the 3-bit code (000–111) is just an integer from 0–7
    # so it can be used directly as a list index.
    # It works because it matches with the 8086 table.
    regs_w0 = ["al", "cl", "dl", "bl", "ah", "ch", "dh", "bh"]
    regs_w1 = ["ax", "cx", "dx", "bx", "sp", "bp", "si", "di"]
    return (regs_w1 if w else regs_w0)[code]

with open(input_path, "rb") as f:
    x = f.read()

# "x" has all the bytes in the file
#  we need iterate over it in pairs (16-bit values)
for i in range(0, len(x), 2):

    b1, b2 = x[i], x[i+1]  # indexing  gives us an int (no need for int.from_bytes)
    _op_code = b1 >> 2
    _d = (b1 >> 1) & 1  # 1 reg is the dest, otherwise r/m is the dest
    _w = b1 & 1
    _mod = (b2 >> 6) & 0b11
    _reg = b2 >> 3 & 0b111
    _rm = b2 & 0b111

    operation = 'N/A'
    if _op_code == 0b100010:
        operation = "mov"

    reg_name = register_name(_reg, _w)
    rm_name = register_name(_rm, _w)

    dest, src = (reg_name, rm_name) if _d == 1 else (rm_name, reg_name)

    print(f"{operation} {dest}, {src}")
