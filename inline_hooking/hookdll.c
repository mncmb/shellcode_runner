#include <windows.h>

void __stdcall myOutputDebugStringA(LPCSTR lpOutputString) {
    printf(lpOutputString);
}

void run(void) {
    void * HookOutputDebugStringA = &myOutputDebugStringA;
    DWORD oldprotect = 0;
    void * funcAdress;
    
    // get Address of OutputDebugStringA function
    funcAdress = (void*)GetProcAddress(GetModuleHandle(TEXT("kernel32.dll")), "OutputDebugStringA");
    
    // change permissions on memory page, where OutputDebugString is mapped into the current process
    VirtualProtect(funcAdress, 100, PAGE_EXECUTE_READWRITE, &oldprotect);

    // prepare a buffer with the patch and copy contents of patch to start address of OutputDebugStringA
    char patch[12] = {0};
    memcpy_s(patch, 1, "\x48", 1); // mov
    memcpy_s(patch+1, 1, "\xb8", 1); // rax,
    memcpy_s(patch+2, 8, &HookOutputDebugStringA, 8); // 64bit value
    memcpy_s(patch+10, 1, "\x50", 1); // push rax
    memcpy_s(patch+11, 1, "\xc3",1); // ret
    memcpy(funcAdress, patch, sizeof(patch));
}

BOOL WINAPI DllMain( HINSTANCE hinstDLL, DWORD fdwReason, LPVOID lpReserved ) {
	switch ( fdwReason ) {
			case DLL_PROCESS_ATTACH:
			        // patch memory address of OutputDebugStringA as soon as this dll gets attached to the process
					run();
					break;
			case DLL_THREAD_ATTACH:
					break;
			case DLL_THREAD_DETACH:
					break;
			case DLL_PROCESS_DETACH:
					break;
			}
	return TRUE;
}
