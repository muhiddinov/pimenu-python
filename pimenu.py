#!/usr/bin/python3
from itertools import count
from time import sleep
import tkinter as TkC
from tkinter import NW, TOP, Tk, Frame, Button, Label, PhotoImage, filedialog
from subprocess import Popen, PIPE, STDOUT
import os
import sys
from math import sqrt, floor, ceil
import yaml
from threading import Thread
import json
import logging

logging.basicConfig(format='Date-Time : %(asctime)s : Line No. : %(lineno)d - %(message)s', level = logging.DEBUG)

class disk_states:
    disk_name   :str
    label1      :Label
    end_task    :bool
    type        :int
    counter     :int

    def __init__(self, counter:int, disk:str, label: Label, type=0):
        self.disk_name = disk
        self.label1 = label
        self.end_task = False
        self.type = type
        self.counter = counter

    def task_kill (self, end: bool):
        self.end_task = end

    def task_kill (self):
        self.end_task = True

    def read_process(self):
        if self.type == 1:
            p = Popen('lxterminal -e "sudo wipe -Q {0} -kqfZ {1} -R /dev/zero"'.format(self.counter, self.disk_name), stdout = PIPE, stderr = STDOUT, shell = True)
        elif self.type == 0:
            p = Popen('lxterminal -e "sudo wipe -Q {0} -kqfZ {1} -R /dev/random"'.format(self.counter, self.disk_name), stdout = PIPE, stderr = STDOUT, shell = True)
        elif self.type == 2:
            p = Popen('lxterminal -e "sudo shred -v -n1 -z {}"'.format(self.disk_name), stdout = PIPE, stderr = STDOUT, shell = True)
        elif self.type == 3:
            print('lxterminal -e "sudo shred -v -n1 -z \'{0}\' && sudo rm -rf \'{0}\'"'.format(self.disk_name))
            p = Popen('lxterminal -e "sudo shred -v -n1 -z \'{0}\' && sudo rm -rf \'{0}\'"'.format(self.disk_name), stdout = PIPE, stderr = STDOUT, shell = True)

        else:
            return

class FlatButton(Button):
    def __init__(self, master=None, cnf=None, **kw):
        Button.__init__(self, master, cnf, **kw)
        self.config(
            compound=TkC.TOP,
            relief=TkC.FLAT,
            bd=0,
            bg="#b91d47",
            fg="white",
            activebackground="#b91d47",
            activeforeground="white",
            highlightthickness=0
        )

    def set_color(self, color):
        self.configure(
            bg=color,
            fg="white",
            activebackground=color,
            activeforeground="white"
        )

    def set_font (self, font):
        self.configure(
            font=font
        )

class PiMenu(Frame):
    framestack = []
    icons = {}
    path = ''
    lastinit = 0
    disks = []
    thread_breaking = False
    items_doc = []
    drive_stat = []
    thread_tasks = []
    disk_names = []
    disk_stats = []
    status_disk = []
    disk_menu : Frame

    def __init__(self, parent):
        Frame.__init__(self, parent, background="white")
        self.parent = parent
        self.pack(fill=TkC.BOTH, expand=1)
        self.path = os.path.dirname(os.path.realpath(sys.argv[0]))
        self.disk_menu = Frame(self, bg="#000000")
        disk_det = Thread(target=self.disk_info)
        disk_det.start()
        self.initialize()

    def initialize(self):
        with open(self.path + '/pimenu.yaml', 'r') as f:
            doc = yaml.load(f, Loader=yaml.SafeLoader)
        self.lastinit = os.path.getmtime(self.path + '/pimenu.yaml')
        #while not len(self.disks):
        #    sleep(1)
        doc[0]['items'] = self.disks
        doc[2]['items'] = self.status_disk
        self.items_doc = doc
        if len(self.framestack):
            self.destroy_all()
            self.destroy_top()
        self.show_items(items=doc)

    def disk_info (self):
        with open(self.path + '/disk_utils.yaml', 'r') as f:
            doc = yaml.load(f, Loader=yaml.SafeLoader)
        while self.thread_breaking == False:
            self.disks = []
            self.disk_names = []
            p = Popen('lsblk --json', stdout = PIPE, stderr = STDOUT, shell = True)
            lines = p.stdout.readlines()
            json_data = ''
            for line in lines:
                json_data += str(line, 'utf-8')
            objs = json.loads(json_data)
            for obj in objs['blockdevices']:
                if obj['type'] == 'disk' and obj['name'][0:2] == 'sd':
                    self.disk_names.append('/dev/' + obj['name'])
                    str_obj = {
                        'name': '/dev/' + obj['name'],
                        'label': str(obj['name'][-1]).upper() + ':/ disk\n' + obj['size'],
                        'icon': 'database',
                        'color': '#3335c4',
                        'items': doc
                    }
                    if str_obj['name'] in self.disk_names:
                        if str_obj['name'] in self.disk_stats:
                            continue
                    self.disks.append(str_obj)
            self.items_doc[0]['items'] = self.disks
            self.items_doc[2]['items'] = self.status_disk
            sleep(5)

    def has_config_changed(self):
        return self.lastinit != os.path.getmtime(self.path + '/pimenu.yaml')

    def show_items(self, items, upper=None):
        if upper is None:
            upper = []
        num = 0
        wrap = Frame(self, bg="black")
        if len(self.framestack):
            self.hide_top()
            back = FlatButton(
                wrap,
                text='orqaga…',
                image=self.get_icon("arrow.left"),
                command=self.go_back,
            )
            back.set_color("#2b5797")
            back.set_font("Sans 20")
            back.grid(row=0, column=0, padx=1, pady=1, sticky=TkC.W + TkC.E + TkC.N + TkC.S)
            num += 1
        self.framestack.append(wrap)
        self.show_top()
        allitems = len(items) + num
        rows = floor(sqrt(allitems))
        cols = ceil(allitems / rows)
        for x in range(int(cols)):
            wrap.columnconfigure(x, weight=1)
        for y in range(int(rows)):
            wrap.rowconfigure(y, weight=1)
        for item in items:
            #print (item['name'])
            if item['name'] == 'empty':
                break
            #if item['name'] in self.disk_names:
            #    if item['name'] in self.disk_stats:
            #        break
            act = upper + [item['name']]
            #print (act)
            if 'icon' in item:
                image = self.get_icon(item['icon'])
            else:
                image = self.get_icon('scrabble.' + item['label'][0:1].lower())
            btn = FlatButton(
                wrap,
                text=item['label'],
                image=image
            )
            if 'items' in item:
                btn.configure(command=lambda act=act, item=item: self.show_items(item['items'], act),
                                text=item['label'])
                btn.set_color("#2b5797")

            else:
                btn.configure(command=lambda act=act: self.go_action(act), )
            if 'color' in item:
                btn.set_color(item['color'])
            btn.grid(
                row=int(floor(num / cols)),
                column=int(num % cols),
                padx=1,
                pady=1,
                sticky=TkC.W + TkC.E + TkC.N + TkC.S
            )
            btn.set_font("Sans 20")
            num += 1

    def get_icon(self, name):
        if name in self.icons:
            return self.icons[name]
        ico = self.path + '/ico/' + name + '.png'
        if not os.path.isfile(ico):
            ico = self.path + '/ico/' + name + '.gif'
            if not os.path.isfile(ico):
                ico = self.path + '/ico/cancel.gif'
        self.icons[name] = PhotoImage(file=ico)
        return self.icons[name]

    def hide_top(self):
        self.framestack[len(self.framestack) - 1].pack_forget()

    def show_top(self):
        self.framestack[len(self.framestack) - 1].pack(fill=TkC.BOTH, expand=1)

    def destroy_top(self):
        self.framestack[len(self.framestack) - 1].destroy()
        self.framestack.pop()

    def destroy_all(self):
        while len(self.framestack) > 1:
            self.destroy_top()

    def go_action(self, actions):
        self.hide_top()
        delay = Frame(self, bg="#2d89ef")
        delay.pack(fill=TkC.BOTH, expand=1)
        print(actions)
        
        if actions[len(actions) - 1] == 'quit':
            label = Label(delay, text='Dasturdan chiqish...', fg="white", bg="#2d89ef", font="Sans 30")
            label.pack(fill=TkC.BOTH, expand=1)
            self.parent.update()
            self.thread_breaking = True
            for task_disk in self.thread_tasks:
                task_disk.task_kill()
            self.quit()

        elif actions[len(actions) - 1] == 'reboot':
            label = Label(delay, text='Tizimini qayta yuklash...', fg="white", bg="#2d89ef", font="Sans 30")
            label.pack(fill=TkC.BOTH, expand=1)
            self.parent.update()
            sleep(3)
            p = Popen('sudo reboot', stdout = PIPE, stderr = STDOUT, shell = True)
            
        elif actions[len(actions) - 1] == 'shutdown':
            label = Label(delay, text="Tizimini o'chirish...", fg="white", bg="#2d89ef", font="Sans 25")
            label.pack(fill=TkC.BOTH, expand=1)
            self.parent.update()
            sleep(3)
            p = Popen('shutdown -h now', stdout = PIPE, stderr = STDOUT, shell = True)


        elif actions[len(actions) - 1] == 'shred':
            for dds in self.items_doc[0]['items']:
                if dds['name'] == actions[1]:
                    dds['items'] = [
                        {
                            'name': 'proc',
                            'label': dds['label'] + '\nburdalash jarayonida...',
                            'color': '#2b5797',
                        }
                    ]
                    self.status_disk.append(dds)
            label = Label(delay, text='{}:/ diskni burdalash'.format(str(actions[1][-1]).upper()), fg="white", bg="#2d89ef", font="Sans 30")
            label.pack(fill=TkC.BOTH, expand=1)
            self.parent.update()
            lbl = Label(self.disk_menu, text='', fg="white", bg="#2d89ef", font="Sans 15")
            lbl.pack(side=TOP, anchor=NW)
            dsks = disk_states(disk=actions[1], label=lbl, type=2, counter=1)
            thr = Thread(target=dsks.read_process)
            self.thread_tasks.append(dsks)
            thr.start()
            self.disk_stats.append(actions[1])
            sleep(3)

        elif actions[len(actions) - 1] == 'shredFile':
            
            label = Label(delay, text='{} burdalash!'.format(str(actions[1][-1]).upper()), fg="white", bg="#2d89ef", font="Sans 30")
            label.pack(fill=TkC.BOTH, expand=1)
            self.parent.update()
            lbl = Label(self.disk_menu, text='', fg="white", bg="#2d89ef", font="Sans 15")
            lbl.pack(side=TOP, anchor=NW)
            file_name = filedialog.askopenfilename(initialdir='/media/pi')
            dsks = disk_states(disk=file_name, label=lbl, type=3, counter=1)
            thr = Thread(target=dsks.read_process)
            self.thread_tasks.append(dsks)
            thr.start()
            self.disk_stats.append(actions[1])
            sleep(3)

        elif actions[len(actions) - 1] == 'zero':
            for dds in self.items_doc[0]['items']:
                if dds['name'] == actions[1]:
                    dds['items'] = [
                        {
                            'name': 'proc',
                            'label': dds['label'] + '\nnollar bilan\nto\'ldirish jarayonida...',
                            'color': '#2b5797',
                        }
                    ]
                    self.status_disk.append(dds)
            label = Label(self.disk_menu, text='{}:/ diskni nollash'.format(str(actions[1][-1]).upper()), fg="white", bg="#2d89ef", font="Sans 30")
            label.pack(fill=TkC.BOTH, expand=1)
            self.parent.update()
            lbl = Label(self.disk_menu, text='', fg="white", bg="#2d89ef", font="Sans 15")
            lbl.pack(side=TOP, anchor=NW)
            dsks = disk_states(disk=actions[1], label=lbl, type=1, counter=int(actions[len(actions)-2]))
            thr = Thread(target=dsks.read_process)
            self.thread_tasks.append(dsks)
            thr.start()
            self.disk_stats.append(actions[1])
            sleep(3)

        elif actions[len(actions) - 1] == 'random':
            for dds in self.items_doc[0]['items']:
                if dds['name'] == actions[1]:
                    dds['items'] = [
                        {
                            'name': 'proc',
                            'label': dds['label'] + "\ntasodifiy belgilar\nbilan to'ldirish\n jarayonida...",
                            'color': '#2b5797',
                        }
                    ]
                    self.status_disk.append(dds)
            label = Label(delay, text="{}:/ diskni tasodifiy\nqiymatga to'ldirish".format(str(actions[1][-1]).upper()), fg="white", bg="#2d89ef", font="Sans 30")
            label.pack(fill=TkC.BOTH, expand=1)
            self.parent.update()
            lbl = Label(self.disk_menu, text='', fg="white", bg="#2d89ef", font="Sans 15")
            lbl.pack(side=TOP, anchor=NW)
            dsks = disk_states(disk=actions[1], label=lbl, type=0, counter=int(actions[len(actions)-2]))
            thr = Thread(target=dsks.read_process)
            self.thread_tasks.append(dsks)
            thr.start()
            self.disk_stats.append(actions[1])
            sleep(3)

        elif actions[len(actions) - 1] == 'info':
            self.show_disk_state()

        delay.destroy()
        self.destroy_all()
        self.show_top()
    
    def show_disk_state (self):
        self.hide_top()
        back = FlatButton(
            self.disk_menu,
            text='orqaga…',
            image=self.get_icon("arrow.left"),
            command=self.go_back,
        )
        back.set_color("#2b5797")
        back.set_font("Sans 20")
        back.grid(row=0, column=0, padx=1, pady=1, sticky=TkC.W + TkC.E + TkC.N + TkC.S)
        
        self.disk_menu.pack(fill=TkC.BOTH, expand=1)
        self.parent.update()

    def go_back(self):
        if self.has_config_changed():
            self.initialize()
        else:
            self.destroy_top()
            self.show_top()


def main():
    root = Tk()
    root.geometry("640x480")
    root.wm_title('PiMenu')
    if len(sys.argv) > 1 and sys.argv[1] == 'fs':
        root.wm_attributes('-fullscreen', True)
    PiMenu(root)
    root.mainloop()

if __name__ == '__main__':
    main()
