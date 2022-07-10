kernel void single_hash(global uchar *w, global int *len, global unsigned int *hash)
{
    // manually create the input for now assuming len is 4
    unsigned int input_buffer[32];

    input_buffer[0] = (w[3] << 24) | (w[2] << 16) | ( w[1] << 8 ) | (w[0]);
    for (int i = 1; i < 32; i++) {
        input_buffer[i] = 0;
    } 

    hash_priv_to_glbl(&input_buffer, 4, hash);
}

// __kernel void single_hash(__global const inbuf * inbuffer, __global outbuf * outbuffer)
// {
//     // test word "hels"
//     //uchar w[4] = {104, 101, 108, 115};

//     // test word "hell"
//     uchar w[4] = {104, 101, 108, 108};

//     // manually create the input for now assuming len is 4
//     unsigned int input_buffer[32];

//     input_buffer[0] = (w[3] << 24) | (w[2] << 16) | ( w[1] << 8 ) | (w[0]);
//     for (int i = 1; i < 32; i++) {
//         input_buffer[i] = 0;
//     } 

//     unsigned int idx = get_global_id(0);
//     hash_priv_to_glbl(&input_buffer, 4, outbuffer[idx].buffer);

// /*
//     // --- the below test give the correct result ---
//     //hash_global(inbuffer[idx].buffer, inbuffer[idx].length, outbuffer[idx].buffer);

//     unsigned int new_buffer[inBufferSize];
//     for (int i = 0; i < inBufferSize; i++) {
//         new_buffer[i] = inbuffer[idx].buffer[i];
//     }

//     hash_priv_to_glbl(&new_buffer, inbuffer[idx].length, outbuffer[idx].buffer);
//     // ---
// */


//     //word buffer[inBufferSize];

//     // for (int i = 0; i < inBufferSize; i++) {
//     //     buffer[i] = inbuffer[idx].buffer[i];
//     // }

// // the below shows the input buffer
//     // hash_global(inbuffer[idx].buffer, inbuffer[idx].length, outbuffer[idx].buffer);

//     //  for (int i = 0; i < outBufferSize; i++) {
//     //     //outbuffer[idx].buffer[i] = 0;
//     //     outbuffer[idx].buffer[i] = new_buffer[i];
//     // }
//     // outbuffer[idx].buffer[0] = new_buffer[0];
// }