import tkinter as tk
import tkinter.ttk as ttk
from serialcom_task import SerialCOM
from layout import Layout
from PIL import ImageTk, Image
import struct
#------------------------------------------------------------------------------
class App(Layout):
    def __init__(self) -> None:
        super().__init__()
        #...
        self.sercom = SerialCOM()
        self.sercom.set_disconnect_callback(self.update_com_list)
        self.sercom.set_receive_callback(self.package_received)
        #...
        self.serial_port_select.bind("<<ComboboxSelected>>", self.serial_port_select_event)
        self.serial_port_select.bind("<Button-1>", self.update_com_list)
        #...
        f = lambda: self.sercom.write(0x10)
        self.tracker_framecount_button.configure(command = f)
        f = lambda: self.sercom.write(bytearray([0x0B, 0x0A]))
        self.camera_raw_button.configure(command = f)
        f = lambda: self.sercom.write(0x0F)
        self.tracker_rects_button.configure(command = f)
        #...
        self.serial_connect_button.configure(command=self.serial_connect_event)
        self.serial_disconnect_button.configure(command=self.serial_disconnect_event)
        self.serial_baudrate_select.bind("<<ComboboxSelected>>", self.serial_baudrate_select_event)
        #...
        self.protocol("WM_DELETE_WINDOW", self.on_app_close)
        #...
        self.update_com_list()
    #--------------------------------------------------------------------------
    #...
    def package_received(self, package):
        print("Package Type:", package[0])
        # Frames
        if(package[0] == 0x00):
            w, h = struct.unpack("II", package[1:1+4*2])
            frame = Image.frombytes("L", (w, h), package[3:])
            self._img = ImageTk.PhotoImage(frame)   
            self.frame_canvas.configure(width = w, height = h)
            self.frame_canvas.create_image(0, 0, image = self._img, anchor="nw")
        # Rectangles
        elif(package[0] == 0x01):
            size = int((len(package)-1)/4)
            rects = struct.unpack("I"*size, package[1:])
            rects = [rects[i:i+4] for i in range(0, size, 4)]
            self.frame_canvas.delete("rects")
            for rect in rects[:-1]:
                self.frame_canvas.create_rectangle(*rect, 
                                                   tags=("rects", ),
                                                   width = 3,
                                                   outline = "red")
        # Unsigned Integers
        elif(package[0] == 0x02):
            lenght = int((len(package)-1)/4)
            uints = struct.unpack("I"*lenght, package[1:])
            print(uints[:lenght])
        # Unknown Type
        else:
            print(package[1:])
    #--------------------------------------------------------------------------
    #...
    def update_com_list(self, event = None):
        coms = self.sercom.get_ports()
        self.serial_port_select.configure(values = coms)
        if(len(coms) == 0):
            self.serial_connect_button.configure(state="disabled")
            self.serial_disconnect_button.configure(state="disabled")
            self.serial_port_select.set("None")
        elif(self.serial_port_select.get() == "None"):
            self.serial_port_select.set(coms[0])
            self.serial_port_select_event()
    #--------------------------------------------------------------------------
    #...
    def serial_port_select_event(self, event = None):
        if(self.sercom.is_open()):
            self.sercom.close()
        self.serial_connect_button.configure(state="normal")
        self.serial_disconnect_button.configure(state="disabled")
    #--------------------------------------------------------------------------
    #...
    def serial_baudrate_select_event(self, event = None):
        if(self.sercom.is_open()):
            self.sercom.close()
        self.serial_connect_button.configure(state="normal")
        self.serial_disconnect_button.configure(state="disabled")
    #--------------------------------------------------------------------------
    #...
    def serial_connect_event(self):
        self.sercom.set_port(self.serial_port_select.get()) 
        self.sercom.set_baudrate(int(self.serial_baudrate_select.get()))
        self.sercom.open()
        self.serial_connect_button.configure(state="disabled")
        self.serial_disconnect_button.configure(state="normal")
    #--------------------------------------------------------------------------
    #...
    def serial_disconnect_event(self):
        self.sercom.close()
        self.serial_connect_button.configure(state="normal")
        self.serial_disconnect_button.configure(state="disabled")
    #--------------------------------------------------------------------------
    def serial_rx_task(self):
        while(self.state == "normal"):
            if(self.sercom.is_open):
                if(self.sercom.in_waiting):
                    package = self.sercom.read()
                    print(package)

    def on_app_close(self):
        self.sercom.active = False
        self.destroy()

#------------------------------------------------------------------------------
if(__name__ == "__main__"):
    app = App()
    app.mainloop()

