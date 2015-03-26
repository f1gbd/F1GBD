avrdude -p m328p -c arduino -P COM51 -b 115200 -U flash:w:%1
pause
