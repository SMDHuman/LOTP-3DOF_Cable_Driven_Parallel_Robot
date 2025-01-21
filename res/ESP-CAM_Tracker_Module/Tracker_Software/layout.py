import tkinter as tk
import tkinter.ttk as ttk

class Layout(tk.Tk):
    def __init__(self):
        super().__init__("ESP Tracker Software")
        self.geometry("800x600")
        for r in range(3):
            self.rowconfigure(r, weight=1)
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        #...
        configs_frame = tk.Frame(self)
        configs_frame.pack(side="left", fill="y")
        #----------------------------------------------------------------------
        # ____ Serial Config Frame ____
        serial_config_fr = tk.LabelFrame(configs_frame, 
                                         text="Serial Config", 
                                         width=200)
        serial_config_fr.pack(side = "top", fill="x")
        serial_config_fr.columnconfigure(0, weight=1)
        serial_config_fr.columnconfigure(1, weight=1)
        #...
        tk.Label(serial_config_fr, text="Port:").grid(row=0, column=0)
        self.serial_port_select = ttk.Combobox(serial_config_fr, 
                                               state="readonly", 
                                               width=8)
        self.serial_port_select.set("None")
        self.serial_port_select.grid(row=0, column=1)
        #...
        tk.Label(serial_config_fr, text="Baudrate:").grid(row=1, column=0)
        bauds = ["4800", "9600", "19200", "38400", "57600", 
                 "115200", "230400", "460800", "921600"]
        self.serial_baudrate_select = ttk.Combobox(serial_config_fr,
                                                   values=bauds, 
                                                   width=8)
        self.serial_baudrate_select.set("115200")
        self.serial_baudrate_select.grid(row=1, column=1)
        #...
        self.serial_connect_button = tk.Button(serial_config_fr, 
                                               text="Connect", 
                                               state="disabled")
        self.serial_connect_button.grid(row=2, column=0, sticky = "e")
        self.serial_disconnect_button = tk.Button(serial_config_fr, 
                                                  text="Disconnect", 
                                                  state="disabled")
        self.serial_disconnect_button.grid(row=2, column=1, sticky="w")
        #----------------------------------------------------------------------
        # ____ Camera Config Frame ____
        camera_config_fr = tk.LabelFrame(configs_frame, 
                                         text="Camera Config", 
                                         width=200)

        self.camera_raw_button=tk.Button(camera_config_fr, 
                                         text = "Get Raw Frame")
        self.camera_raw_button.pack()
        camera_config_fr.pack(side = "top", fill="x")
        #----------------------------------------------------------------------
        # ____ Tracker Config Frame ____
        tracker_config_fr = tk.LabelFrame(configs_frame, 
                                          text="Tracker Config", 
                                          width=200)
        tracker_config_fr.pack(side = "top", fill="x")
        #...
        self.tracker_framecount_button=tk.Button(tracker_config_fr, 
                                                 text = "Request Frame Count")
        self.tracker_rects_button=tk.Button(tracker_config_fr, 
                                         text = "Get Rectangles")
        self.tracker_rects_button.pack()
        self.tracker_framecount_button.pack()
        #----------------------------------------------------------------------
        # ____ Graphics Frame ____
        graphics_fr = tk.LabelFrame(self, text="Graphics")
        graphics_fr.pack(side = "left", expand=1, fill="both")

        self.frame_canvas = tk.Canvas(graphics_fr, 
                                      width=240, height=240)
        self.frame_canvas.grid(row=0, column=0)