"""CPU functionality."""

import sys

OP_LDI = 0b10000010
OP_PRN = 0b01000111
OP_ADD = 0b10100000
OP_MUL = 0b10100010
OP_HLT = 0b00000001
OP_PUSH = 0b01000101
OP_POP = 0b01000110
OP_CALL = 0b01010000
OP_RET = 0b00010001

SP = 7 # Stack pointer constant

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0b00000000] * 256
        self.reg = [0b00000000] * 8

        self.reg[SP] = 0xf4  # Stack pointer

        self.branchtable = {}
        self.branchtable[OP_LDI] = self.ldi
        self.branchtable[OP_PRN] = self.prn
        self.branchtable[OP_ADD] = self.add
        self.branchtable[OP_MUL] = self.mul
        self.branchtable[OP_HLT] = self.hlt
        self.branchtable[OP_PUSH] = self.push
        self.branchtable[OP_POP] = self.pop
        self.branchtable[OP_CALL] = self.call
        self.branchtable[OP_RET] = self.ret

        self.running = True

        self.pc = 0 # Program Counter, address of the currently executing instruction
        self.ir = 0 # Instruction Register, contains a copy of the currently executing instruction
        self.mar = 0 # Memory Address Register, holds the memory address we're reading or writing
        self.mdr = 0 # Memory Data Register, holds the value to write or the value just read
        self.fl = 0 # Flags, L G E

    def ram_read(self, mar):
        return self.ram[mar]

    def ram_write(self, mar, mdr):
        self.ram[mar] = mdr

    def load(self):
        """Load a program into memory."""

        address = 0

        if len(sys.argv) != 2:
            print("usage: comp.py progname")
            sys.exit(1)

        try:
            with open(sys.argv[1]) as f:
                for line in f:
                    line = line.strip()
                    temp = line.split()
                    # print(temp)

                    if len(temp) == 0:
                        continue
                    
                    if temp[0][0] == '#':
                        continue

                    try:
                        self.ram[address] = int(temp[0], 2)

                    except ValueError:
                        print(f"Invalid number: {temp[0]}")
                        sys.exit(1)

                    address += 1

        except FileNotFoundError:
            print(f"Couldn't open {sys.argv[1]}")
            sys.exit(2)

        if address == 0:
            print("Program was empty!")
            sys.exit(3)

        # print(f"RAM: {self.ram}")


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "DIV":
            self.reg[reg_a] /= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")


    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()


    def incrementPC(self, i):
        if i >= 1 & i <= 3:
            self.pc += i
        else:
            raise Exception("Unsupported 'i' value")

    def ldi(self, operand_a, operand_b):
        self.reg[operand_a] = operand_b
        self.incrementPC(3)

    def prn(self, operand_a):
        print(self.reg[operand_a])
        self.incrementPC(2)

    def add(self, operand_a, operand_b):
        self.alu("ADD", operand_a, operand_b)
        self.incrementPC(3)

    def mul(self, operand_a, operand_b):
        self.alu("MUL", operand_a, operand_b)
        self.incrementPC(3)

    def hlt(self):
        self.running = False
        self.incrementPC(1)

    def push(self, register):
        # Decrement SP
        self.reg[SP] -= 1

        # Get value from register
        reg_num = self.ram[self.pc + 1]
        value = self.reg[reg_num] # We want to push this value

        # Store it on the stack
        top_of_stack_addr = self.reg[SP]
        self.ram[top_of_stack_addr] = value

        # print(f"{self.ram}")

        self.incrementPC(2)

    def pop(self, register):
        # Copy value from top of the stack
        reg_num = self.ram[self.pc + 1]
        top_of_stack_addr = self.reg[SP]
        value = self.ram[top_of_stack_addr] # We want to pop this value

        # Store it in the given register
        self.reg[reg_num] = value

        # Increment SP
        self.reg[SP] += 1
        
        self.incrementPC(2)

    def call(self, register):
        # Push return address
        ret_addr = self.pc + 2
        self.reg[SP] -= 1
        self.ram[self.reg[SP]] = ret_addr

        # Call the subroutine
        reg_num = self.ram[self.pc + 1]
        self.pc = self.reg[reg_num]

    def ret(self):
        # Pop the return addr off the stack
        ret_addr = self.ram[self.reg[SP]]
        self.reg[SP] += 1

        # Set the PC to it
        self.pc = ret_addr

    def run(self):
        """Run the CPU."""
        while self.running:
            ir = self.ram_read(self.pc)

            # print(f"IR: {ir}")

            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)
            num_ops = "{0:08b}".format(ir)[0:2]

            if num_ops == '00':
                self.branchtable[ir]()

            elif num_ops == '01':
                self.branchtable[ir](operand_a)

            elif num_ops == '10':
                self.branchtable[ir](operand_a, operand_b)


