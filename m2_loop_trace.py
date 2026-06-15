from cpu import CPU
from asm import assemble, load_program
SRC = """
        LOAD r1, 0
        LOAD r2, 10
        LOAD r3, 1
loop:
        ADD  r1, r1, r3
        CMP  r1, r2
        JNZ  loop
        HALT
"""
cpu = CPU(trace=True)
load_program(cpu, assemble(SRC))
cpu.run()
print("\nFinal state:")
cpu.dump()
