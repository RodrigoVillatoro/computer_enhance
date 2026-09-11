# 1000100111011001
# 100010  0  1  11   011  001
# op      d  w  mod  reg  r/m

def register_name(code, w):
    # the 3-bit code (000–111) is just an integer from 0–7
    # so it can be used directly as a list index.
    # Works because matches with the 8086 table.
    regs_w0 = ["al", "cl", "dl", "bl", "ah", "ch", "dh", "bh"]
    regs_w1 = ["ax", "cx", "dx", "bx", "sp", "bp", "si", "di"]
    return (regs_w1 if w else regs_w0)[code]

with open("asm/listing_0037_single_register_mov", "rb") as f:
    x = f.read()

value = int.from_bytes(x, byteorder="big")
_op_code = value >> 10
_d = (value >> 9) & 1  # 1 reg is the dest, otherwise r/m is the dest
_mod = (value >> 6) & 0b11
_w = value >> 8 & 1
_reg = value >> 3 & 0b111
_rm = value & 0b111

operation = 'N/A'
print(f"{_op_code:06b}")
if _op_code == 0b100010:
    operation = "mov"

reg_name = register_name(_reg, _w)
rm_name = register_name(_rm, _w)

dest, src = (reg_name, rm_name) if _d == 1 else (rm_name, reg_name)

print(f"{operation} {dest}, {src}")
