from cpu import CPU
from asm import assemble, load_program

SRC = """
        LOAD r1, 0       # counter
        LOAD r2, 10      # limit
        LOAD r3, 1       # step
loop:
        ADD  r1, r1, r3  # counter += 1
        CMP  r1, r2      # compare counter, limit
        JNZ  loop        # if not equal, repeat
        HALT
"""

cpu = CPU()
load_program(cpu, assemble(SRC))
cpu.run()
cpu.dump()
