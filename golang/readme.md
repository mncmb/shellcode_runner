## Shellcode Execution with GoLang
A rip off of [blackhillsinfosec.com/webcast-shellcode-execution-with-golang](https://www.blackhillsinfosec.com/webcast-shellcode-execution-with-golang/) and some anotations regarding payload creation and env setup in this doc.

## generate shellcode
`c#` formatted shellcode can be used with minimal adjustments in go
```
msfvenom -p windows/x64/exec CMD=calc.exe -f csharp
```

Create xored payload with `msfvenom`, other algorithms can be used. See list of algorithms supported by `msfvenom` with `msfvenom --list encrypt` 
```
msfvenom -p windows/x64/exec CMD=calc.exe -f csharp --encrypt xor --encrypt-key "\x31"
```

## DLL creation
- include an Exported function (start function name with capital letter) and a comment above it that includes the export keyword and the function name
```go
import "C"

//export Engage
func Engage() {
	testDLLExportedFunction()
}
```

## regsvr32 dll
A Dll created for use with regsvr32 needs to implement specific methods. This can be done through defining the following 4 exports:
- EntryPoint()
- DllRegisterServer()
- DllUnregisterServer()
- DllInstall()
	
All four need to return boolean (True for success). The payload call can be put in either of the four.

## compile
### compile on windows
This needs golang obviously but also mingw for DLL creation.

Easiest way of setting everything up is by isntalling it through `chocolatey`. This also adds necessary environment variables.

Run 
```
choco install -y vscode golang mingw
```

Building the Dll can then be done with
```
go build -buildmode=c-shared -o go.dll main.go
```

### cross compile DLL 
Cross compilation on Linux is possible but needs some further setup. I have collected some pointers towards setup here, but this needs further refinement.

Based on this stackoverflow post (https://stackoverflow.com/questions/49078510/trouble-compiling-windows-dll-using-golang-1-10), the following is necessary:

Install `mingw` for cross compilation

```
sudo apt install gcc-mingw-w64-i686 gcc-mingw-w64-x86-64 
```
Compile for Windows on Ubuntu: 
```
env GOOS=windows GOARCH=386 CGO_ENABLED=1 CC=i686-w64-mingw32-gcc go build -buildmode=c-shared -o main.dll main.go 
```
or 
```
env GOOS=windows GOARCH=amd64 CGO_ENABLED=1 CC=x86_64-w64-mingw32-gcc go build -buildmode=c-shared -o main.dll main.go 
```


## TODO
check out calling shellcode by casting alloc mem to function pointer (https://stackoverflow.com/questions/3601796/can-we-have-function-pointers-in-go)


## links 
https://github.com/yoda66/GoShellcode


A
A

