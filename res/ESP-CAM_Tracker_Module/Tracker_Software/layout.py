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
        self.serial_baudrate_select.set("921600")
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
        # ____ Module Config Frame ____
        module_config_fr = tk.LabelFrame(configs_frame, 
                                         text="Module Config", 
                                         width=200)
        #...
        frame = tk.Frame(module_config_fr)
        tk.Label(frame, text = "Led Delay : ").pack(side = "left")
        self.led_delay_entry=tk.Spinbox(frame, from_ = 0, to = 2000, increment=50, width=5)
        self.led_delay_entry.pack()
        frame.pack()
        #...
        self.send_config_button=tk.Button(module_config_fr, 
                                         text = "Set Config")
        self.send_config_button.pack()
        module_config_fr.pack(side = "top", fill="x")
        #----------------------------------------------------------------------
        # ____ Camera Config Frame ____
        camera_config_fr = tk.LabelFrame(configs_frame, 
                                         text="Camera Config", 
                                         width=200)
        self.camera_framesize_label=tk.Label(camera_config_fr, 
                                              text = "Camera Size : -x-")
        self.camera_framesize_label.pack()
        camera_config_fr.pack(side = "top", fill="x")
        #----------------------------------------------------------------------
        # ____ Tracker Config Frame ____
        tracker_config_fr = tk.LabelFrame(configs_frame, 
                                          text="Tracker Config", 
                                          width=200)
        tracker_config_fr.pack(side = "top", fill="x")
        #...
        self.tracker_framecount_label=tk.Label(tracker_config_fr, 
                                                 text = "FPS: 0")
        self.tracker_framesize_label=tk.Label(tracker_config_fr, 
                                              text = "Frame Size : -x-")
        self.tracker_framecount_label.pack()
        self.tracker_framesize_label.pack()
        #----------------------------------------------------------------------
        # ____ Frame Request Frame ____
        frame_request_fr = tk.LabelFrame(configs_frame, 
                                          text="Frame Request", 
                                          width=200)
        frame_request_fr.pack(side = "top", fill="x")
        #...
        self.request_raw_button=tk.Button(frame_request_fr, 
                                         text = "Get Raw Frame")
        self.request_filtered_button=tk.Button(frame_request_fr, 
                                         text = "Get Filtered")
        self.request_dilated_button=tk.Button(frame_request_fr, 
                                         text = "Get Dilated")
        self.request_eroded_button=tk.Button(frame_request_fr, 
                                         text = "Get Eroded")
        self.request_flooded_button=tk.Button(frame_request_fr, 
                                         text = "Get Flooded")
        self.request_rects_button=tk.Button(frame_request_fr, 
                                         text = "Get Rectangles")
        self.request_raw_button.pack()
        self.request_filtered_button.pack()
        self.request_eroded_button.pack()
        self.request_dilated_button.pack()
        self.request_flooded_button.pack()
        self.request_rects_button.pack()
        #----------------------------------------------------------------------
        # ____ Graphics Frame ____
        graphics_fr = tk.LabelFrame(self, text="Graphics")
        graphics_fr.pack(side = "left", expand=1, fill="both")
        for i in range(2):
          graphics_fr.rowconfigure(i, weight=1)
          graphics_fr.columnconfigure(i, weight=1)

        config_c = {"width": 240, "height": 176, "bg":"orange"}
        config_g = {"sticky": "wens"}
        self.frame_canvas_A = tk.Canvas(graphics_fr, config_c)
        self.frame_canvas_A.grid(config_g, row=0, column=0)
        self.frame_canvas_B = tk.Canvas(graphics_fr, config_c)
        self.frame_canvas_B.grid(config_g, row=0, column=1)
        self.frame_canvas_C = tk.Canvas(graphics_fr, config_c)
        self.frame_canvas_C.grid(config_g, row=1, column=0)
        self.frame_canvas_D = tk.Canvas(graphics_fr, config_c)
        self.frame_canvas_D.grid(config_g, row=1, column=1)
        
        self.selected_frame_canvas = self.frame_canvas_A

        def f(e: tk.Event):
            self.selected_frame_canvas.delete("select_rect") 
            self.selected_frame_canvas = e.widget
            cw = self.selected_frame_canvas.winfo_width()
            ch = self.selected_frame_canvas.winfo_height()
            self.selected_frame_canvas.create_rectangle(0, 0, cw, ch, width=10, outline="black", tags="select_rect") 
        self.frame_canvas_A.bind("<Button-1>", f)
        self.frame_canvas_B.bind("<Button-1>", f)
        self.frame_canvas_C.bind("<Button-1>", f)
        self.frame_canvas_D.bind("<Button-1>", f)

