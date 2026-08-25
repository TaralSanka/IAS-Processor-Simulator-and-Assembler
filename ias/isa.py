"""Instruction set definition shared by the assembler and the simulator.

The IAS word is 40 bits wide and holds *two* half-instructions:

    bit  0 ..  7   left opcode    (8 bits)
    bit  8 .. 19   left address   (12 bits)
    bit 20 .. 27   right opcode   (8 bits)
    bit 28 .. 39   right address  (12 bits)

Keeping the table in one place is what stops the assembler and the
simulator from drifting apart -- the original submission encoded the
opcodes twice and the two copies disagreed on COMPARE and HALT.
"""

WORD_BITS = 40
OPCODE_BITS = 8
ADDRESS_BITS = 12
HALF_BITS = OPCODE_BITS + ADDRESS_BITS  # 20

#: Default number of 40-bit words in main memory M.
MEMORY_WORDS = 256


class Instruction:
    """One entry of the instruction table."""

    def __init__(self, mnemonic, opcode, has_address, description):
        self.mnemonic = mnemonic
        self.opcode = opcode              # 8-character string of '0'/'1'
        self.has_address = has_address    # False => address field is unused
        self.description = description

    def __repr__(self):
        return "Instruction(%r, %r)" % (self.mnemonic, self.opcode)


#: Canonical form of each mnemonic, with the operand stripped out.
#: ``LOAD M(0)`` normalises to ``LOAD M()``, ``JUMP+ M(6,0:19)`` to
#: ``JUMP+ M(,:)`` -- see :func:`normalise`.
INSTRUCTIONS = [
    # --- standard IAS instructions -------------------------------------
    Instruction("LOAD M()",     "00000001", True,  "AC <- M(X)"),
    Instruction("LOAD MQ, M()", "00001001", True,  "MQ <- M(X)"),
    Instruction("STOR M()",     "00100001", True,  "M(X) <- AC"),
    Instruction("MUL M()",      "10001011", True,  "AC <- MQ x M(X)"),
    Instruction("JUMP+ M(,:)",  "00001111", True,  "if AC > 0 then PC <- X"),
    Instruction("NOP",          "00000000", False, "no operation"),
    # --- instructions added for this assignment ------------------------
    Instruction("COMPARE M()",  "10101010", True,  "AC <- 1 if M(X) <= 0 else -1"),
    Instruction("DEC",          "11111111", False, "AC <- AC - 1"),
    Instruction("HALT",         "10000000", False, "stop the instruction cycle"),
]

BY_MNEMONIC = {i.mnemonic: i for i in INSTRUCTIONS}
BY_OPCODE = {i.opcode: i for i in INSTRUCTIONS}

NOP = BY_MNEMONIC["NOP"]
HALT = BY_MNEMONIC["HALT"]


def normalise(text):
    """Reduce a written instruction to its table key.

    Digits and whitespace inside the operand carry no opcode information,
    so ``LOAD MQ, M(7)`` and ``LOAD MQ, M(0)`` both key on ``LOAD MQ, M()``.
    """
    return "".join(c for c in text if not c.isdigit()).strip()


def to_bits(value, width):
    """Two's-complement bit string of ``value`` in ``width`` bits."""
    return format(value & ((1 << width) - 1), "0%db" % width)


def from_bits(bits, signed=False):
    """Inverse of :func:`to_bits`."""
    value = int(bits, 2)
    if signed and bits[0] == "1":
        value -= 1 << len(bits)
    return value
