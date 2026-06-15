from cpu import CPU
from asm import assemble, load_program

SRC = """
    LOAD  r1, 200    # address to use
    LOAD  r2, 99     # value to store
    STORE r1, r2     # mem[200] = 99
    LOADR r3, r1     # r3 = mem[200]
    HALT
"""

cpu = CPU()
load_program(cpu, assemble(SRC))
cpu.run()
cpu.dump()
print("mem[200] =", cpu.memory[200])
