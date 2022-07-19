"""
This module implements the Zimcoin miner functionality.
"""

import pyopencl as cl
import numpy as np
from blocks import Block


class ZimcoinMiner:
    """
    Mine for Zimcoins using OpenCL.
    """
    def __init__(self,
                 platform_id : int, device_id : int,
                 window_size : int = 1e6):
        """
        Initialize the miner.
        """
        # set the opencl platform and device
        self.platform_id = platform_id
        self.device_id = device_id
        self.window_size = window_size

        # set the opencl source files
        self.program_files = [
            'Library/worker/sha256.cl',
            'Library/worker/zimcoin.cl',
        ]

        # initialize the opencl context
        self.cl_devices = cl.get_platforms()[self.platform_id].get_devices()
        self.cl_context = cl.Context(self.cl_devices)
        self.cl_queue = cl.CommandQueue(self.cl_context, self.cl_devices[self.device_id])
        self.cl_device = self.cl_devices[self.device_id ]

        # configure the number of threads to use
        self.cl_threads = self.cl_device.max_compute_units \
                        * self.cl_device.max_work_group_size

        if self.cl_device .type & 4 == 0:
            self.cl_threads = self.cl_device.max_work_group_size

        # build the opencl program
        self.cl_program = self.build_program()

    @property
    def thread_count(self) -> int:
        """
        Get the number of OpenCL threads that will be used.
        """
        return self.cl_threads

    def build_program(self, build_options=None) -> cl.Program:
        """
        Build a program from an OpenCL source file.

        Parameters
        ----------
        build_options : list of str
            The build options to use.

        Returns
        -------
        pyopencl.Program
        """
        program_source = ''
        for cl_file in self.program_files:
            with open(cl_file, 'r', encoding='utf8') as cl_file:
                file_source = cl_file.read()
                program_source += '\n' + file_source

        program_source = cl.Program(self.cl_context, program_source)


        if build_options is None:
            build_options = []

        self.cl_program = program_source.build(options=build_options)

        return self.cl_program

    def mine(self, previous : bytes, height : int, miner : bytes,
             transactions : list, timestamp : int, difficulty : int):
        """
        Mine for Zimcoins.
        """
        # create the block from the input data
        input_block = Block(
            previous=previous,
            height=height,
            miner=miner,
            transactions=transactions,
            timestamp=timestamp,
            difficulty=difficulty,
            block_id=None,
            nonce=None)

        # set up the variables for finding the nonce
        block_data = np.frombuffer(input_block.to_bytes(), dtype=np.uint32)
        block_data_len = np.int32(block_data.size) * 4

        seed = np.ulonglong(0)
        
        target = np.frombuffer(
            input_block.calculate_target() \
                .to_bytes(32, byteorder='big', signed=False),
            np.uint32)

        nonce = np.zeros(shape=1, dtype=np.ulonglong)

        # allocate the memory for the variables on the device
        cl_window_size = cl.Buffer(self.cl_context, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=np.uint32(self.window_size))
        cl_block_data = cl.Buffer(self.cl_context, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=block_data)
        cl_block_data_len = cl.Buffer(self.cl_context, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=block_data_len)
        cl_nonce = cl.Buffer(self.cl_context, cl.mem_flags.WRITE_ONLY, nonce.nbytes)
        cl_target = cl.Buffer(self.cl_context, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=target)

        # search for a valid nonce
        while nonce[0] == 0:
            cl_seed = cl.Buffer(self.cl_context, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=seed)

            # execute the kernel
            self.cl_program.mine_sequential(
                self.cl_queue, (self.thread_count,), None,
                cl_seed,
                cl_window_size,
                cl_block_data,
                cl_block_data_len,
                cl_nonce,
                cl_target,
                None)

            # get the results
            cl.enqueue_copy(self.cl_queue, nonce, cl_nonce)

            seed = np.ulonglong(seed + self.thread_count * self.window_size)

        # return the nonce
        return int.from_bytes(nonce[0].tobytes(), byteorder='little')
