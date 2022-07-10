kernel void sha256_test(global uchar *w, global int *len, global u32 *hash) {
    // ulong number = 1234;
    // sha256_ctx_t ctx;

    // int input_len = *len * sizeof(u32);
    // u32 input[256];
    // for (int i = 0; i < *len; i++) {
    //     input[i] = w[i];
    // }

    // manually create the input for now assuming len is 4
    int input_len = 256;
    u32 input_buffer[256];

    input_buffer[0] = (w[3] << 24) | (w[2] << 16) | ( w[1] << 8 ) | (w[0]);
    for (int i = 1; i < 256; i++) {
        input_buffer[i] = input_buffer[0];
    }

    sha256_init(&ctx);
    sha256_update(&ctx, &input, len);
    //sha256_update(&ctx, &input_buffer, &input_len);
    sha256_final(&ctx);


    // sha256_init(&ctx);
    // sha256_update(&ctx, w, len);
    // //sha256_update(&ctx, &input, len);
    // sha256_final(&ctx);

    for (int i = 0; i < 8; i++) {
        hash[i] = ctx.h[i];
        //hash[i] = input_buffer[0];
    }
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
