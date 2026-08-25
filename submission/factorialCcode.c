#include <stdio.h>

int main() {
    int n, a = 1;
    scanf("%d", &n);
    if (n <= 1) {
        a = 0;
        }
    else{
        for (int i = n-3; i >= 0; i++) {
            if (n % (i+2) == 0) {
                a = 0;
                break;
            }
        }
    }
    if (a) {
        printf("prime");
    } else {
        printf("not a prime");
    }
    return 0;
}
