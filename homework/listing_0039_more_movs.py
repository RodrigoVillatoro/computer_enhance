# Register to Register
# 100010  0  x  11   xxx  xxx
# op      d  w  mod  reg  r/m
#
# Immediate to Register
# 1100011  x  xx   000  xxx
# op       w  mod  reg  r/m

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
        "direct address",
        "[bx]"
    ]
    return address[code]

def get_address_name_w_displacement(code: int, data) -> str:
    address = [
        f"[bx + si + {data}]",
        f"[bx + di + {data}]",
        f"[bp + si + {data}]",
        f"[bp + di + {data}]",
        f"[si + {data}]",
        f"[di + {data}]",
        "[bp]",  # direct access
        f"[bx + {data}]",
    ]
    return address[code]

def mask_low_bits(offset: int, total_width: int = 8) -> int:
    # returns mask that keep lowest bits
    return (1 << (total_width - offset)) - 1

def get_op_code(current_int: int, op_code_bit_length: int) -> int:
    num_bits = 8
    return current_int >> (num_bits - op_code_bit_length)

def print_in_binary(number: int, description: str = ''):
    print(f"{number:08b}", f'-{description}')

with open(input_path, "rb") as f:
    x = f.read()

# "x" has all the bytes in the file
# We need to change our strategy because can't guarantee the instructions
# will come in 16 bytes. So we have have to iterate over x. First read the
# instructions, then determine how many bytes to consider.

# Immediate to Register
i2r = 0b1011
i2r_bit_length = i2r.bit_length()

# Register/Memory to/from Register
rm2r = 0b100010
rm2r_bit_length = rm2r.bit_length()

i = 0
while i < len(x):

    current_byte = x[i]

    # First try Immediate to Register
    op_code = get_op_code(current_byte, i2r_bit_length)

    if op_code == i2r:
        w = current_byte >> 3 & 0b1
        reg = current_byte & 0b111
        reg_name = get_register_name(reg, w)
        # print_in_binary(w, 'w')
        # print_in_binary(reg, 'reg')
        # print(reg_name, 'reg_name')

        data = x[i + 1]
        # print(data_a)
        i += 1

        if w == 1:
            data_b = x[i + 1]
            data = (data_b << 8) | data
            i += 1

        print(f"mov {reg_name}, {data}")

        i += 1

        continue

    # Then try Register/Memory to/from Register
    else:
        op_code = get_op_code(current_byte, rm2r_bit_length)

        if op_code == rm2r:
            d = current_byte >> 1 & 0b1
            w = current_byte & 0b1

            next_byte = x[i+1]
            mod = (next_byte >> 6) & 0b11
            reg = next_byte >> 3 & 0b111
            rm = next_byte & 0b111
            reg_name = get_register_name(reg, w)

            i += 1

            if mod == 0b11:

                rm_name = get_register_name(rm, w)
                # print_in_binary(w, 'w')
                # print_in_binary(reg, 'reg')
                # print(reg_name, 'reg_name')
                # print(rm_name, 'rm_name')

                dest, src = (reg_name, rm_name) if d == 1 else (rm_name, reg_name)
                print(f"mov {dest}, {src}")

            # memory mode, no displacement (exept when r/m = 110, then 16 bit disp.)
            elif mod == 0b00:

                # 16-bit displacement
                if rm == 0b110:
                    data_a, data_b = x[i+1], x[i+2]
                    address = get_address_name_no_displacement(rm)
                    dest, src = (reg_name, address) if d == 1 else (address, reg_name)
                    print(f"mov {dest}, {src}")
                    i += 2
                # no displacement
                else:
                    address = get_address_name_no_displacement(rm)
                    dest, src = (reg_name, address) if d == 1 else (address, reg_name)
                    print(f"mov {dest}, {src}")

            # memory mode, 8-bit displacement
            elif mod == 0b01:

                data = x[i+1]
                address = get_address_name_w_displacement(rm, data)
                dest, src = (reg_name, address) if d == 1 else (address, reg_name)
                print(f"mov {dest}, {src}")

                i += 1

            # memory mode, 16-bit displacement
            elif mod == 0b10:

                data_a, data_b = x[i+1], x[i+2]
                data = (data_b << 8) | data_a
                address = get_address_name_w_displacement(rm, data)
                dest, src = (reg_name, address) if d == 1 else (address, reg_name)
                print(f"mov {dest}, {src}")

                i += 2

    i += 1
