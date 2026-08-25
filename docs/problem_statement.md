# Problem statement

**EG 212 Computer Architecture — Assignment 1: IAS processor design**
IIIT Bangalore, Feb 2024. Individually or in groups of at most three, in any
language.

Summarised from the course handout, which is not redistributed here. The
report submitted against this brief is [`report.pdf`](report.pdf).

## What was asked

**1. C and assembly programming.** Pick a C program — matrix multiplication,
sorting, factorial, encoding — and hand-write the equivalent IAS assembly. Once
assembled, the program had to exercise load, store, jump and ALU instructions.
At least **two new instructions** had to be added to the ISA, each given a new
opcode and a described operation, and actually used in the program; the
8085/8086 sets were suggested as a model.

**2. Assembler.** Read that assembly program in and emit machine code, verified
against the IAS instruction set.

**3. Processor.** Model the IAS datapath — AC, MQ, PC, IR, IBR, MAR, MBR, the
ALU and memory — and run the machine code from step 2 by fetch, decode and
execute, one instruction cycle per instruction. Memory could be a fixed-size
array rather than 2^40 words.

The brief was specific about the level of detail expected. `LOAD M(X)` had to
be shown as `MAR ← PC`, `MBR ← M[MAR]`, `AC ← MBR` step by step, and *not*
coded directly as `AC ← M(X)`. Control circuitry generating MemRead and
MemWrite was expected; gate-level design was not.

## How this repository answers it

| Requirement | Where |
|---|---|
| C program | [`programs/factorial.c`](../programs/factorial.c) |
| IAS assembly | [`programs/factorial.asm`](../programs/factorial.asm) |
| Load / store / jump / ALU | `LOAD`, `STOR`, `JUMP+`, `MUL` — see [ISA.md](ISA.md) |
| Two or more new instructions | `COMPARE`, `DEC`, `HALT` — three were added |
| Assembler | [`ias/assembler.py`](../ias/assembler.py) |
| Machine code | [`programs/factorial.bin.txt`](../programs/factorial.bin.txt) |
| Processor with all seven registers | [`ias/processor.py`](../ias/processor.py) |
| Step-by-step register transfers | `--trace`; sample in the [README](../README.md) |
| MemRead / MemWrite signals | `Processor.mem_read` / `Processor.mem_write` |
| Report | [`report.pdf`](report.pdf) |
