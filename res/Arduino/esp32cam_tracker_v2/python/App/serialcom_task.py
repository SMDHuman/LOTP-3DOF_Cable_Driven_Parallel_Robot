from typing import Callable
from serial.tools import list_ports
from  threading import Thread
from serial import Serial
import time

class SerialCOM:
	def __init__(self):
		self.serial = Serial()
		self.active = True
		self.request_close = False
		self.apply_close = False
		Thread(target=self.rx_loop).start()
		self.rx_buffer = b""
		self.disconnected_cb = lambda : 0

	def set_disconnect_callback(self, callback: Callable):
		self.disconnected_cb = callback

	def get_ports(self):
		return([com.name for com in list_ports.comports()])

	def set_port(self, name: str):
		self.close()
		self.serial.port = name

	def set_baudrate(self, baudrate: int):
		self.close()
		self.serial.baudrate = baudrate

	def is_open(self):
		return(self.serial.is_open)

	def close(self):
		self.request_close = True
		while(not self.apply_close): pass
		if(self.serial.is_open):
			self.serial.close()
		self.request_close = False
		self.rx_buffer = b""

	def open(self):
		self.rx_buffer = b""
		self.serial.open()

	def write(self, data) -> bool:
		if(self.serial.is_open):
			if(type(data) == list):
				data = bytearray(data)
			elif(type(data) == int):
				data = bytearray([data])
			self.serial.write(data)
			return(True)
		return(False)

	def rx_loop(self):
		while(self.active):
			#...
			if(self.request_close):
				self.apply_close = True
				while(self.request_close): pass
				self.apply_close = False
			#...
			if(self.serial.is_open):
				try:
					if(self.serial.in_waiting):
						self.rx_buffer += self.serial.read()
						print(self.rx_buffer)
				except:
					self.rx_buffer = b""
					self.disconnected_cb()
					self.serial.close()
			time.sleep(0.001)