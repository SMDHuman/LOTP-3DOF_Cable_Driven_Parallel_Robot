import tkinter as tk
import tkinter.ttk as ttk
from serialcom_task import SerialCOM
from layout import Layout
from PIL import ImageTk, Image
import struct
from random import randint
#------------------------------------------------------------------------------
class App(Layout):
    def __init__(self) -> None:
        super().__init__()
        #...
        self.camera_size = (0, 0)
        self.tracker_size = (0, 0)
        self.rand_colors = [(randint(0, 255), randint(0, 255), randint(0, 255)) for i in range(255)]
        #...
        self.sercom = SerialCOM()
        self.sercom.set_disconnect_callback(self.update_com_list)
        self.sercom.set_receive_callback(self.package_received)
        #...
        self.serial_port_select.bind("<<ComboboxSelected>>", self.serial_port_select_event)
        self.serial_port_select.bind("<Button-1>", self.update_com_list)
        #...
        self.request_raw_button.configure(command = lambda: self.sercom.write(bytearray([0x0B, 0x0A])))
        self.request_rects_button.configure(command = lambda: self.sercom.write(0x0F))
        self.request_filtered_button.configure(command = lambda: self.sercom.write(bytearray([0x13, 1])))
        self.request_eroded_button.configure(command = lambda: self.sercom.write(bytearray([0x13, 2])))
        self.request_dilated_button.configure(command = lambda: self.sercom.write(bytearray([0x13, 3])))  
        self.request_flooded_button.configure(command = lambda: self.sercom.write(bytearray([0x13, 4])))
        #...
        self.serial_connect_button.configure(command=self.serial_connect_event)
        self.serial_disconnect_button.configure(command=self.serial_disconnect_event)
        self.serial_baudrate_select.bind("<<ComboboxSelected>>", self.serial_baudrate_select_event)
        #...
        self.protocol("WM_DELETE_WINDOW", self.on_app_close)
        #...
        self.update_com_list()
        #...
        self.last_framecount = 0
        self.after(1000, self.request_framecount)

        self._imgs = {}
    #--------------------------------------------------------------------------
    # Request frame count every second
    def request_framecount(self):
        self.sercom.write(0x10)
        self.after(1000, self.request_framecount)
    #--------------------------------------------------------------------------
    #...
    def package_received(self, package):
        #print("Package Type:", package[0])
        # Frames
        if(package[0] == 0x00):
            f_id = package[1]
            w, h = struct.unpack("II", package[2:2+4*2])
            frame = Image.frombytes("L", (w, h), package[2+4*2:])
            # If flooded frame received, color it
            if(f_id == 4):
                colored_frame = Image.new("RGB", (w, h))
                for y in range(h):
                    for x in range(w):
                        index = int(frame.getpixel((x, y)))
                        if(index > 0):
                            colored_frame.putpixel((x, y), self.rand_colors[index])
                frame = colored_frame
            #...
            self._imgs[self.selected_frame_canvas] = ImageTk.PhotoImage(frame)
            cw = self.selected_frame_canvas.winfo_width()
            ch = self.selected_frame_canvas.winfo_height()
            self.selected_frame_canvas.create_image(cw/2, ch/2, 
                                                    image = self._imgs[self.selected_frame_canvas], 
                                                    anchor="center")
        # Rectangles
        elif(package[0] == 0x01):
            size = int((len(package)-1)/4)
            rects = struct.unpack("I"*size, package[1:])
            rects = [rects[i:i+4] for i in range(0, size, 4)]
            cw = self.selected_frame_canvas.winfo_width()
            ch = self.selected_frame_canvas.winfo_height()
            offset = [(cw-self.tracker_size[0])/2, (ch-self.tracker_size[1])/2]
            self.selected_frame_canvas.delete("rects")
            for rect in rects[:-1]:
                rect = [rect[i] + offset[i%2] for i in range(4)]
                self.selected_frame_canvas.create_rectangle(*rect, 
                                                   tags=("rects", ),
                                                   width = 3,
                                                   outline = "red")
        # Frame Count
        elif(package[0] == 0x02):
            count = struct.unpack("I", package[1:])[0]
            self.tracker_framecount_label.configure(text=f"FPS: {count-self.last_framecount}")
            self.last_framecount = count
        # Tracker Frame Size
        elif(package[0] == 0x03 and len(package) == 2+1):
            size = struct.unpack("BB", package[1:])
            self.tracker_framesize_label.configure(text=f"Frame Size: {size[0]}x{size[1]}")
            self.tracker_size = size[:2]
        # Tracker Frame Size
        elif(package[0] == 0x04 and len(package) == 4*2+1):
            size = struct.unpack("II", package[1:])
            self.camera_framesize_label.configure(text=f"Frame Size: {size[0]}x{size[1]}")
            self.camera_size = size[:2]
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
        self.sercom.write(0x11)
        self.sercom.write(0x12)
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

