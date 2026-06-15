OPCODES = {"NOP":0x0,"LOAD":0x1,"ADD":0x2,"SUB":0x3,"AND":0x4,"OR":0x5,"MOD":0x6,
"CMP":0x7,"JMP":0x8,"JZ":0x9,"JNZ":0xA,"STORE":0xB,"LOADR":0xC,"HALT":0xD}

def reg(tok):
    tok = tok.strip().lower().rstrip(",")
    assert tok[0] == "r", f"expected register, got {tok}"
    return int(tok[1:])

def assemble(source):
    lines = []
    for raw in source.splitlines():
        line = raw.split("#")[0].strip()
        if line:
            lines.append(line)
    labels, addr, cleaned = {}, 0, []
    for line in lines:
        if line.endswith(":"):
            labels[line[:-1].strip()] = addr
        else:
            cleaned.append(line)
            addr += 2
    words = []
    for line in cleaned:
        parts = line.replace(",", " ").split()
        mn = parts[0].upper()
        op = OPCODES[mn]
        if mn in ("NOP", "HALT"):
            word = op << 12
        elif mn == "LOAD":
            word = (op << 12) | (reg(parts[1]) << 8) | (int(parts[2]) & 0xFF)
        elif mn in ("ADD", "SUB", "AND", "OR", "MOD"):
            word = (op << 12) | (reg(parts[1]) << 8) | (reg(parts[2]) << 4) | reg(parts[3])
        elif mn == "CMP":
            word = (op << 12) | (reg(parts[1]) << 4) | reg(parts[2])
        elif mn in ("JMP", "JZ", "JNZ"):
            t = parts[1]
            a = labels[t] if t in labels else int(t)
            word = (op << 12) | (a & 0xFF)
        elif mn == "STORE":
            word = (op << 12) | (reg(parts[1]) << 4) | reg(parts[2])
        elif mn == "LOADR":
            word = (op << 12) | (reg(parts[1]) << 8) | (reg(parts[2]) << 4)
        else:
            raise ValueError(f"cannot assemble: {line}")
        words.append(word)
    return words

def load_program(cpu, words, start=0):
    addr = start
    for w in words:
        cpu.memory[addr] = (w >> 8) & 0xFF
        cpu.memory[addr + 1] = w & 0xFF
        addr += 2
