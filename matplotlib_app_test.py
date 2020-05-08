"""
   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

""" This simple example shows how to display a matplotlib plot image.
    The MatplotImage gets addressed by url requests that points to 
     a specific method. The displayed image url points to "get_image_data" 
    Passing an additional parameter "update_index" we inform the browser 
     about an image change so forcing the image update.
"""

import io
import time
import threading

import remi.gui as gui
from remi import start, App

import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
from threading import Timer


class MatplotImage(gui.Image):
    ax = None

    def __init__(self, **kwargs):
        super(MatplotImage, self).__init__("/%s/get_image_data?update_index=0" % id(self), **kwargs)
        self._buf = None
        self._buflock = threading.Lock()

        self._fig = Figure(figsize=(4, 4))
        self.ax = self._fig.add_subplot(111)

        self.redraw()

    def redraw(self):
        canv = FigureCanvasAgg(self._fig)
        buf = io.BytesIO()
        canv.print_figure(buf, format='png')
        with self._buflock:
            if self._buf is not None:
                self._buf.close()
            self._buf = buf

        i = int(time.time() * 1e6)
        self.attributes['src'] = "/%s/get_image_data?update_index=%d" % (id(self), i)

        super(MatplotImage, self).redraw()

    def get_image_data(self, update_index):
        with self._buflock:
            if self._buf is None:
                return None
            self._buf.seek(0)
            data = self._buf.read()

        return [data, {'Content-type': 'image/png'}]

class MyApp(App):
    def __init__(self, *args):
        super(MyApp, self).__init__(*args)
        
    def idle(self):
        self.time_counter.set_text('Elapsed time: ' "%.1f" % self.time_count)

    def main(self): # i.e., setup? when does this run? "start"?
        wid = gui.VBox(width=350, height=600, margin='0px auto')
        wid.style['text-align'] = 'center'
        
        # "generate data" button
        bt = gui.Button('Data', width=100, height=30)
        bt.style['margin'] = '10px'
        bt.onclick.do(self.on_button_pressed)

        # "clear" button
        bt2 = gui.Button('Clear', width = 300, height = 60)
        bt2.style['margin'] = '10px'
        bt2.onclick.do(self.on_clear_pressed)

        # "count" button
        bt_counter = gui.Button('Count', width = 100, height = 50)
        bt_counter.style['margin'] = '10px'
        bt_counter.onclick.do(self.on_counter_pressed)
        
        # "reset" button
        bt_counter_reset = gui.Button('Reset count', width = 100, height = 50)
        bt_counter_reset.style['margin'] = '10px'
        bt_counter_reset.onclick.do(self.on_counter_reset_pressed)
        
        # "reset timer" button
        timer_reset = gui.Button('Reset timer', width = 100, height = 50)
        timer_reset.style['margin'] = '10px'
        timer_reset.onclick.do(self.on_timer_reset_pressed)
        
        # plot and plot components
        self.plot_data = np.array([0])
        self.mpl = MatplotImage(width=250, height=250)
        self.mpl.style['margin'] = '10px'
        self.mpl.ax.set_title("test")
        self.mpl.ax.plot(self.plot_data)
        self.mpl.redraw()
       
        # button counter
        self.button_count = 0
        self.counter = gui.Label('Button presses: 0', width=200, height=30, margin='10px')
        
        # timer
        self.time_count = 0
        self.time_counter = gui.Label('Elapsed time: ', width=200, height=30, margin='10px')
        self.reset_time_flag = False
        self.display_time_counter() # starts the recurring timing
     
        # Build widget from buttons
        wid.append(bt)
        wid.append(bt2)
        wid.append(bt_counter)
        wid.append(bt_counter_reset)
        wid.append(timer_reset)
        wid.append(self.counter)
        wid.append(self.time_counter)
        wid.append(self.mpl)
        return wid

    def display_time_counter(self):
        if self.reset_time_flag == True:
            self.time_count = 0
            self.reset_time_flag = False
        else:
            self.time_count += 0.1
            self.time_count = np.round(self.time_count, decimals = 1)
        
        Timer(0.1, self.display_time_counter).start() # re-calls this every second
        
    def on_button_pressed(self, widget):
        self.plot_data = np.append(self.plot_data, self.plot_data[-1] -1 + 2*np.round(np.random.rand()))
        self.mpl.ax.plot(self.plot_data, 'k.')
        self.mpl.ax.plot(self.plot_data, 'k')
        self.mpl.redraw()

    def on_clear_pressed(self, widget):
        self.plot_data = [0]
        self.mpl.ax.clear()
        self.mpl.redraw()
        
    def on_counter_pressed(self, widget):
        self.button_count += 1
        self.counter.set_text("Button presses: " + str(self.button_count))
        
    def on_counter_reset_pressed(self, widget):
        self.button_count = 0
        self.counter.set_text("Button presses: " + str(self.button_count))
        
    def on_timer_reset_pressed(self, widget):
        self.reset_time_flag = True

        
if __name__ == "__main__": # i.e., this only runs when executed rather than imported
    import socket
    host = socket.gethostbyname(socket.gethostname())
    start(MyApp, debug = False, address = host, port = 8000)
