from cpu import CPU
from asm import assemble, load_program

# Plan:
#   r1 = current number (1..20)
#   r2 = limit (21, loop while r1 != 21)
#   r3 = 3, r4 = 5, r5 = 1 (constants)
#   r6 = result code, r7 = output address (grows each pass)
# For each n: code = 0; if n%3==0 code+=1; if n%5==0 code+=2; store code; n++
SRC = """
        LOAD  r1, 1        # n = 1
        LOAD  r2, 21       # limit
        LOAD  r3, 3
        LOAD  r4, 5
        LOAD  r5, 1
        LOAD  r7, 100      # output base address
loop:
        LOAD  r6, 0        # result code = 0
        MOD   r0, r1, r3   # (discard) compute n%3 into a temp via r0? r0 is zero-sink
        # r0 can't hold a value, so use a real temp register instead:
        MOD   r1, r1, r3   # WRONG: would clobber n. handled below differently.
        HALT
"""
# The naive version above hits the r0-sink problem and clobbering.
# Correct version uses a dedicated temp register and recomputes carefully:

SRC = """
        LOAD  r1, 1        # n
        LOAD  r2, 21       # limit
loop:
        LOAD  r6, 0        # code = 0
        LOAD  r3, 3
        MOD   r3, r1, r3   # r3 = n % 3
        CMP   r3, r0       # is r3 == 0 ?
        JNZ   skip3
        LOAD  r3, 1
        ADD   r6, r6, r3   # code += 1
skip3:
        LOAD  r4, 5
        MOD   r4, r1, r4   # r4 = n % 5
        CMP   r4, r0       # is r4 == 0 ?
        JNZ   skip5
        LOAD  r4, 2
        ADD   r6, r6, r4   # code += 2
skip5:
        LOAD  r7, 100
        ADD   r7, r7, r1   # output addr = 100 + n
        STORE r7, r6       # mem[100+n] = code
        LOAD  r5, 1
        ADD   r1, r1, r5   # n += 1
        CMP   r1, r2       # n == 21 ?
        JNZ   loop
        HALT
"""

cpu = CPU()
load_program(cpu, assemble(SRC))
cpu.run()

labels = {0: "{}", 1: "Fizz", 2: "Buzz", 3: "FizzBuzz"}
for n in range(1, 21):
    code = cpu.memory[100 + n]
    print(labels[code].format(n))
