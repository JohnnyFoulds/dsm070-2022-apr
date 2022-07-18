"""
This module implements the Zimcoin miner functionality.
"""

import pyopencl as cl


class ZimcoinMiner:
    """
    Mine for Zimcoins using OpenCL.
    """
    def __init__(self, platform_id : int, device_id : int):
        """
        Initialize the miner.
        """
        # set the opencl platform and device
        self.platform_id = platform_id
        self.device_id = device_id

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
