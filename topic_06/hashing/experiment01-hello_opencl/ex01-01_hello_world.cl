// #pragma OPENCL EXTENSION cl_khr_fp64: enable

kernel void summy(global float *a, global float *b, global float *c) {
    printf("%f\n", *a + *b + *c);
    *c = *a + *b;
}

// kernel void double_test(__global float* a,
//                           __global float* b,
//                           __global double* out) {
//    *out = (double)(*a / *b);
// }