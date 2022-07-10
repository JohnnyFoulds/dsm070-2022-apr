void single_hash(uchar *w, int len, unsigned int *hash)
{
    // initialize the input buffer
    unsigned int input_buffer[32];
    for (int i = 0; i < 32; i++) {
        input_buffer[i] = 0;
    }

    // convert the char array to an unsigned integer array
    for (int i = 0; i < len; i += 4) {
        uchar w_3 = ( (i + 3) < len) ? w[i + 3] : 0;
        uchar w_2 = ( (i + 2) < len) ? w[i + 2] : 0;
        uchar w_1 = ( (i + 1) < len) ? w[i + 1] : 0;
        uchar w_0 = ( (i + 0) < len) ? w[i + 0] : 0;

        input_buffer[i / 4] = (w_3 << 24) | (w_2 << 16) | (w_1 << 8) | w_0;
    }

    hash_private(input_buffer, len, hash);
}

kernel void get_single_hash(global uchar *w, global int *len, global unsigned int *hash)
{
    unsigned int loc_hash[8];
    uchar loc_w[512];

    for (int i = 0; i < *len; i++) {
        loc_w[i] = w[i];
    }

    // get the single hash
    single_hash(loc_w, *len, loc_hash);

    // assign the output
    for (int i=0; i<8; i++) {
        hash[i] = loc_hash[i];
    }
}

// miller_generator source: https://github.com/emb-team/opencl_random
uchar miller_generator(unsigned int *seed, uchar start, uchar end)
{
    unsigned int a = 16807;
    unsigned int m = 2147483647;
    int gid = get_global_id(0);

    *seed = *seed * (gid + 1);

    unsigned int final, val;
    final = 0;
    *seed = (a * *seed) % m;
    for (int j = 0; j < 4; j++) {
        val = 0;
        val = ((*seed & (0xff << j*8)) >> j*8) % (end - start + 1) + start;
        final = final | (val << j*8);
    }
    return final;
}

kernel void get_random_numbers(global unsigned int *seed, global uchar *start,
    global uchar *end, global unsigned int *len, global uchar *res_g)
{
    unsigned int local_seed = *seed;

    for (int i = 0; i < *len; i++) {
        res_g[i] = miller_generator(&local_seed, *start, *end);
    }
}

void generate_random_string(unsigned int *seed, uchar *w, uchar *len)
{
    // initialize the output buffer
    for (int i = 0; i < 16; i++) {
        w[i] = 0;
    }

    // generate the string
    *len = miller_generator(seed, 0, 16);
    for (int i = 0; i < *len; i++) {
        w[i] = miller_generator(seed, 32, 126);
    }
}

kernel void get_random_string(global unsigned int *seed, global uchar* w, 
    global uchar* len)
{
    // generate the random string
    unsigned int loc_seed = *seed;
    uchar loc_w[16];
    uchar loc_len;

    generate_random_string(&loc_seed, loc_w, &loc_len);

    // set the return values
    len[0] = loc_len;
    for (int i = 0; i < loc_len; i++) {
        w[i] = loc_w[i];
    }
}

void single_hash_nonce(
    unsigned int *seed,
    uchar *w, int len, 
    uchar *nonce, uchar *nonce_len,
    unsigned int *hash)
{
    // initialize the input buffer
    uchar input_buffer[512];
    for (int i = 0; i < len; i++) {
        input_buffer[i] = w[i];
    }

    // generate the random string
    generate_random_string(seed, nonce, nonce_len);
    for (int i = 0; i < *nonce_len; i++) {
        nonce[i] = nonce[i];
    }

    // add the nonce to the input buffer
    int input_len = len + *nonce_len;
    for (int i = 0; i < *nonce_len; i++) {
        input_buffer[len + i] = nonce[i];
    }

    // get the hash
    single_hash(input_buffer, input_len, hash);
}

kernel void get_single_hash_nonce(
    global unsigned int *seed,
    global uchar *w, global int *len, 
    global uchar *nonce, global uchar *nonce_len,
    global unsigned int *hash)
{
    unsigned int loc_seed = *seed;

    // initialize the input buffer
    uchar input_buffer[512];
    for (int i = 0; i < *len; i++) {
        input_buffer[i] = w[i];
    }

    // generate the random string
    uchar loc_nonce[16];
    uchar loc_nonce_len;
    generate_random_string(&loc_seed, loc_nonce, &loc_nonce_len);
    for (int i = 0; i < loc_nonce_len; i++) {
        nonce[i] = loc_nonce[i];
    }

    *nonce_len = loc_nonce_len;

    // add the nonce to the input buffer
    int input_len = *len + loc_nonce_len;
    for (int i = 0; i < loc_nonce_len; i++) {
        input_buffer[*len + i] = loc_nonce[i];
    }

    // // get the hash
    unsigned int loc_hash[8];
    single_hash(input_buffer, input_len, loc_hash);

    for (int i=0; i<8; i++) {
        hash[i] = loc_hash[i];
    }
}