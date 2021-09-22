@ECHO OFF

cl.exe /O2 /D_USRDLL /D_WINDLL hookdll.c /MT /link /DLL /OUT:Hook.dll
cl.exe /O2 injector.cpp /MT /link /OUT:injector.exe
cl.exe /O2 testexe.c /MT /link /OUT:test.exe
del *.obj