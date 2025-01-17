import tkinter as tk
import tkinter.ttk as ttk
from serialcom_task import SerialCOM
#------------------------------------------------------------------------------
class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__("ESP Tracker Software")
        self.geometry("800x600")
        for r in range(3):
            self.rowconfigure(r, weight=1)
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)

        configs_frame = tk.Frame(self)
        configs_frame.pack(side="left", fill="y")
        self.sercom = SerialCOM()
        self.sercom.set_disconnect_callback(self.update_com_list)
        
        # ____ Serial Config Frame ____
        serial_config_fr = tk.LabelFrame(configs_frame, text="Serial Config", width=200)
        serial_config_fr.pack(side = "top", fill="x")
        serial_config_fr.columnconfigure(0, weight=1)
        serial_config_fr.columnconfigure(1, weight=1)
        #...
        tk.Label(serial_config_fr, text="Port:").grid(row=0, column=0)
        self.serial_port_select = ttk.Combobox(serial_config_fr, state="readonly", width=8)
        self.serial_port_select.bind("<<ComboboxSelected>>", self.serial_port_select_event)
        self.serial_port_select.bind("<Button-1>", self.update_com_list)
        self.serial_port_select.set("None")
        self.serial_port_select.grid(row=0, column=1)
        #...
        tk.Label(serial_config_fr, text="Baudrate:").grid(row=1, column=0)
        bauds = ["4800", "9600", "19200", "38400", "57600", "115200", "230400", "460800", "921600"]
        self.serial_baudrate_select = ttk.Combobox(serial_config_fr,values=bauds, width=8)
        self.serial_baudrate_select.bind("<<ComboboxSelected>>", self.serial_baudrate_select_event)
        self.serial_baudrate_select.set("115200")
        self.serial_baudrate_select.grid(row=1, column=1)
        #...
        self.serial_connect_button = tk.Button(serial_config_fr, text="Connect", 
                                                state="disabled", command=self.serial_connect_event)
        self.serial_connect_button.grid(row=2, column=0, sticky = "e")
        self.serial_disconnect_button = tk.Button(serial_config_fr, text="Disconnect", 
                                                  state="disabled", command=self.serial_disconnect_event)
        self.serial_disconnect_button.grid(row=2, column=1, sticky="w")
        # ____ Camera Config Frame ____
        camera_config_fr = tk.LabelFrame(configs_frame, text="Camera Config", width=200)
        camera_config_fr.pack(side = "top", fill="x")
        tk.Label(camera_config_fr, text="Port:").grid(row=0, column=0)
        # ____ Tracker Config Frame ____
        tracker_config_fr = tk.LabelFrame(configs_frame, text="Tracker Config", width=200)
        tracker_config_fr.pack(side = "top", fill="x")
        tracker_framecount_button = tk.Button(tracker_config_fr, text = "Request Frame Count")
        f = lambda event: self.sercom.write(0x10)
        tracker_framecount_button.bind("<Button-1>", f)
        tracker_framecount_button.pack()
        # ____ Graphics Frame ____
        graphics_fr = tk.LabelFrame(self, text="Graphics")
        graphics_fr.pack(side = "left", expand=1, fill="both")

        self.protocol("WM_DELETE_WINDOW", self.app_close)

        #...
        self.update_com_list()
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

    def app_close(self):
        self.sercom.active = False
        self.destroy()

#------------------------------------------------------------------------------
if(__name__ == "__main__"):
    app = App()
    app.mainloop()

