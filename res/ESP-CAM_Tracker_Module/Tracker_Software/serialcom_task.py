from typing import Callable
from serial.tools import list_ports
from threading import Thread
from serial import Serial
import struct
from slip import SLIP
import time

class SerialCOM:
	#--------------------------------------------------------------------------
	#...
	def __init__(self):
		self.serial = Serial()
		self.active = True
		self.request_close = False
		self.apply_close = False
		self.slip = SLIP()
		self.disconnected_cb = lambda: 0
		self.receive_cb = lambda p: 0
		Thread(target=self.rx_loop).start()
	#--------------------------------------------------------------------------
	#...
	def set_disconnect_callback(self, callback: Callable):
		self.disconnected_cb = callback
	#--------------------------------------------------------------------------
	#...
	def set_receive_callback(self, callback: Callable):
		self.receive_cb = callback
	#--------------------------------------------------------------------------
	#...
	def get_ports(self):
		return([com.name for com in list_ports.comports()])
	#--------------------------------------------------------------------------
	#...
	def set_port(self, name: str):
		self.close()
		self.serial.port = name
	#--------------------------------------------------------------------------
	#...
	def set_baudrate(self, baudrate: int):
		self.close()
		self.serial.baudrate = baudrate
	#--------------------------------------------------------------------------
	#...
	def is_open(self):
		return(self.serial.is_open)
	#--------------------------------------------------------------------------
	#...
	def close(self):
		self.request_close = True
		while(not self.apply_close): pass
		if(self.serial.is_open):
			self.serial.close()
		self.request_close = False
	#--------------------------------------------------------------------------
	#...
	def open(self):
		self.serial.open()
	#--------------------------------------------------------------------------
	#...
	def send_slip(self, package: bytearray) -> None:
		#print("package:", package)
		checksum = 0
		for data in package:
			checksum += data
			if(data == self.slip.END):
				self.write(self.slip.ESC)
				self.write(self.slip.ESC_END)
			elif(data == self.slip.ESC):
				self.write(self.slip.ESC)
				self.write(self.slip.ESC_ESC)
			else:
				self.write(data)
		# War Crime 
		for data in struct.pack("I", checksum):
			if(data == self.slip.END):
				self.write(self.slip.ESC)
				self.write(self.slip.ESC_END)
			elif(data == self.slip.ESC):
				self.write(self.slip.ESC)
				self.write(self.slip.ESC_ESC)
			else:
				self.write(data)
		self.write(self.slip.END)

	#--------------------------------------------------------------------------
	#...
	def write(self, data) -> bool:
		#print("write:", data)
		if(self.serial.is_open):
			if(type(data) == list):
				data = bytearray(data)
			elif(type(data) == int):
				data = bytearray([data])
			self.serial.write(data)
			return(True)
		return(False)
	#--------------------------------------------------------------------------
	#...
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
					while(self.serial.in_waiting > 0):
						value = ord(self.serial.read(1))
						#print(chr(value), end = "")
						self.slip.push(value)
				except:
					self.disconnected_cb()
					self.serial.close()
			#...
			if(self.slip.wait_ack):
				self.serial.write(bytearray([1]))
				self.slip.wait_ack = False
			#...
			if(self.slip.ready):
				pack = self.slip.get()
				if(self.check_checksum(pack)):
					self.receive_cb(pack[:-4])
			time.sleep(0.00001)	
	#--------------------------------------------------------------------------
	#...
	def check_checksum(self, package: bytearray):
		checksum = struct.unpack("I", package[-4:])[0]
		return(sum(package[:-4])%(2**64) == checksum)

