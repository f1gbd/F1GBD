avrdude -p m2560 -c stk500v2 -P \\.\COM29 -b 115200 -U flash:w:DFT406.hex
pause