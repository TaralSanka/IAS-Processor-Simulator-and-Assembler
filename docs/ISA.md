# Instruction set

## Word format

The IAS word is 40 bits and holds **two** half-instructions. Both are decoded
and executed within a single instruction cycle: the left half runs from MBR,
the right half is buffered in IBR and runs immediately after.

```
 0        7 8            19 20      27 28           39
+----------+---------------+----------+---------------+
|  opcode  |    address    |  opcode  |    address    |
|  8 bits  |    12 bits    |  8 bits  |    12 bits    |
+----------+---------------+----------+---------------+
        left half                  right half
```

A 12-bit address field addresses 4096 words. The simulator allocates
`isa.MEMORY_WORDS` (256) by default, which is ample for these programs.

A word may instead hold **data**: a 40-bit two's-complement integer.
Nothing in the encoding distinguishes the two — as on the real IAS, a word is
an instruction only because the PC reaches it.

## Implemented instructions

| Mnemonic | Opcode | Standard IAS | Operation |
|---|---|---|---|
| `LOAD M(X)` | `00000001` | `00000001` | AC ← M(X) |
| `LOAD MQ, M(X)` | `00001001` | `00001001` | MQ ← M(X) |
| `STOR M(X)` | `00100001` | `00100001` | M(X) ← AC |
| `MUL M(X)` | `10001011` | `00001011` † | AC ← MQ × M(X) |
| `JUMP+ M(X,0:19)` | `00001111` | `00001111` | if AC > 0 then PC ← X |
| `NOP` | `00000000` | — ‡ | no operation |
| `COMPARE M(X)` | `10101010` | *new* | AC ← 1 if M(X) ≤ 0, else −1 |
| `DEC` | `11111111` | *new* | AC ← AC − 1 |
| `HALT` | `10000000` | *new* | stop the instruction cycle |

The last three are the instructions added for this assignment, and are the
ones described in the submitted [report](report.pdf); the rest keep
their standard IAS encodings, with two deviations carried over from the
original submission and kept here so the machine code stays reproducible:

- † `MUL` was assigned `10001011` rather than the standard `00001011`.
- ‡ `00000000` is not a defined IAS opcode; it is used here as `NOP` so the
  unused half of a word has something to hold.

Instructions with no operand (`NOP`, `DEC`, `HALT`) still occupy a full
20-bit half; their address field is emitted as zero and ignored.

### The instructions added for this assignment

**`COMPARE M(X)`** — compares M(X) against zero and leaves a flag in AC:
`+1` when M(X) ≤ 0, `−1` otherwise. It exists to pair with `JUMP+`, which is
the only conditional branch in the IAS and tests only for a strictly positive
AC. Together the two give a "branch when the counter reaches zero" that the
base ISA cannot express in one word, which is what the factorial loop needs
to handle `n = 0` without a special case.

**`DEC`** — decrements AC in place. The base ISA has `SUB M(X)`, which would
need a memory word holding the constant 1 and a memory read on every pass of
the loop. `DEC` is the single-cycle, ALU-only equivalent, in the spirit of the
8085 `DCR` instruction.

**`HALT`** — stops the instruction cycle. Without it the PC runs past the end
of the program into whatever follows it; the real IAS had no halt and relied on
an operator stopping the machine.

## Semantics worth stating

- **Number representation.** AC and MQ hold 40-bit two's-complement integers.
  The real IAS used sign-and-magnitude; two's complement is used here because
  it makes the store path a plain bit-width truncation.
- **`MUL`.** The real IAS leaves the 80-bit product in the AC:MQ pair, high
  half in AC. This design keeps the whole product in AC, which is exact for
  the operand widths these programs use.
- **A taken jump ends the word.** If `JUMP+` in the *left* half branches, the
  right half is not executed — the PC has already moved. In the *right* half
  the question does not arise. No program here puts a jump in the left half,
  so this choice does not affect the results.
- **`COMPARE` reads signed.** M(X) is interpreted as two's complement, so a
  stored negative value compares as negative rather than as a large unsigned
  quantity.

## Not implemented

The rest of the IAS set — `ADD`, `SUB`, `DIV`, `LSH`, `RSH`, unconditional
`JUMP`, the address-modify `STOR M(X,8:19)` forms, and the absolute-value and
negating loads — is not implemented, because the factorial program does not
use it. Adding one means a row in `INSTRUCTIONS` in [`ias/isa.py`](../ias/isa.py)
and a matching `_op_<opcode>` method on `Processor`; the assembler needs no
change, since it is driven entirely by that table.
