"""CPU functionality."""

import sys

LDI = 0b10000010
PRN = 0b01000111
HLT = 0b00000001
MUL = 0b10100010
POP = 0b01000110
PUSH = 0b01000101
CALL = 0b01010000
RET = 0b00010001
ADD = 0b10100000
CMP = 0b10100111
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110

SP = 7
greater_flag = 0b00000010
less_flag = 0b00000100
equal_flag = 0b00000001


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.pc = 0
        self.reg = [0] * 8
        self.ram = [0] * 256
        self.branchtable = {
            LDI: self.ldi,
            PRN: self.prn,
            HLT: self.hlt,
            ADD: self.add,
            MUL: self.mul,
            POP: self.pop,
            PUSH: self.push,
            CALL: self.call,
            RET: self.ret,
            CMP: self.cmp,
            JMP: self.cmp,
            JEQ: self.jeq,
            JNE: self.jne
        }
        self.line = 0
        # set the flag for CMP as 0 for not equal values
        self.flag = 0b00000001

    def ram_read(self, mar):
        mdr = self.ram[mar]
        return mdr


    def ram_write(self, mar, value):
        self.ram[mar] = value


    def load(self, file):
        """Load a program into memory."""

        try:
            address = 0
            # open file
            with open(sys.argv[1]) as f:
                # read all lines
                for line in f:
                    # parse out comments
                    comment_split = line.strip().split("#")
                    # cast number strings to ints
                    value = comment_split[0].strip()
                    # ignore blank lines
                    if value == "":
                        continue
                    self.line += 1
                    instruction = int(value, 2)
                    # populate a memory array
                    self.ram[address] = instruction
                    address += 1

        except FileNotFoundError:
            print("File not found")
            sys.exit(2)

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

        
    def ldi(self, operand_a, operand_b):
        self.reg[operand_a] = operand_b
        self.pc += 3        
    
    def prn(self, operand_a, operand_b):
        #operand_a = self.ram_read(self.pc + 1)
        print(self.reg[operand_a])
        self.pc += 2

    def hlt(self):
        sys.exit(0)

    def mul(self):
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2)
        self.reg[operand_a] *= self.reg[operand_b]
        self.pc += 3

    def add(self):
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2)
        self.reg[operand_a] += self.reg[operand_b]
        self.pc += 3

    def push(self):
        # grab the register argument
        reg = self.ram_read(self.pc + 1)
        val = self.reg[reg]
        # decrement the SP
        self.reg[SP] -= 1
        # copy the value in the given register
        self.ram_write(self.reg[SP], val)
        self.pc += 2

    def pop(self):
        # grab the value from the top of the stack
        reg = self.ram_read(self.pc + 1)
        val = self.ram_read(self.reg[SP])
        # copy the value from the address pointed to by SP to the given register
        self.reg[reg] = val
        # increment SP
        self.reg[SP] += 1
        self.pc += 2

    def call(self):
        # push return addr on stack
        return_address = self.pc + 2
        self.reg[SP] -= 1 # decrement sp
        self.ram_write(self.reg[SP], return_address)
        # set the pc to the value in the register
        reg_num = self.ram_read(self.pc + 1)
        self.pc = self.reg[reg_num]

    def ret(self):
        # pop the value from the top of the stack
        # store it in the PC.
        self.pc = self.ram_read(self.reg[SP])
        self.reg[SP] += 1
    
    def cmp(self, operand_a, operand_b):
        self.alu("CMP", operand_a, operand_b)
        self.pc +=3

    def jmp(self, operand_a, operand_b):
        self.pc = self.reg[operand_a]

    def jeq(self, operand_a, operand_b):
        if self.flag & equal_flag:
            self.pc = self.reg[operand_a]
        else:
            self.pc += 2

    def jne(self, operand_a, operand_b):
        if self.flag != equal_flag:
            self.pc = self.reg[operand_a]
        else:
            self.pc += 2
    
    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == MUL:
            self.reg[reg_a] *= self.reg[reg_b]
        #elif op == "SUB": etc
        elif op == "CMP":
            if self.reg[reg_a] < self.reg[reg_b]:
                self.flag = less_flag
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.flag = greater_flag
            else:
                self.flag = equal_flag
        else:
            raise Exception("Unsupported ALU operation")

    def run(self):
        """Run the CPU."""
        for _ in range(self.line):
            ins = self.ram_read(self.pc)

            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            if ins in self.branchtable:
                self.branchtable[ins](operand_a, operand_b)
            else:
                raise Exception(f'Invalid {ins}, not in branch table \t {list(self.branchtable.keys())}')