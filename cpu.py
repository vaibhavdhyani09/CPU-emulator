# cpu.py — TINY-16 fantasy CPU emulator (with trace mode)

MEMORY_SIZE = 256
NUM_REGS    = 8

NOP, LOAD, ADD, SUB, AND, OR, MOD, CMP = 0x0, 0x1, 0x2, 0x3, 0x4, 0x5, 0x6, 0x7
JMP, JZ, JNZ, STORE, LOADR, HALT       = 0x8, 0x9, 0xA, 0xB, 0xC, 0xD

MNEMONIC = {
    0x0:"NOP", 0x1:"LOAD", 0x2:"ADD", 0x3:"SUB", 0x4:"AND", 0x5:"OR",
    0x6:"MOD", 0x7:"CMP", 0x8:"JMP", 0x9:"JZ", 0xA:"JNZ",
    0xB:"STORE", 0xC:"LOADR", 0xD:"HALT",
}

class CPU:
    def __init__(self, trace=False):
        self.memory = bytearray(MEMORY_SIZE)
        self.regs   = [0] * NUM_REGS
        self.pc     = 0
        self.flag_z = False
        self.flag_n = False
        self.halted = False
        self.trace  = trace
        self.cycle  = 0

    def read16(self, addr):
        return (self.memory[addr] << 8) | self.memory[addr + 1]

    def reg_write(self, idx, value):
        if idx != 0:
            self.regs[idx] = value & 0xFFFF
    def reg_read(self, idx):
        return 0 if idx == 0 else self.regs[idx]

    def disasm(self, instr):
        op  = (instr >> 12) & 0xF
        rd  = (instr >> 8)  & 0xF
        ra  = (instr >> 4)  & 0xF
        rb  = (instr >> 0)  & 0xF
        imm = instr & 0xFF
        mn  = MNEMONIC.get(op, f"?{op:x}")
        if op in (NOP, HALT):              return mn
        if op == LOAD:                     return f"{mn} r{rd}, {imm}"
        if op in (ADD, SUB, AND, OR, MOD): return f"{mn} r{rd}, r{ra}, r{rb}"
        if op == CMP:                      return f"{mn} r{ra}, r{rb}"
        if op in (JMP, JZ, JNZ):           return f"{mn} {imm:#04x}"
        if op == STORE:                    return f"{mn} r{ra}, r{rb}"
        if op == LOADR:                    return f"{mn} r{rd}, r{ra}"
        return mn

    def step(self):
        if self.halted:
            return

        pc_before = self.pc

        instr = self.read16(self.pc)
        self.pc += 2

        opcode = (instr >> 12) & 0xF
        rd     = (instr >>  8) & 0xF
        ra     = (instr >>  4) & 0xF
        rb     = (instr >>  0) & 0xF
        imm8   = instr & 0xFF
        addr8  = instr & 0xFF

        if opcode == NOP:    pass
        elif opcode == LOAD: self.reg_write(rd, imm8)
        elif opcode == ADD:  self.reg_write(rd, self.reg_read(ra) + self.reg_read(rb))
        elif opcode == SUB:  self.reg_write(rd, self.reg_read(ra) - self.reg_read(rb))
        elif opcode == AND:  self.reg_write(rd, self.reg_read(ra) & self.reg_read(rb))
        elif opcode == OR:   self.reg_write(rd, self.reg_read(ra) | self.reg_read(rb))
        elif opcode == MOD:
            d = self.reg_read(rb)
            self.reg_write(rd, 0 if d == 0 else self.reg_read(ra) % d)
        elif opcode == CMP:
            a, b = self.reg_read(ra), self.reg_read(rb)
            self.flag_z = (a == b); self.flag_n = (a < b)
        elif opcode == JMP:  self.pc = addr8
        elif opcode == JZ:
            if self.flag_z: self.pc = addr8
        elif opcode == JNZ:
            if not self.flag_z: self.pc = addr8
        elif opcode == STORE: self.memory[self.reg_read(ra)] = self.reg_read(rb) & 0xFF
        elif opcode == LOADR: self.reg_write(rd, self.memory[self.reg_read(ra)])
        elif opcode == HALT:  self.halted = True
        else:
            raise ValueError(f"Unknown opcode {opcode:#x} at PC={pc_before:#x}")

        self.cycle += 1

        if self.trace:
            text = self.disasm(instr)
            regs = " ".join(f"r{i}={self.regs[i]}" for i in range(NUM_REGS))
            flags = f"Z={int(self.flag_z)} N={int(self.flag_n)}"
            took_branch = self.pc != pc_before + 2
            arrow = f"  -> PC={self.pc:#04x}" if took_branch else ""
            print(f"[{self.cycle:3d}] {pc_before:#04x}: {instr:#06x}  {text:<16} | {flags} | {regs}{arrow}")

    def run(self, max_steps=10_000):
        steps = 0
        while not self.halted and steps < max_steps:
            self.step(); steps += 1
        if steps == max_steps:
            print(f"[warn] hit step limit at PC={self.pc:#x}")

    def dump(self):
        print(f"PC={self.pc:#04x}  Z={int(self.flag_z)} N={int(self.flag_n)}  HALTED={self.halted}")
        for i, v in enumerate(self.regs):
            print(f"  r{i} = {v:#06x} ({v})")
