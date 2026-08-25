; factorial.asm -- computes n! for the n held in M(0).
;
; Memory map
;   M(0)  n, used as the loop counter and counted down to 0
;   M(7)  running product; seeded with 1 and holding n! at HALT
;
; One line = one 40-bit word.  Two spaces separate the left and right
; half-instruction of a word; a bare integer is a data word.

5                                      ; M(0) = n

COMPARE M(0)    JUMP+ M(6,0:19)        ; M(1) if n <= 0, skip the loop
LOAD MQ, M(7)   LOAD M(0)              ; M(2) MQ = product, AC = n
MUL M(0)        STOR M(7)              ; M(3) product = product * n
LOAD M(0)       DEC                    ; M(4) AC = n - 1
STOR M(0)       JUMP+ M(2,0:19)        ; M(5) n = n - 1, repeat while n > 0
NOP             HALT                   ; M(6) done

1                                      ; M(7) product, seeded to 1
