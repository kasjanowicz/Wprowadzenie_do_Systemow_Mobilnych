import random
import math
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk

S = 10
lambda_O = 2.0
lambda_H = 1.0
mu = 1/3.0
SIM_TIME = 5000

random.seed(42)

time_now = 0.0
busy = 0
arr_O = 0
arr_H = 0
blk_O = 0
blk_H = 0
end_times = []
next_O = random.expovariate(lambda_O)
next_H = random.expovariate(lambda_H)
times = []
busy_hist = []

def dep(t):
    return t + random.expovariate(mu)

while time_now < SIM_TIME:
    next_dep = min(end_times) if end_times else math.inf
    if next_O <= next_H and next_O <= next_dep:
        time_now = next_O
        arr_O += 1
        if busy < S:
            busy += 1
            end_times.append(dep(time_now))
        else:
            blk_O += 1
        next_O = time_now + random.expovariate(lambda_O)
    elif next_H < next_O and next_H <= next_dep:
        time_now = next_H
        arr_H += 1
        if busy < S:
            busy += 1
            end_times.append(dep(time_now))
        else:
            blk_H += 1
        next_H = time_now + random.expovariate(lambda_H)
    else:
        time_now = next_dep
        end_times.remove(next_dep)
        busy -= 1
    times.append(time_now)
    busy_hist.append(busy)

BO = blk_O / arr_O
BH = blk_H / arr_H

root = tk.Tk()
root.title("Symulator M/M/S/S")

fig, ax = plt.subplots(figsize=(7,4))
ax.plot(times, busy_hist)
ax.set_title("Zajętość kanałów w czasie")
ax.set_xlabel("Czas")
ax.set_ylabel("Zajęte kanały")
ax.grid(True)

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.draw()
canvas.get_tk_widget().pack()

label = tk.Label(root, text=f"BO = {BO:.4f}    BH = {BH:.4f}", font=("Arial", 14))
label.pack()

root.mainloop()