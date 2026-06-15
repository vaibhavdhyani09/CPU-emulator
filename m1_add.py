from cpu import CPU
from asm import assemble, load_program

SRC = """
    LOAD r1, 10      # r1 = 10
    LOAD r2, 32      # r2 = 32
    ADD  r3, r1, r2  # r3 = r1 + r2  -> 42
    HALT
"""

cpu = CPU()
load_program(cpu, assemble(SRC))
cpu.run()
cpu.dump()
