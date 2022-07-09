kernel void sha256_test(global uchar *w, global int *len) {
}

kernel void increment_int(global uchar *x, global u32 *y) {
    // *y = *x + 1;
    u32 a = *x;
    *y = a + 2;
}

kernel void hello() {
    printf("Hello, world!!\n");
}

void reverse(global uchar *s, int len) {
    int i, j;
    uchar c;
    for (i = 0, j = len - 1; i < j; i++, j--) {
        c = s[i];
        s[i] = s[j];
        s[j] = c;
    }
}

kernel void itoa(global ulong *number, global uchar *output) {
    ulong i, sign;
    ulong n = *number;

    if ((sign = n) < 0) {
        n = -n;
    }
    i = 0;
    do {
        output[i++] = n % 10 + '0';
    } while ((n /= 10) > 0);
    if (sign < 0) {
        output[i++] = '-';
    }
    output[i] = '\0';
    reverse(output, i);
}
