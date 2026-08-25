# IAS Processor Simulator and Assembler

A register-level simulator of the **IAS machine** — the 1952 von Neumann
computer at the Institute for Advanced Study — together with an assembler that
targets it, both in Python with no dependencies.

The simulator models all seven IAS registers (AC, MQ, PC, IR, IBR, MAR, MBR)
and an explicit fetch–decode–execute cycle over *both* half-instructions of
each 40-bit word. Memory is reachable only through MAR and MBR under a MemRead
or MemWrite signal, so a run can be traced as the sequence of register
transfers a real datapath would perform, rather than as `AC ← M(X)` in one
step.

## Quick start

Python 3.6+, nothing to install.

```bash
python -m ias.assembler programs/factorial.asm -o programs/factorial.bin.txt
```

```bash
python -m ias.processor programs/factorial.bin.txt --result 7
```

```
halted after 22 instruction cycles
AC = 0   MQ = 120   PC = 7
M(7) = 120
```

`M(7) = 120` is 5!. Add `--trace` to print every register transfer.

## Layout

```
ias/
  isa.py          instruction table + bit helpers, shared by both tools
  assembler.py    assembly source  ->  40-bit machine code
  processor.py    machine code     ->  simulated execution
programs/
  factorial.c            the C program being implemented
  factorial.asm          its hand-written IAS assembly
  factorial.bin.txt      machine code, as emitted by the assembler
docs/
  ISA.md                 word format, opcode table, added instructions
  problem_statement.md   the assignment, and where each part is answered
  report.pdf             the report submitted with it
tests/                   end-to-end tests
submission/              the original Feb 2024 files, unmodified
```

The opcode table lives in exactly one place, `ias/isa.py`, and both the
assembler and the simulator are driven by it — adding an instruction means
adding a row and one `_op_<opcode>` method.

## The machine

A 40-bit word packs two half-instructions, each an 8-bit opcode and a 12-bit
address:

```
 0        7 8            19 20      27 28           39
+----------+---------------+----------+---------------+
|  opcode  |    address    |  opcode  |    address    |
+----------+---------------+----------+---------------+
        left half                  right half
```

One instruction cycle fetches a word and executes both halves:

```
FETCH    MAR <- PC                       DECODE   IR  <- IBR(0:7)
         MBR <- M[MAR]   (MemRead)                MAR <- IBR(8:19)
         PC  <- PC + 1                   EXEC     ... right half ...
DECODE   IR  <- MBR(0:7)
         MAR <- MBR(8:19)
         IBR <- MBR(20:39)
EXEC     ... left half ...
```

Execution starts at M(1), leaving M(0) for data.

## The program

[`programs/factorial.c`](programs/factorial.c) computes `n!` by repeated
multiplication. [`programs/factorial.asm`](programs/factorial.asm) is its
hand-written translation, exercising load, store, conditional-jump and
multiply paths:

```asm
5                                      ; M(0) = n

COMPARE M(0)    JUMP+ M(6,0:19)        ; M(1) if n <= 0, skip the loop
LOAD MQ, M(7)   LOAD M(0)              ; M(2) MQ = product, AC = n
MUL M(0)        STOR M(7)              ; M(3) product = product * n
LOAD M(0)       DEC                    ; M(4) AC = n - 1
STOR M(0)       JUMP+ M(2,0:19)        ; M(5) n = n - 1, repeat while n > 0
NOP             HALT                   ; M(6) done

1                                      ; M(7) product, seeded to 1
```

| Word | Holds |
|---|---|
| M(0) | `n`, doubling as the loop counter, counted down to 0 |
| M(1)–M(6) | the program |
| M(7) | the running product; `n!` when the machine halts |

Change the first data word to compute a different factorial.

### ISA additions

Three instructions were added to the IAS set for this program — `COMPARE`,
`DEC` and `HALT`. The base ISA has only one conditional branch, `JUMP+`, which
tests for a strictly positive AC; `COMPARE M(X)` turns "M(X) has reached zero"
into a sign that `JUMP+` can test, which is what lets the loop terminate and
handle `n = 0` without a special case. `DEC` replaces a `SUB` against a
memory-resident constant 1, and `HALT` stops the cycle instead of letting the
PC run off the end of the program.

Full opcode table, encodings, and the deviations from the standard IAS set:
**[docs/ISA.md](docs/ISA.md)**.

## Tracing a run

`--trace` shows each register transfer, with the control signal that drives
memory. One cycle of the loop, executing `MUL M(0)` then `STOR M(7)`:

```
--- cycle 3 ----------------------------------------------
FETCH    MAR <- PC                    MAR = 000000000011 (3)
         MBR <- M[MAR]   (MemRead)    MBR = 1000101100000000000000100001000000000111
         PC  <- PC + 1                PC  = 000000000100 (4)
DECODE   IR  <- MBR(0:7)              IR  = 10001011  MUL M()
         MAR <- MBR(8:19)             MAR = 000000000000 (0)
         IBR <- MBR(20:39)            IBR = 00100001000000000111
EXEC     MBR <- M[MAR]   (MemRead)    MBR = 0000000000000000000000000000000000000101
         AC  <- MQ x MBR              AC  = 0000000000000000000000000000000000000101 (5)
DECODE   IR  <- IBR(0:7)              IR  = 00100001  STOR M()
         MAR <- IBR(8:19)             MAR = 000000000111 (7)
EXEC     MBR <- AC                    MBR = 0000000000000000000000000000000000000101
         M[MAR] <- MBR   (MemWrite)   M[7] = 0000000000000000000000000000000000000101
```

## Tests

```bash
python tests/test_toolchain.py
```

14 checks, covering both tools end to end: every emitted word is 40 bits and
splits into a known opcode plus a 12-bit address; the assembler's output
matches the machine code in `programs/` and in `submission/`; the simulator
computes `n!` correctly for `n = 0..7`; `n = 0` skips the loop in two cycles;
and malformed input — an unknown mnemonic, a missing address, an undefined
opcode, a program with no `HALT` — is rejected with a diagnostic rather than
a stack trace.

`pytest tests/` works too.

## Assignment

Written for EG 212 Computer Architecture (IIIT Bangalore), Feb 2024. What was
asked, and where each part is answered, is in
[docs/problem_statement.md](docs/problem_statement.md); the submitted report
is [docs/report.pdf](docs/report.pdf). The submitted files themselves are
kept in [`submission/`](submission/).

## Credits

Done in a group of three:

- Kotyada Parthiv (IMT2023559)
- Taral Sri Sai Ram (IMT2023588)
- Dheeraj Muppiri (IMT2023596)
