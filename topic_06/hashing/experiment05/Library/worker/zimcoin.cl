kernel void single_hash(global uchar *w, global int *len, global unsigned int *hash)
{
    // initialize the input buffer
    unsigned int input_buffer[32];
    for (int i = 0; i < 32; i++) {
        input_buffer[i] = 0;
    }

    // convert the char array to an unsigned integer array
    for (int i = 0; i < *len; i += 4) {
        uchar w_3 = ( (i + 3) < *len) ? w[i + 3] : 0;
        uchar w_2 = ( (i + 2) < *len) ? w[i + 2] : 0;
        uchar w_1 = ( (i + 1) < *len) ? w[i + 1] : 0;
        uchar w_0 = ( (i + 0) < *len) ? w[i + 0] : 0;

        input_buffer[i / 4] = (w_3 << 24) | (w_2 << 16) | (w_1 << 8) | w_0;
    }

    hash_priv_to_glbl(&input_buffer, *len, hash);
}