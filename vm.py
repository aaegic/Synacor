#!/usr/bin/env python

# XXX check modulo of all operations

ptr = 0
mem = list()
stk = list()

reg = { 0x8000: 0, 0x8001: 0, 0x8002: 0, 0x8003: 0,
        0x8004: 0, 0x8005: 0, 0x8006: 0, 0x8007: 0 }

import struct
import sys
import var_dump
import json

def getins(ptr: int) -> list:
    #print(ptr)
    #print(ptr, mem[ptr:ptr+4])
    ins = mem[ptr:ptr+4]
    #oc = mem[ptr]
    #noa = getnoa(oc)
    #ins = mem[ptr:ptr + noa + 1]

    #ins = mem[ptr:ptr + getnoa(mem[ptr]) + 1]

    #ins = list()
    #print(ins)

    #ins = deref(ins)
    
    for i in ins:
        if i >= 32776 and i <= 65535:
            print("found invalid number: "+i)

    incptr()

    #print(ins)
    return ins

def deref(ins: list) -> list:
    for i in range(len(ins)):
        if ins[i] >= 0x8000 and ins[i] <= 0x8007:
            ins[i] = reg[ins[i]]

    return ins

def getnoa(oc: int) -> int:
    opands = {  0x00: 0, 0x01: 2, 0x02: 1, 0x03: 1,
                0x04: 3, 0x05: 3, 0x06: 1, 0x07: 2,
                0x08: 2, 0x09: 3, 0x0A: 3, 0x0B: 3,
                0x0C: 3, 0x0D: 3, 0x0E: 2, 0x0F: 2,
                0x10: 2, 0x11: 1, 0x12: 0, 0x13: 1,
                0x14: 1, 0x15: 0 }

    return opands[oc]

def incptr() -> None:
    global ptr
    ptr = ptr + getnoa(mem[ptr]) + 1

def init(fn: list) -> None:
    global mem
    global ptr

    for i in range(0, 0b111111111111111):
        mem.append(0)

    with open(fn, "rb") as f:
        while (word := f.read(2)):
            word = struct.unpack('<H', word)[0]
            mem[ptr] = word
            ptr += 1
    
    ptr = 0

def sc_halt(aa: int, ab: int, ac: int) -> None:
    exit()

def sc_set(aa: int, ab: int, ac: int) -> None:
    global reg
    reg[aa] = deref([ab])[0]

def sc_push(aa: int, ab: int, ac: int) -> None:
    global stk
    aa = deref([aa])[0]
    stk.append(aa)

def sc_pop(aa: int, ab: int, ac: int) -> None:
    global stk
    global reg

    if len(stk) == 0:
        print("error: popping 0 stack")
    else:
        reg[aa] = stk.pop()

def sc_eq(aa: int, ab: int, ac: int) -> None:
    global reg
    ab, ac = deref([ab, ac])

    if ab == ac:
        reg[aa] = 1
    else:
        reg[aa] = 0

def sc_gt(aa: int, ab: int, ac: int) -> None:
    global reg
    ab, ac = deref([ab, ac])

    if ab > ac:
        reg[aa] = 1
    else:
        reg[aa] = 0

def sc_jmp(aa: int, ab: int, ac: int) -> None:
    global ptr
    aa = deref([aa])[0]
    ptr = aa

def sc_jt(aa: int, ab: int, ac: int) -> None:
    global ptr
    aa, ab = deref([aa, ab])

    if aa != 0:
        sc_jmp(ab, ab, ac)
        #ptr = ab

def sc_jf(aa: int, ab: int, ac: int) -> None:
    global ptr
    aa, ab = deref([aa, ab])

    if aa == 0:
        sc_jmp(ab, ab, ac)
        #ptr = ab

def sc_add(aa: int, ab: int, ac:int) -> None:
    global reg
    ab, ac = deref([ab, ac])
    reg[aa] = ab + ac

    while reg[aa] >= 32768:
        reg[aa] -= 32768

def sc_mult(aa: int, ab: int, ac:int) -> None:
    global reg
    ab, ac = deref([ab, ac])
    reg[aa] = ab * ac

    while reg[aa] >= 32768:
        reg[aa] -= 32768

def sc_mod(aa: int, ab: int, ac:int) -> None:
    global reg
    ab, ac = deref([ab, ac])
    reg[aa] = ab % ac

def sc_and(aa: int, ab: int, ac: int) -> None:
    global reg
    ab, ac = deref([ab, ac])
    reg[aa] = ab & ac

def sc_or(aa: int, ab: int, ac: int) -> None:
    global reg
    ab, ac = deref([ab, ac])
    reg[aa] = ab | ac

def sc_not(aa: int, ab: int, ac: int) -> None:
    global reg
    reg[aa] = 0b111111111111111 - deref([ab])[0]

def sc_rmem(aa: int, ab: int, ac: int) -> None:
    global mem
    global reg
    ab = deref([ab])[0]
    reg[aa] = mem[ab]

def sc_wmem(aa: int, ab: int, ac: int) -> None:
    global mem
    global reg
    aa, ab = deref([aa, ab])
    mem[aa] = ab

def sc_call(aa: int, ab: int, ac: int) -> None:
    global stk
    global ptr
    sc_push(ptr, ab, ac)
    sc_jmp(aa, ab, ac)

def sc_ret(aa: int, ab: int, ac: int) -> None:
    global stk
    aa = stk.pop()
    sc_jmp(aa, ab, ac)

def sc_out(aa: int, ab: int, ac: int) -> None:
    print(chr(aa), end="")

def sc_in(aa: int, ab: int, ac: int) -> None:
    global reg
    reg[aa] = ord(input()[0])

def sc_noop(aa: int, ab: int, ac: int) -> None:
    return

def run() -> None:
    global ptr

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
        oc, aa, ab, ac = getins(ptr)
        #print(ptr, oc, aa, ab, ac, reg)

        try:
            d[oc](aa, ab, ac)
        except KeyError:
            print(oc, "not implemented", ptr, oc, aa, ab, ac)


if __name__ == "__main__":
    fn = sys.argv[1]

    init(fn)
    run()


