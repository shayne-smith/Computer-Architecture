"""CPU functionality."""

import sys

OP_LDI = 0b10000010
OP_PRN = 0b01000111
OP_MUL = 0b10100010
OP_HLT = 0b00000001

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0b00000000] * 256
        self.reg = [0b00000000] * 8

        self.branchtable = {}
        self.branchtable[OP_LDI] = self.ldi
        self.branchtable[OP_PRN] = self.prn
        self.branchtable[OP_MUL] = self.mul
        self.branchtable[OP_HLT] = self.hlt

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

        print(f"RAM: {self.ram}")


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

    def mul(self, operand_a, operand_b):
        self.alu("MUL", operand_a, operand_b)
        self.incrementPC(3)

    def hlt(self):
        self.running = False
        self.incrementPC(1)

    def run(self):
        """Run the CPU."""
        while self.running:
            ir = self.ram_read(self.pc)

            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)
            num_ops = "{0:08b}".format(ir)[0:2]

            if num_ops == '00':
                self.branchtable[ir]()

            elif num_ops == '01':
                self.branchtable[ir](operand_a)

            elif num_ops == '10':
                self.branchtable[ir](operand_a, operand_b)


