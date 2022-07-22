#define max_nonce 16

#ifndef NULL
#define NULL 0L
#endif

/*
 * This helper function is used to count the number of leading hex zeros
 * as used during the prize activity.
 */
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
        if (c[i] > 0xf) {
            return count;
        }
        if ((c[i] > 0) && (c[i] <= 0xf)) {
            return (count + 1);
        }

        if (c[i] == 0) {
            count += 2;
        } 
    }
}

/*
 * Calculate the hash value for the input string.
 */
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

    __private unsigned int hash_priv[8];
    hash_private(input_buffer, len, hash_priv);

    for (int i = 0; i < 8; i++) {
        hash[i] = hash_priv[i];
    }
}

/*
 * Tis kernel calculates the hash value for the input string and outputs
 * the hash value and number of leading hex zeros.
 */
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

#define max_seq_nonce_len 20
#define max_seq_output_size 256

/*
 * Convert the seed to a string and compute the hash value.
 */
void hash_seed(
    unsigned long seed,
    uchar *w, int len, 
    uchar *nonce, uchar *nonce_len,
    unsigned int *hash)
{
    *nonce_len = 0;

    // initialize nonce buffer
    uchar nonce_reverse[max_seq_nonce_len];
    for (int i = 0; i < max_seq_nonce_len; i++) {
        nonce[i] = 0;
        nonce_reverse[i] = 2;
    }

    // handle zero
    if (seed == 0) {
        *nonce_len = 1;
        nonce[0] = 48;
        return;
    }

    // convert the seed to a string
    while (seed > 0) {
        *nonce_len += 1;
        nonce_reverse[*nonce_len-1] = (seed % 10) + 48;
        seed = seed / 10;
    }

    // reverse the numbers
    for (int i = 0; i < *nonce_len; i++) {
        //nonce[i] = nonce_reverse[i];
        nonce[*nonce_len - 1 -i]  = nonce_reverse[i];
    }

    // start the actual hashing
    // initialize the input buffer
    uchar input_buffer[512];
    for (int i = 0; i < len; i++) {
        input_buffer[i] = w[i];
    }

    // add the nonce to the input buffer
    int input_len = len + *nonce_len;
    for (int i = 0; i < *nonce_len; i++) {
        input_buffer[len + i] = nonce[i];
    }

    // get the hash
    single_hash(input_buffer, input_len, hash);
}

/**
 * This kernel was used during the competition to find a nonce that
 * creates a hash with the most leading zeros.
 */
kernel void mine_nonce_sequential(
    global unsigned long *seed,
    global unsigned int *window_size,
    global uchar *w, global int *len,
    global uchar *nonce, global uchar *nonce_len
)
{
    for (int i = 0; i < max_seq_output_size; i++) {
        nonce_len[i] = 0;
    }

    unsigned long start_index = *seed + (get_global_id(0) * *window_size);

    uchar loc_w[512];
    for (int i = 0; i < *len; i++) {
        loc_w[i] = w[i];
    }

    uchar loc_nonce[max_seq_nonce_len];
    uchar loc_nonce_len;
    unsigned int hash[8];

    unsigned int loc_window_size = *window_size;
    int loc_len = *len;
    unsigned long current_index = start_index;

    for (unsigned int i = 0; i < loc_window_size; i++) {
        hash_seed(current_index, loc_w, loc_len, loc_nonce, &loc_nonce_len, hash);
        int leading_zeros = count_leading_zeros(hash);

        if ((leading_zeros > 0) && (nonce_len[leading_zeros] == 0)) {

            // output the nonce
            nonce_len[leading_zeros] = loc_nonce_len;
            for (int j = 0; j < max_seq_nonce_len; j++) {
                nonce[leading_zeros * max_seq_nonce_len + j] = loc_nonce[j];
            }
        }
        current_index++;
    }
}

/**
 * This is a test kernel created to develop the functionality to hash
 * block data with a unsingned long nonce value.
 */
kernel void get_hashed_nonce(global unsigned int *w, global int *len,
    global unsigned long *nonce, global unsigned int *hash)
{
    *nonce = 9223372036854775807;

    // create the private input buffer
    __private unsigned int input_buffer[256];

    // initialize the input buffer
    for (int i = 0; i < *len / 4; i++) {
        input_buffer[i] = w[i];
    }

    // add the nonce to the input buffer
    input_buffer[*len / 4] = *nonce & 0xFFFFFFFF;
    input_buffer[(*len + 4) / 4] = (*nonce >> 32);

    hash_priv_to_glbl(&input_buffer, *len + 8, hash);
}

/**
 * This function is used to test if the hash value is less than or equal
 * to the target value.
 */
bool is_target_met(unsigned int *hash, unsigned int *target)
{
    for (int i = 0; i < 8; i++) {
        uchar* hash_word = (uchar*)&hash[i];
        uchar* target_word = (uchar*)&target[i];

        for (int j = 0; j < 4; j++) {
            if (hash_word[j] > target_word[j]) {
                return false;
            }
            else if (hash_word[j] < target_word[j]) {
                return true;
            }
        }
    }

    return true;
}

/**
 * Using a sequential search find a nonce that meets the target
 * requirement.
 *
 * NOTE: For real world applications, a random search pattern should
 * be used instead to find the nonce.
 */
kernel void mine_sequential(
    global unsigned long *seed,
    global unsigned int *window_size,
    global unsigned int *block_data,
    global int *block_data_len,
    global unsigned long *nonce,
    global unsigned int *target,
    global unsigned int *output_hash)
{
    // set the start index for the thread
    unsigned long start_nonce = *seed + (get_global_id(0) * *window_size);

    if (get_global_id(0) == 0)
          *nonce = 0;

    // initialize the input buffer
    __private unsigned int input_buffer[256];
    
    for (int i = 0; i < *block_data_len / 4; i++) {
        input_buffer[i] = block_data[i];
    }

    // copy the target to local memory
    unsigned int loc_target[8];
    for (int i = 0; i < 8; i++) {
        loc_target[i] = target[i];
    }

    // attempt a sequation search for the nonce
    unsigned int hash[8];
    unsigned long current_nonce = start_nonce;

    for (unsigned int i = 0; i < *window_size; i++) {
        // if the nonce has been set in another thread stop the search
        if (*nonce != 0) {
            return;
        }

        // add the nonce to the input buffer
        input_buffer[*block_data_len / 4] = current_nonce & 0xFFFFFFFF;
        input_buffer[(*block_data_len + 4) / 4] = (current_nonce >> 32);

        // get the hash value
        hash_private(input_buffer, *block_data_len + 8, hash);

        // check if the hash is less than or equal to the target
        if (is_target_met(hash, loc_target)) {
            *nonce = current_nonce;

            if (output_hash != NULL) {
                for (int j = 0; j < 8; j++) {
                    output_hash[j] = hash[j];
                }
            }

            return;
        }

        // set the next nonce to try
        current_nonce++;
    }
}


