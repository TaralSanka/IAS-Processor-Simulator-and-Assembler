/* factorial.c -- the C program that programs/factorial.asm implements.
 *
 * The loop below maps one-to-one onto the assembly:
 *   n        lives in M(0) and is counted down to zero
 *   product  lives in M(7) and holds n! when the loop ends
 *
 * There is no input instruction in this ISA, so n is a constant that the
 * assembler places in M(0); change the first data word of factorial.asm
 * to compute a different factorial.
 */

#include <stdio.h>

int main(void)
{
    int n = 5;         /* M(0) */
    int product = 1;   /* M(7) */

    while (n > 0) {    /* COMPARE M(0) / JUMP+ M(6) */
        product *= n;  /* LOAD MQ,M(7); LOAD M(0); MUL M(0); STOR M(7) */
        n -= 1;        /* LOAD M(0); DEC; STOR M(0) */
    }                  /* JUMP+ M(2) */

    printf("%d\n", product);
    return 0;
}
