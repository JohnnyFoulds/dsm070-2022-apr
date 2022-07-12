#define max_nonce 16

int count_leading_zeros(unsigned int *hash)
{
    // /unsigned int x = hash[0];
    int count = 0;

    unsigned char c[32];
    for (int w = 0; w < 8; w++) {
        c[0 + w*4] = hash[w] & 0xff;
        c[1 + w*4] = (hash[w] >> 8) & 0xff;
        c[2 + w*4] = (hash[w] >> 16) & 0xff;
        c[3 + w*4] = (hash[w] >> 24) & 0xff;        
    }

    for (int i = 0; i < 32; i++) {
        if (c[i] > 9) {
            return count;
        }
        if ((c[i] > 0) && (c[i] < 9)) {
            return (count + 1);
        }

        if (c[i] == 0) {
            count += 2;
        } 
    }


    // c[0] = rgba & 0xff;
    // c[1] = (rgba >> 8) & 0xff;
    // c[2] = (rgba >> 16) & 0xff;
    // c[3] = (rgba >> 24) & 0xff;

    // for (int w = 0; w < 8; w++) {
    //     signed char *p = (uchar *)&hash[w];
    //     for (int c = 0; c < 4; c++) {
    //         if (p[c] > 9) {
    //             return count;
    //         }
    //         count++;
    //     }
    // }

    // int count = 0;
    // int zeros = 0;
    // for (int w = 0; w < 8; w++) {
    //     signed char *p = (unsigned char*)&hash[w];
    //     for (int c = 0; c < 4; c++) {
    //         zeros = __builtin_clz(p[c]);
    //         if (zeros == 0) {
    //             return count;
    //         }
    //         count += zeros;
    //     }
    // }


    // int count = 0;
    // int zeros = 0;

    // for (int w = 0; w < 8; w++) {
    //     x = hash[w];
    //     zeros = __builtin_clz(x);
    //     if (zeros != 0) {
    //         count += zeros;
    //     }
    //     else {
    //         return count;
    //     }
    // }



    // int n = 32;
    // unsigned y;

    // y = x >>16; if (y != 0) { n = n -16; x = y; }
    // y = x >> 8; if (y != 0) { n = n - 8; x = y; }
    // y = x >> 4; if (y != 0) { n = n - 4; x = y; }
    // y = x >> 2; if (y != 0) { n = n - 2; x = y; }
    // y = x >> 1; if (y != 0) return n - 2;
    // return n - x;
}

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

kernel void get_single_hash(global uchar *w, global int *len,
global unsigned int *hash, global uchar *leading_zeros)
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

    *leading_zeros = count_leading_zeros(loc_hash);
}

// miller_generator source: https://github.com/emb-team/opencl_random
uchar miller_generator(unsigned int seed, uchar start, uchar end)
{
    unsigned int a = 16807;
    unsigned int m = 2147483647;

    unsigned int final, val;
    final = 0;
    seed = (a * seed) % m;
    for (int j = 0; j < 4; j++) {
        val = 0;
        val = ((seed & (0xff << j*8)) >> j*8) % (end - start + 1) + start;
        final = final | (val << j*8);
    }
    return final;
}

// https://stackoverflow.com/questions/9912143/how-to-get-a-random-number-in-opencl
unsigned int random_xorshift(unsigned int seed)
{
    uint t = seed ^ (seed << 11);  
    return seed ^ (seed >> 19) ^ (t ^ (t >> 8));
}

uchar random_generator(unsigned int *seed, uchar start, uchar end)
{
    int gid = get_global_id(0);
    *seed = (*seed * (gid + 1)) + 1;

    return random_xorshift(*seed) % (end - start + 1) + start;
}

kernel void get_random_numbers(global unsigned int *seed, global uchar *start,
    global uchar *end, global unsigned int *len, global uchar *res_g)
{
    unsigned int local_seed = *seed;

    for (int i = 0; i < *len; i++) {
        res_g[i] = random_generator(&local_seed, *start, *end);
        *seed = local_seed;
    }
}

void generate_random_string(unsigned int *seed, uchar *w, uchar *len)
{
    // initialize the output buffer
    for (int i = 0; i < max_nonce; i++) {
        w[i] = 0;
    }

    // generate the string
    *len = random_generator(seed, 1, max_nonce);
    for (int i = 0; i < *len; i++) {
        w[i] = random_generator(seed, 32, 126);
    }
}

kernel void get_random_string(global unsigned int *seed, global uchar* w, 
    global uchar* len)
{
    // generate the random string
    unsigned int loc_seed = *seed;
    uchar loc_w[max_nonce];
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
    
    uchar loc_w[512];
    for (int i = 0; i < *len; i++) {
        loc_w[i] = w[i];
    }
    uchar loc_nonce[max_nonce];
    uchar loc_nonce_len;
    unsigned int loc_hash[8];

    // get the single hash with a random nonce
    single_hash_nonce(&loc_seed, loc_w, *len, loc_nonce, &loc_nonce_len, loc_hash);

    // assign the output
    *nonce_len = loc_nonce_len;
    for (int i = 0; i < *nonce_len; i++) {
        nonce[i] = loc_nonce[i];
    }

    for (int i=0; i<8; i++) {
        hash[i] = loc_hash[i];
    }
}

kernel void mine_nonce(
    global unsigned int *seed,
    global unsigned int *window_size,
    global uchar *w, global int *len,
    global uchar *nonce, global uchar *nonce_len)
{
    for (int i = 0; i < 65; i++) {
        nonce_len[i] = 0;
    }

    unsigned int loc_seed = *seed + get_global_id(0);
    uchar loc_w[512];
    for (int i = 0; i < *len; i++) {
        loc_w[i] = w[i];
    }

    uchar loc_nonce[max_nonce];
    uchar loc_nonce_len;
    unsigned int hash[8];
    int next_open_slot = 0;

    unsigned int loc_window_size = *window_size;
    int loc_len = *len;

    for (unsigned int i = 0; i < loc_window_size; i++) {
        single_hash_nonce(&loc_seed, loc_w, loc_len, loc_nonce, &loc_nonce_len, hash);

        int leading_zeros = count_leading_zeros(hash);
        if (leading_zeros > next_open_slot) {
            nonce_len[leading_zeros] = loc_nonce_len;
            for (int j = 0; j < loc_nonce_len; j++) {
                nonce[leading_zeros * max_nonce + j] = loc_nonce[j];
            }

            if (leading_zeros == next_open_slot+1) {
                next_open_slot++;
            }
        }
    }
}
