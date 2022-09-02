"""
This is a serial monitor gui that is intended to replace the standard
Arduino one and allow for easy graphing and other Python-based data
processing.
"""

############################################
#
# Next Steps:
#
# ----------------
#

#############################################

#iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii
#
# Issues:
#
#
# Resovled:
#  
#iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii

import tkinter
import tkinter as tk
from tkinter import ttk

#from matplotlib.backends.backend_tkagg import (
#    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)

import numpy as np

from tkinter import ttk
from tkinter.messagebox import showinfo


# stuff to fix before pusing to pypi:
# - txt_mixin and rwkos are in krauss_misc
# - this is a different tkinter_utils from pybd_gui
#     - could I put this tkinter_utils in krauss_misc?
#     - do I merge the tkinter_utils versions into one file in krauss_misc?
# - serial_utils is a dependency
#     - so is pyserial

from krauss_misc import tkinter_utils, rwkos, txt_mixin

import os, glob, time, re
import serial, serial_utils

pad_options = {'padx': 5, 'pady': 5}



class tkinter_serial_gui(tk.Tk, tkinter_utils.abstract_window):
    def __init__(self):
        super().__init__()
        self.option_add('*tearOff', False)
        #self.geometry("900x600")
        self.mylabel = 'Tkinter Python Serial GUI'
        self.title(self.mylabel)
        self.resizable(1, 1)

        self.portname = None
        self.open = False
        self.delim = ","
        # configure the grid
        self.columnconfigure(0, weight=4)
        self.columnconfigure(1, weight=1)
        #self.rowconfigure(4, weight=2)
        self.rowconfigure(3, weight=4)        

        self.options = {'padx': 5, 'pady': 5}

        self.menubar = tk.Menu(self)
        self['menu'] = self.menubar
        self.menu_file = tk.Menu(self.menubar)
        self.menu_serial = tk.Menu(self.menubar)
        self.menu_plot = tk.Menu(self.menubar)        
        ## self.menu_codegen = tk.Menu(self.menubar)        
        self.menubar.add_cascade(menu=self.menu_file, label='File')
        self.menubar.add_cascade(menu=self.menu_serial, label='Serial')
        self.menubar.add_cascade(menu=self.menu_plot, label='Plot')        
        ## self.menubar.add_cascade(menu=self.menu_codegen, label='Code Generation')        
        ## self.menu_file.add_command(label='Save', command=self.on_save_menu)
        ## self.menu_file.add_command(label='Load', command=self.on_load_menu)        
        ## #menu_file.add_command(label='Open...', command=openFile)
        self.menu_file.add_command(label='Quit', command=self._quit)
        self.menu_serial.add_command(label='Read (force read)', command=self.read_serial)
        self.menu_serial.add_command(label='Transmit (write)', command=self.write_serial)
        self.menu_plot.add_command(label='dt Plot', command=self.plot_dt)
        self.menu_serial.add_command(label="Set Portname", \
                                         command=self.set_portname)
        self.menu_serial.add_command(label="Open Serial Port", \
                                         command=self.open_serial_port)
                                         ## self.menu_codegen.add_command(label='Set Arduino Template File', command=self.set_arduino_template)
        ## self.menu_codegen.add_command(label='Get Arduino Template File', command=self.get_arduino_template)
        ## self.menu_codegen.add_command(label='Set Arduino Output Path', \
        ##                               command=self.set_arduino_output_folder)
        ## self.menu_codegen.add_command(label='Generate Arduino Code', command=self.arduino_codegen)                

        self.bind("<Key>", self.key_pressed)
        self.bind('<Control-q>', self._quit)
        self.bind('<Command-q>', self._quit)
        self.bind('<Control-r>', self.read_serial)
        self.bind('<Control-t>', self.write_serial)                
        ## self.bind('<Control-s>', self.on_save_menu)
        ## self.bind('<Control-l>', self.on_load_menu)
        ## self.bind('<Control-a>', self.add_block)
        ## self.bind('<Control-P>', self.on_place_btn)
        ## self.bind('<Alt-p>', self.on_place_btn)
        ## self.bind('<Control-d>', self.on_draw_btn)
        
        # configure the root window
        self.make_widgets()


    def set_portname(self):
        portname = self.portname_var.get()
        if os.path.exists(portname):
            print("found: %s" % portname)
            print("portname set")
        else:
            print("portname not valid: %s" % portname)
            

    def find_serial_port(self):
        if rwkos.amiMac():
            pat = "/dev/tty.usb*"
        else:
            print("you are out of luck (for now)")
            return

        matches = glob.glob(pat)
        if len(matches) == 1:
            self.portname = matches[0]
            self.portname_var.set(self.portname)
        elif len(matches) == 0:
            print("did not find a match for %s" % pat)
        else:
            print("found more than one match for %s:\n %s" % (pat, matches))


    def open_serial_port(self):
        if self.portname:
            self.ser = serial_utils.serial_test(self.portname, baudrate=230400)
            self.ser.open()
            time.sleep(2)
            self.open = True
            print("serial port should be open")


    def close_serial_port(self):
        self.ser.close()
        self.open = False


    def read_serial(self, *args, **kwargs):
        if self.open:
            new_str = self.ser.read_all()
            #old_str = self.receive_text_var.get()
            #new_new_str = old_str + new_str
            #self.receive_text_var.set(new_new_str)
            self.receive_text.insert('end', new_str)
            print("new_str:")
            print(new_str)


    def write_serial(self, *args, **kwargs):
        self.notebook.select(0)
        mytext = self.send_text_var.get()
        if mytext:
            print("mytext: %s" % mytext)
            self.ser.write_string(mytext)
        time.sleep(0.5)
        # think about intelligent reading
        self.read_serial()
        time.sleep(0.1)
        self.read_serial()
        

    def startup(self):
        self.find_serial_port()
        self.open_serial_port()
        self.read_serial()

        
    def key_pressed(self, event):
        print("pressed:")
        print(repr(event.char))


    ## def on_load_menu(self, *args, **kwargs):
    ##     print("in menu laod")
    ##     filename = tk.filedialog.askopenfilename(title = "Select Model to Load (CSV)",\
    ##                                              filetypes = (("csv files","*.csv"),("all files","*.*")))
    ##     print (filename)
    ##     if filename:
    ##         new_bd = pybd.load_model_from_csv(filename)
    ##         self.bd = new_bd
    ##         self.block_list_var.set(self.bd.block_name_list)
            
    
    ## def on_save_menu(self, *args, **kwargs):
    ##     print("in menu save")
    ##     filename = tk.filedialog.asksaveasfilename(title = "Select filename",\
    ##                                                filetypes = (("csv files","*.csv"),("all files","*.*")))
    ##     print (filename)
    ##     if filename:
    ##         self.bd.save_model_to_csv(filename)
    def _quit(self, *args, **kwargs):
        print("in _quit")
        self.close_serial_port()
        #self.save_params()
        self.quit()     # stops mainloop
        self.destroy()  # this is necessary on Windows to prevent
                        # Fatal Python Error: PyEval_RestoreThread: NULL tstate


    def make_widgets(self):
        # don't assume that self.parent is a root window.
        # instead, call `winfo_toplevel to get the root window
        #self.winfo_toplevel().title("Simple Prog")
        #self.wm_title("Python Block Diagram GUI")        


        # column 0
        mycol = 0
        self.make_label_and_grid_sw("Send Text", 0, mycol)
        self.make_entry_and_var_grid_nw("send_text", 1,mycol, sticky='new')
        self.send_button = self.make_button_and_grid("Transmit", 2, mycol, \
                                                     command=self.write_serial, sticky='e')

        ## receive_text doesn't fit well with my graph
        # - side by side or notebook?
        # - make sure the force read button is always visible
        self.notebook = ttk.Notebook(self)
        self.notebook_row = 3
        self.notebook.grid(row=self.notebook_row, column=0, ipadx=10, ipady=10, \
                           sticky="news")#, columnspan=2)
        self.notebook.columnconfigure(0, weight=4)
        self.notebook.rowconfigure(0, weight=4)

        # receive notebook:
        self.make_receive_text_frame()


        # plotting notebook
        self.make_plot_frame()
        
        # column 1
        mycol = 1
        self.make_label_and_grid_sw("Portname", 0, mycol)
        self.make_entry_and_var_grid_nw("portname", 1,mycol, sticky='new')

        # plot widgets in column 1
        self.make_plot_widgets_frame()



        ## self.button_frame1 = ttk.Frame(self)
        ## self.quit_button = ttk.Button(self.button_frame1, text="Quit", command=self._quit)
        ## self.quit_button.grid(column=0, row=0, **self.options)

        ## self.draw_button = ttk.Button(self.button_frame1, text="Draw", command=self.on_draw_btn)
        ## self.draw_button.grid(column=1, row=0, **self.options)

        ## self.xlim_label = ttk.Label(self.button_frame1, text="xlim:")
        ## self.xlim.grid(row=0,column=2,sticky='E')
        ## self.xlim_var = tk.StringVar()
        ## self.xlim_box = ttk.Entry(self.button_frame1, textvariable=self.xlim_var)
        ## self.xlim_box.grid(column=3, row=0, sticky="W", padx=(0,5))


    def make_plot_widgets_frame(self):
        self.plot_widgets_frame = ttk.Frame(self)#, width=400, height=280)
        self.plot_widgets_frame.grid(row=self.notebook_row, column=1, sticky="news")
        myroot = self.plot_widgets_frame
        mycol = 0
        currow = 0
        self.make_label_and_grid_sw("X-axis Column", row=0, col=mycol, root=myroot)
        currow += 1
        self.make_combo_and_var_grid_nw("x_axis", row=currow, col=mycol, root=myroot)
        self.x_axis_combobox['values'] = [str(item) for item in range(10)]#<--- change me when data loaded
        currow += 1
        self.make_button_and_grid("Plot", currow, mycol, \
                                  command=self.generate_plot, \
                                  root=myroot)



    def update_x_col_combo(self, nc):
        self.x_axis_combobox['values'] = [str(item) for item in range(nc)]


    def generate_plot(self, *args, **kwargs):
        print("getting ready to plot something")
        self.find_latest_data()
        self._plot()


    def plot_dt(self, *args, **kwargs):
        x_col_choice = self.x_axis_var.get()
        print("x_col_choice = %s" % x_col_choice)
        if not x_col_choice:
            print("must choose the X column before plotting dt")
            return

        x_col = int(x_col_choice)
        print("x_col: %i" % x_col)
        myx = self.array[:,x_col]
        dt = myx[1:] - myx[0:-1]
        self.ax.clear()
        self.ax.plot(dt)
        self.ax.set_ylim([dt.min()*0.9, dt.max()*1.1])
        self.ax.set_xlim([0, len(dt)])
        self.canvas.draw()

        
    def _plot(self, *args, **kwargs):
        x_col_choice = self.x_axis_var.get()
        print("x_col_choice = %s" % x_col_choice)
        my_cols = list(range(self.nc))
        if x_col_choice:
            x_col = int(x_col_choice)
            print("x_col: %i" % x_col)
            my_cols.pop(x_col)
            # how do I get the other columns?
            myx = self.array[:,x_col]
        else:
            myx = np.arange(0,self.nr)

        print("my_cols: %s" % my_cols)
        plot_data = self.array[:,my_cols]
        self.ax.clear()
        self.ax.plot(myx, plot_data)
        self.ax.set_xlim([myx.min(), myx.max()])
        self.ax.set_ylim([plot_data.min(), plot_data.max()])
        self.canvas.draw()


    def find_latest_data(self):
        p = re.compile("^[0-9,\.\-]+$")
        # Approach:
        # - read data
        # - split to list
        # - start at the end of the data:
        #     - find first line that matches pattern
        #     - keep going up until first line that fails to match
        #     - keep data in between
        mystr = self.receive_text.get('1.0','end')
        mylist = mystr.split('\n')
        N_raw = len(mylist)
        for i in range(N_raw):
            currow = mylist[-i]
            if p.search(currow) is not None:
                print("bottom good row: %s" % currow)
                break
        end_row = -(i-1)

        start_search = -(end_row-1)
        for i in range(start_search,N_raw):
            currow = mylist[-i]
            if p.search(currow) is None:
                print("top bad row: %s" % currow)
                break
        start_row = N_raw-i+1
        good_rows = mylist[start_row:end_row]
        list_of_lists = [row.split(self.delim) for row in good_rows]
        str_array = np.array(list_of_lists)
        self.array = str_array.astype(float)
        self.nr, self.nc = self.array.shape
        print("num rows: %i" % self.nr)
        print("num cols: %i" % self.nc)
        self.update_x_col_combo(self.nc)
        

    def make_receive_text_frame(self):
        self.frame1 = ttk.Frame(self.notebook)#, width=400, height=280)
        self.frame1.grid(row=0, column=0, sticky="news")
        self.frame1.columnconfigure(0, weight=4)
        self.frame1.rowconfigure(1, weight=4)

        mycol = 0
        currow = 0
        self.make_label_and_grid_sw("Received Text", currow, mycol, root=self.frame1)
        currow += 1
        self.receive_text = self.make_text_box_and_grid_nw(currow, mycol, width=50, height=10, \
                                                           sticky='news', root=self.frame1)
        currow += 1
        self.read_button = self.make_button_and_grid("Force Read", currow, mycol, \
                                                     command=self.read_serial, sticky='e', \
                                                     root=self.frame1)

        self.notebook.add(self.frame1, text='Receive Text')

    def make_plot_frame(self):
        self.plot_frame = ttk.Frame(self.notebook)#, width=400, height=280)
        self.plot_frame.grid(row=0, column=0, sticky="news")
        self.plot_frame.columnconfigure(0, weight=4)
        self.plot_frame.rowconfigure(0, weight=4)

        ## plot needs a notebook
        self.fig = Figure(figsize=(6, 3), dpi=100)
        t = np.arange(0, 3, .01)
        self.ax = self.fig.add_subplot(111)
        self.ax.plot(t, 2 * np.sin(2 * np.pi * t))
        self.ax.set_xlim([0,0.5])

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=0, ipadx=40, ipady=20, \
                                         sticky="news")#, rowspan=16)

        self.toolbarFrame = ttk.Frame(master=self.plot_frame)
        self.toolbarFrame.grid(row=1,column=0)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.toolbarFrame)



        myroot = self.plot_frame
        kwargs = {'root':myroot}# note: helper functions handle padding
        curcol = 0# switching to notebook changes this

        self.notebook.add(self.plot_frame, text='Plotting')

        
        ##self.button_frame1.grid(row=20, column=0)

    ## def on_draw_btn(self, *args, **kwargs):
    ##     print("you pressed draw")
    ##     self.ax.clear()
    ##     self.bd.update_block_list()
    ##     block_list = self.bd.block_list
    ##     print("block_list: %s" % block_list)
    ##     self.bd.ax = self.ax
    ##     self.bd.draw()
    ##     xlims = self.bd.get_xlims()
    ##     ylims = self.bd.get_ylims()
    ##     self.ax.set_xlim(xlims)
    ##     self.ax.set_ylim(ylims)
    ##     self.bd.axis_off()        
    ##     self.canvas.draw()
        
        
if __name__ == "__main__":
    app = tkinter_serial_gui()
    app.startup()
    app.mainloop()
