from tkinter import *
import os

root = Tk()
termf = Frame(root, height=400, width=500)

termf.pack(fill=BOTH, expand=YES)
wid = termf.winfo_id()
print (termf.winfo_reqwidth(), termf.winfo_reqheight())
print(termf.winfo_rootx(), termf.winfo_rooty(), termf.winfo_vrootwidth(), termf.winfo_vrootheight())
os.system('xterm -into {0} -geometry {1}x{2} -sb &'.format(wid, termf.winfo_reqheight(), termf.winfo_reqwidth()))
root.mainloop()