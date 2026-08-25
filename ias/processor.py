"""Register-level simulator for the IAS machine.

The seven registers of the IAS are modelled explicitly:

    AC   40-bit accumulator
    MQ   40-bit multiplier-quotient register
    PC   12-bit program counter
    IR    8-bit instruction register (opcode being executed)
    IBR  20-bit instruction buffer register (the deferred right half)
    MAR  12-bit memory address register
    MBR  40-bit memory buffer register

Nothing reaches memory except through MAR/MBR under a MemRead or MemWrite
control signal, so a trace of a run shows the same register transfers a
hardware datapath would perform:

    Fetch:  MAR <- PC;  MBR <- M[MAR];  PC <- PC + 1
    Decode: IR <- MBR(0:7);  MAR <- MBR(8:19);  IBR <- MBR(20:39)
"""

import argparse

from . import isa


class Halt(Exception):
    """Raised by the HALT instruction to end the instruction cycle."""


class Jump(Exception):
    """Raised by a taken jump; the rest of the current word is skipped."""


class Processor:
    def __init__(self, memory, trace=False, start=1):
        self.M = list(memory)
        self.M.extend(["0" * isa.WORD_BITS] * (isa.MEMORY_WORDS - len(self.M)))

        self.AC = 0
        self.MQ = 0
        self.PC = start
        self.IR = "0" * isa.OPCODE_BITS
        self.IBR = "0" * isa.HALF_BITS
        self.MAR = 0
        self.MBR = "0" * isa.WORD_BITS

        self.trace = trace
        self.cycles = 0

    # -- trace helpers --------------------------------------------------

    def _log(self, phase, transfer, state):
        if self.trace:
            print("%-8s %-28s %s" % (phase, transfer, state))

    def _show_ac(self):
        return "AC  = %s (%d)" % (isa.to_bits(self.AC, isa.WORD_BITS), self.AC)

    def _show_mq(self):
        return "MQ  = %s (%d)" % (isa.to_bits(self.MQ, isa.WORD_BITS), self.MQ)

    def _show_addr(self, name, value):
        return "%s = %s (%d)" % (name, isa.to_bits(value, isa.ADDRESS_BITS), value)

    # -- memory access: the only two paths to M -------------------------

    def _check_mar(self):
        if not 0 <= self.MAR < len(self.M):
            raise ValueError(
                "MAR = %d is outside memory (%d words); a runaway PC or a "
                "program with no HALT is the usual cause" % (self.MAR, len(self.M))
            )

    def mem_read(self):
        """MemRead: MBR <- M[MAR]."""
        self._check_mar()
        self.MBR = self.M[self.MAR]

    def mem_write(self):
        """MemWrite: M[MAR] <- MBR."""
        self._check_mar()
        self.M[self.MAR] = self.MBR

    # -- instruction cycle ----------------------------------------------

    def fetch(self):
        self.MAR = self.PC
        self._log("FETCH", "MAR <- PC", self._show_addr("MAR", self.MAR))

        self.mem_read()
        self._log("", "MBR <- M[MAR]   (MemRead)", "MBR = %s" % self.MBR)

        self.PC += 1
        self._log("", "PC  <- PC + 1", self._show_addr("PC ", self.PC))

    def decode_left(self):
        self.IR = self.MBR[0:8]
        self.MAR = int(self.MBR[8:20], 2)
        self.IBR = self.MBR[20:40]
        self._log("DECODE", "IR  <- MBR(0:7)", "IR  = %s  %s" % (self.IR, self._mnemonic()))
        self._log("", "MAR <- MBR(8:19)", self._show_addr("MAR", self.MAR))
        self._log("", "IBR <- MBR(20:39)", "IBR = %s" % self.IBR)

    def decode_right(self):
        self.IR = self.IBR[0:8]
        self.MAR = int(self.IBR[8:20], 2)
        self._log("DECODE", "IR  <- IBR(0:7)", "IR  = %s  %s" % (self.IR, self._mnemonic()))
        self._log("", "MAR <- IBR(8:19)", self._show_addr("MAR", self.MAR))

    def _mnemonic(self):
        instruction = isa.BY_OPCODE.get(self.IR)
        return instruction.mnemonic if instruction else "<undefined>"

    def execute(self):
        instruction = isa.BY_OPCODE.get(self.IR)
        if instruction is None:
            raise ValueError("undefined opcode %s at PC=%d" % (self.IR, self.PC - 1))
        getattr(self, "_op_" + instruction.opcode)()

    # -- one handler per opcode -----------------------------------------

    def _op_00000001(self):
        """LOAD M(X):  AC <- M(X)"""
        self.mem_read()
        self._log("EXEC", "MBR <- M[MAR]   (MemRead)", "MBR = %s" % self.MBR)
        self.AC = isa.from_bits(self.MBR, signed=True)
        self._log("", "AC  <- MBR", self._show_ac())

    def _op_00001001(self):
        """LOAD MQ, M(X):  MQ <- M(X)"""
        self.mem_read()
        self._log("EXEC", "MBR <- M[MAR]   (MemRead)", "MBR = %s" % self.MBR)
        self.MQ = isa.from_bits(self.MBR, signed=True)
        self._log("", "MQ  <- MBR", self._show_mq())

    def _op_00100001(self):
        """STOR M(X):  M(X) <- AC"""
        self.MBR = isa.to_bits(self.AC, isa.WORD_BITS)
        self._log("EXEC", "MBR <- AC", "MBR = %s" % self.MBR)
        self.mem_write()
        self._log("", "M[MAR] <- MBR   (MemWrite)", "M[%d] = %s" % (self.MAR, self.MBR))

    def _op_10001011(self):
        """MUL M(X):  AC <- MQ x M(X)

        The real IAS leaves the 80-bit product in AC:MQ; this design keeps
        the product in AC alone, which is sufficient for the operand widths
        used by the programs here.
        """
        self.mem_read()
        self._log("EXEC", "MBR <- M[MAR]   (MemRead)", "MBR = %s" % self.MBR)
        self.AC = self.MQ * isa.from_bits(self.MBR, signed=True)
        self._log("", "AC  <- MQ x MBR", self._show_ac())

    def _op_00001111(self):
        """JUMP+ M(X,0:19):  if AC > 0 then PC <- X"""
        if self.AC > 0:
            self.PC = self.MAR
            self._log("EXEC", "AC > 0: PC <- MAR", self._show_addr("PC ", self.PC))
            raise Jump()
        self._log("EXEC", "AC <= 0: fall through", self._show_ac())

    def _op_00000000(self):
        """NOP"""
        self._log("EXEC", "no operation", "")

    def _op_10101010(self):
        """COMPARE M(X):  AC <- 1 if M(X) <= 0 else -1

        A compare-against-zero that pairs with JUMP+, which branches only on
        a strictly positive AC.  Together they give "jump when M(X) has
        counted down to zero".
        """
        self.mem_read()
        self._log("EXEC", "MBR <- M[MAR]   (MemRead)", "MBR = %s" % self.MBR)
        self.AC = -1 if isa.from_bits(self.MBR, signed=True) > 0 else 1
        self._log("", "AC  <- compare(MBR, 0)", self._show_ac())

    def _op_11111111(self):
        """DEC:  AC <- AC - 1"""
        self.AC -= 1
        self._log("EXEC", "AC  <- AC - 1", self._show_ac())

    def _op_10000000(self):
        """HALT: stop the instruction cycle."""
        self._log("EXEC", "halt", "")
        raise Halt()

    # -- driver ---------------------------------------------------------

    def step(self):
        """Run one instruction cycle: fetch, then both half-instructions."""
        self.cycles += 1
        if self.trace:
            print("\n--- cycle %d %s" % (self.cycles, "-" * 46))

        self.fetch()
        try:
            self.decode_left()
            self.execute()
            self.decode_right()
            self.execute()
        except Jump:
            pass

    def run(self, max_cycles=10000):
        for _ in range(max_cycles):
            try:
                self.step()
            except Halt:
                return self.cycles
        raise RuntimeError("no HALT after %d cycles" % max_cycles)

    def word(self, address, signed=True):
        """Read a memory word as an integer, for inspecting results."""
        return isa.from_bits(self.M[address], signed=signed)


def load_image(path):
    """Read a machine-code file into a list of 40-bit strings."""
    words = []
    with open(path) as handle:
        for number, line in enumerate(handle, start=1):
            bits = line.strip()
            if not bits:
                continue
            if len(bits) != isa.WORD_BITS or set(bits) - set("01"):
                raise ValueError("%s line %d: not a %d-bit word" % (path, number, isa.WORD_BITS))
            words.append(bits)
    return words


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run IAS machine code.")
    parser.add_argument("image", help="machine code file produced by the assembler")
    parser.add_argument("--trace", action="store_true", help="print every register transfer")
    parser.add_argument("--start", type=int, default=1, help="initial PC (default: 1)")
    parser.add_argument("--result", type=int, help="print M(ADDRESS) when the program halts")
    args = parser.parse_args(argv)

    cpu = Processor(load_image(args.image), trace=args.trace, start=args.start)
    cycles = cpu.run()

    print("\nhalted after %d instruction cycles" % cycles)
    print("AC = %d   MQ = %d   PC = %d" % (cpu.AC, cpu.MQ, cpu.PC))
    if args.result is not None:
        print("M(%d) = %d" % (args.result, cpu.word(args.result)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
