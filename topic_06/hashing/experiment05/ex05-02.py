# %% [markdown]
# # Experiment 05-02

# %%
import numpy as np
import hashlib
from binascii import hexlify
import pyopencl as cl
from Library.opencl_information import opencl_information

# %% [markdown]
# ## Show the available Platforms

# %%
info = opencl_information()
info.print_full_info()

# %% [markdown]
# ## Configure the OpenCL Context

# %%
platform_number = 0
device_number = 0

cl_devices = cl.get_platforms()[platform_number].get_devices()
cl_ctx = cl.Context(cl_devices)
cl_queue = cl.CommandQueue(cl_ctx, cl_devices[device_number])

# %% [markdown]
# ## Compile the Program

# %%
def build_program(program_files : list, cl_ctx : cl.Context,
        build_options=[]) -> cl.Program:
    """
    Build a program from an OpenCL source file.

    Parameters
    ----------
    program_files : list
        The path to the OpenCL source files.
    cl_ctx : pyopencl.Context
        The context to build the program with.
    build_options : list of str
        The build options to use.

    Returns
    -------
    pyopencl.Program
    """
    program_source = ''

    for cl_file in program_files:
        with open(cl_file, 'r') as cl_file:
            file_source = cl_file.read()
            program_source += '\n' + file_source

    program_source = cl.Program(cl_ctx, program_source)
    program = program_source.build(options=build_options)
            
    return program

# %%
cl_program_files = [
    'Library/worker/sha256.cl',
    'Library/worker/zimcoin.cl',
]

cl_program = build_program(cl_program_files, cl_ctx)

# show the kernel names
program_kernel_names = cl_program.get_info(cl.program_info.KERNEL_NAMES)
print(f"Kernel Names: {program_kernel_names}")

# %% [markdown]
# ## Mine Nonce

# %%
# set up the variables to generate the random numbers
plaintext = 'this is a description of the latest block'
plaintext_bytes = np.frombuffer(plaintext.encode('utf-8'), dtype=np.uint8)
plaintext_length = np.int32(len(plaintext_bytes))

seed = np.random.randint(0, np.iinfo(np.uint32).max, dtype=np.uint32)
window_size = np.uint32(1000000)
nonce = np.zeros(shape=16 * 64, dtype=np.uint8)
nonce_len = np.zeros(shape=64, dtype=np.uint8)

# allocate the memory for the variables on the device
cl_window_size = cl.Buffer(cl_ctx, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=window_size)
cl_plaintext_bytes = cl.Buffer(cl_ctx, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=plaintext_bytes)
cl_plaintext_length = cl.Buffer(cl_ctx, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=plaintext_length)
cl_nonce = cl.Buffer(cl_ctx, cl.mem_flags.WRITE_ONLY, nonce.nbytes)
cl_nonce_len = cl.Buffer(cl_ctx, cl.mem_flags.WRITE_ONLY, nonce_len.nbytes)

zeros_found = {}

keep_running = True
while (keep_running):
    seed = np.random.randint(0, np.iinfo(np.uint32).max, dtype=np.uint32)
    cl_seed = cl.Buffer(cl_ctx, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=seed)

    # execute the program
    cl_program.mine_nonce(
        cl_queue, (1,), None,
        cl_seed,
        cl_window_size,
        cl_plaintext_bytes,
        cl_plaintext_length,
        cl_nonce,
        cl_nonce_len)

    # get the results
    cl.enqueue_copy(cl_queue, nonce, cl_nonce)
    cl.enqueue_copy(cl_queue, nonce_len, cl_nonce_len)

    # interpret the results
    for i in range(0, 64):
        if nonce_len[i] > 0:
            if (i not in zeros_found):
                nonce_str = nonce[i * 16:i * 16 + nonce_len[i]].tobytes().decode('UTF-8')
                zeros_found[i] = nonce_str
                hash = hashlib.sha256((plaintext + nonce_str).encode('utf-8'))

                print("%4d: [%2d] %16s %64s" % (i, nonce_len[i], nonce_str, hash.hexdigest() if nonce_len[i] > 0 else ''))

    keep_running = True


