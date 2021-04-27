#!/usr/bin/env python

ptr = 0
mem = list()
stk = list()

BITS15 = 0b111111111111111
MODULO = 0x8000

reg = { 0x8000: 0, 0x8001: 0, 0x8002: 0, 0x8003: 0,
        0x8004: 0, 0x8005: 0, 0x8006: 0, 0x8007: 0 }

import struct
import sys
import getch

def getins(ptr: int) -> list:
    ins = mem[ptr:ptr + getnoa(mem[ptr]) + 1]
    incptr()
    return ins

def deref(ins: list) -> list:
    for i in range(len(ins)):
        while ins[i] >= 0x8000 and ins[i] <= 0x8007:
            ins[i] = reg[ins[i]]

    return ins

def getnoa(opc: int) -> int:
    opands = {  0x00: 0, 0x01: 2, 0x02: 1, 0x03: 1,
                0x04: 3, 0x05: 3, 0x06: 1, 0x07: 2,
                0x08: 2, 0x09: 3, 0x0A: 3, 0x0B: 3,
                0x0C: 3, 0x0D: 3, 0x0E: 2, 0x0F: 2,
                0x10: 2, 0x11: 1, 0x12: 0, 0x13: 1,
                0x14: 1, 0x15: 0 }

    return opands[opc]

def incptr() -> None:
    global ptr
    ptr = ptr + getnoa(mem[ptr]) + 1

def init(fn: list) -> None:
    global mem

    with open(fn, "rb") as f:
        while (word := f.read(2)):
            word = struct.unpack('<H', word)[0]
            mem.append(word)

    while len(mem) < BITS15:
        mem.append(0)

def sc_halt() -> None:
    exit()

def sc_set(aa: int, ab: int) -> None:
    global reg
    reg[aa] = deref([ab])[0]

def sc_push(aa: int) -> None:
    global stk
    aa = deref([aa])[0]
    stk.append(aa)

def sc_pop(aa: int) -> None:
    global stk

    if len(stk) == 0:
        sc_halt()

    sc_set(aa, stk.pop())

def sc_eq(aa: int, ab: int, ac: int) -> None:
    ab, ac = deref([ab, ac])

    if ab == ac:
        sc_set(aa, 1)
    else:
        sc_set(aa, 0)

def sc_gt(aa: int, ab: int, ac: int) -> None:
    ab, ac = deref([ab, ac])

    if ab > ac:
        sc_set(aa, 1)
    else:
        sc_set(aa, 0)

def sc_jmp(aa: int) -> None:
    global ptr
    ptr = deref([aa])[0]

def sc_jt(aa: int, ab: int) -> None:
    aa, ab = deref([aa, ab])

    if aa != 0:
        sc_jmp(ab)

def sc_jf(aa: int, ab: int) -> None:
    aa, ab = deref([aa, ab])

    if aa == 0:
        sc_jmp(ab)

def sc_add(aa: int, ab: int, ac:int) -> None:
    ab, ac = deref([ab, ac])
    sc_set(aa, (ab + ac) % MODULO)

def sc_mult(aa: int, ab: int, ac:int) -> None:
    ab, ac = deref([ab, ac])
    sc_set(aa, (ab * ac) % MODULO)

def sc_mod(aa: int, ab: int, ac:int) -> None:
    ab, ac = deref([ab, ac])
    sc_set(aa, ab % ac)

def sc_and(aa: int, ab: int, ac: int) -> None:
    ab, ac = deref([ab, ac])
    sc_set(aa, ab & ac)

def sc_or(aa: int, ab: int, ac: int) -> None:
    ab, ac = deref([ab, ac])
    sc_set(aa, ab | ac)

def sc_not(aa: int, ab: int) -> None:
    sc_set(aa, BITS15 - deref([ab])[0])

def sc_rmem(aa: int, ab: int) -> None:
    ab = deref([ab])[0]
    sc_set(aa, mem[ab])

def sc_wmem(aa: int, ab: int) -> None:
    global mem
    aa, ab = deref([aa, ab])
    mem[aa] = ab

def sc_call(aa: int) -> None:
    sc_push(ptr)
    sc_jmp(aa)

def sc_ret() -> None:
    global stk
    aa = stk.pop()
    sc_jmp(aa)

def sc_out(aa: int) -> None:
    aa = deref([aa])[0]
    print(chr(aa), end="")

def sc_in(aa: int) -> None:
    sc_set(aa, ord(getch.getche()))

def sc_noop() -> None:
    return

def run() -> None:
    d = {   0x00: sc_halt,
            0x01: sc_set,
            0x02: sc_push,
            0x03: sc_pop,
            0x04: sc_eq,
            0x05: sc_gt,
            0x06: sc_jmp,
            0x07: sc_jt,
            0x08: sc_jf,
            0x09: sc_add,
            0x0A: sc_mult,
            0x0B: sc_mod,
            0x0C: sc_and,
            0x0D: sc_or,
            0x0E: sc_not,
            0x0F: sc_rmem,
            0x10: sc_wmem,
            0x11: sc_call,
            0x12: sc_ret,
            0x13: sc_out,
            0x14: sc_in,
            0x15: sc_noop }

    while 1:
        opc, *opa = getins(ptr)

        try:
            d[opc](*opa)
        except KeyError:
            print(opc, "not implemented", ptr, opc, opa)


if __name__ == "__main__":
    fn = sys.argv[1]

    init(fn)
    run()


