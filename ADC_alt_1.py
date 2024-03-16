'''
#!/usr/bin/env python3
import board
import busio
i2c = busio.I2C(board.SCL, board.SDA)
'''
import sys
print("Interpreter : ", sys.executable)
print("Library Path: ", sys.path)