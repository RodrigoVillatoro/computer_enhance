from pathlib import Path

# Get homework's input file
script_stem = Path(__file__).stem
repo_root = Path(__file__).resolve().parent.parent
input_path = repo_root / "perfaware" / "part1" / script_stem

def get_register_name(code: int, w: int) -> str:
    # the 3-bit code (000–111) is just an integer from 0–7
    # so it can be used directly as a list index.
    # It works because it matches with the 8086 table.
    regs_w0 = ["al", "cl", "dl", "bl", "ah", "ch", "dh", "bh"]
    regs_w1 = ["ax", "cx", "dx", "bx", "sp", "bp", "si", "di"]
    return (regs_w1 if w else regs_w0)[code]

def get_address_name_no_displacement(code: int) -> str:
    address = [
        "[bx + si]",
        "[bx + di]",
        "[bp + si]",
        "[bp + di]",
        "[si]",
        "[di]",
        "DIRECT ADDRESS (need to handle)",
        "[bx]"
    ]
    return address[code]

def get_address_name_w_displacement(code: int, data) -> str:

    sign = "-" if data < 0 else "+"

    address = [
        f"[bx + si {sign} {abs(data)}]",
        f"[bx + di {sign} {abs(data)}]",
        f"[bp + si {sign} {abs(data)}]",
        f"[bp + di {sign} {abs(data)}]",
        f"[si {sign} {abs(data)}]",
        f"[di {sign} {abs(data)}]",
        f"[bp {sign} {abs(data)}]",
        f"[bx {sign} {abs(data)}]",
    ]
    return address[code]

jumps = {
    0b01110100: "je",
    0b01111100: "jl",
    0b01111110: "jle",
    0b01110010: "jb",
    0b01110110: "jbe",
    0b01111010: "jp",
    0b01110000: "jo",
    0b01111000: "js",
    0b01110101: "jnz",
    0b01111101: "jnl",
    0b01111111: "jg",
    0b01110011: "jnb",
    0b01110111: "ja",
    0b01111011: "jnp",
    0b01110001: "jno",
    0b01111001: "jns",
    0b11100010: "loop",
    0b11100001: "loopz",
    0b11100000: "loopnz",
    0b11100011: "jcxz",
}

def get_op_code(current_byte: int, op_code_bit_length: int) -> int:
    num_bits = 8
    return current_byte >> (num_bits - op_code_bit_length)

def get_op_name(current_byte: int):
    op_num = (current_byte >> 3) & 0b111
    if op_num == 0b000:
        op = "add"
    elif op_num == 0b101:
        op = "sub"
    elif op_num == 0b111:
        op = "cmp"
    else:
        op = "not recognised"
    return op

def print_in_binary(number: int, description: str = ''):
    print(f"{number:08b}", f'-{description}')

def to_signed(value: int, bits: int) -> int:  # two's complement logic
    if value >= 1 << (bits - 1):  # if the top bit is set
        return value - (1 << bits)  # convert to signed
    return value

with open(input_path, "rb") as f:
    x = f.read()

# Reg/memory with register 2 either

add_rm_w_r2e = 0b000000
add_rm_w_r2e_bit_length = 6

sub_rm_w_r2e = 0b001010
sub_rm_w_r2e_bit_length = 6

cmp_rm_w_r2e = 0b001110
cmp_rm_w_r2e_bit_length = 6

# Immediate to register/memory

add_sub_cmp_im2rm = 0b100000
add_sub_cmp_im2rm_bit_length = 6

# Immediate to accumulator

add_im2acc = 0b0000010
add_im2acc_bit_length = 7

sub_im2acc = 0b0010110
sub_im2acc_bit_length = 7

cmp_im2acc = 0b0011110
cmp_im2acc_bit_length = 7

i = 0
while i < len(x):

    current_byte = x[i]

    # Reg/memory with register 2 either
    if get_op_code(current_byte, add_rm_w_r2e_bit_length) in (
        add_rm_w_r2e, sub_rm_w_r2e, cmp_rm_w_r2e):

        op = get_op_name(current_byte)
        d = (current_byte >> 1) & 0b1
        w = current_byte & 0b1

        next_byte = x[i+1]

        mod = (next_byte >> 6) & 0b11
        reg = (next_byte >> 3) & 0b111
        rm = next_byte & 0b111
        reg_name = get_register_name(reg, w)

        i += 1

        if mod == 0b11:

            rm_name = get_register_name(rm, w)
            dest, src = (reg_name, rm_name) if d == 1 else (rm_name, reg_name)
            print(f"{op} {dest}, {src}")

        # memory mode, no displacement (exept when r/m = 110, then 16 bit disp.)
        elif mod == 0b00:

            # 16-bit displacement
            if rm == 0b110:
                data_a, data_b = x[i+1], x[i+2]
                data = (data_b << 8) | data_a
                address = f"[{data}]"  # direct access, no lookup needed
                dest, src = (reg_name, address) if d == 1 else (address, reg_name)
                print(f"{op} {dest}, {src}")
                i += 2
            # no displacement
            else:
                address = get_address_name_no_displacement(rm)
                dest, src = (reg_name, address) if d == 1 else (address, reg_name)
                print(f"{op} {dest}, {src}")

        # memory mode, 8-bit displacement
        elif mod == 0b01:

            data = to_signed(x[i+1], bits=8)
            address = get_address_name_w_displacement(rm, data)
            dest, src = (reg_name, address) if d == 1 else (address, reg_name)
            print(f"{op} {dest}, {src}")

            i += 1

        # memory mode, 16-bit displacement
        elif mod == 0b10:

            data_a, data_b = x[i+1], x[i+2]
            data = (data_b << 8) | data_a
            data = to_signed(data, bits=16)
            address = get_address_name_w_displacement(rm, data)
            dest, src = (reg_name, address) if d == 1 else (address, reg_name)
            print(f"{op} {dest}, {src}")

            i += 2

    # Immediate to register/memory
    elif add_sub_cmp_im2rm == get_op_code(current_byte, add_sub_cmp_im2rm_bit_length):

        s = (current_byte >> 1) & 0b1
        w = current_byte & 0b1

        i += 1
        next_byte = x[i]

        mod = (next_byte >> 6) & 0b11
        reg = (next_byte >> 3) & 0b111
        rm = next_byte & 0b111
        op = get_op_name(next_byte)

        if mod == 0b11: # register mode, no displacement
            address = get_register_name(rm, w)

        elif mod == 0b00:  # memory mode, no displacement
            if rm == 0b110: # direct access
                data_a, data_b = x[i+1], x[i+2]
                data = (data_b << 8) | data_a
                address = f"[{data}]"
                i += 2
            else:
                address = get_address_name_no_displacement(rm)

        elif mod == 0b01:  # with 8-bit displacement
            data = to_signed(x[i+1], bits=8)
            address = get_address_name_w_displacement(rm, data)
            i += 1

        else: # mod == 0b10 (with 16-bit displacement)
            data_a, data_b = x[i+1], x[i+2]
            data = (data_b << 8) | data_a
            data = to_signed(data, bits=16)
            address = get_address_name_w_displacement(rm, data)
            i += 2

        if s == 0b0 and w == 0b1:  # data right after the displacement
            data_a, data_b = x[i+1], x[i+2]
            data = (data_b << 8) | data_a
            i += 2
        else:
            data = x[i+1]
            if s == 0b1:
                data = to_signed(data, 8)
            i += 1

        if mod == 0b11: # register destination implies the size
            print(f"{op} {address}, {data}")
        else:
            if w == 0b0:
                size = "byte"
            else:
                size = "word"
            print(f"{op} {address}, {size} {data}")

    # Immediate to accumulator
    elif get_op_code(current_byte, add_im2acc_bit_length) in (
        add_im2acc, sub_im2acc, cmp_im2acc
    ):

        op = get_op_name(current_byte)

        w = current_byte & 0b1
        reg_name = get_register_name(0, w)

        if w == 0b0:
            data = x[i+1]
            data = to_signed(data, 8)
            i += 1
        else:
            data_a, data_b = x[i+1], x[i+2]
            data = (data_b << 8) | data_a
            data = to_signed(data, 16)
            i += 2

        print(f"{op} {reg_name}, {data}")

    elif current_byte in jumps:
        op = jumps[current_byte]
        offset = to_signed(x[i+1], 8)
        print(f"{op} ${offset + 2:+d}")
        i += 1

    else:
        raise ValueError(f"unknown opcode {current_byte:08b} at byte {i}")

    i += 1
