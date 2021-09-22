#include <windows.h>
#include <stdio.h>

void main(){
    char supersecret[100] = "This is my super secret supersecret.\0";
    printf("press enter for first call to OutputDebugStringA...");
    getchar();
    
    OutputDebugStringA(supersecret);
    
    printf("Inject dll now and press enter for second call to OutputDebugStringA ....");
    getchar();
    
    OutputDebugStringA(supersecret);
}
