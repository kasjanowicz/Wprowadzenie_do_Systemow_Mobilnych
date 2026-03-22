import random
import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

random.seed(42)

# ============================================================
#  START SYMULACJI
# ============================================================

def start_sim():
    # czyszczenie wykresów
    for w in plot_frame.winfo_children():
        w.destroy()
    for w in plot_frame_poisson.winfo_children():
        w.destroy()
    lambda_listbox.delete(0, tk.END)

    # pobranie parametrów
    L = float(entry_lambda.get())
    N = float(entry_N.get())
    S = float(entry_sigma.get())
    MIN_D = float(entry_min.get())
    MAX_D = float(entry_max.get())
    CH = int(entry_channels.get())
    QMAX = int(entry_queue.get())
    TMAX = int(entry_time.get())
    mode = mode_var.get()

    # listy danych
    arrivals = []
    durations = []
    lambda_i_list = []
    gauss_raw_list = []
    gauss_clip_list = []
    gauss_int_list = []

    # generowanie λᵢ
    t = 0.0
    while t < TMAX:
        x = random.expovariate(L)
        lambda_i_list.append(x)
        t += x
        arrivals.append(int(t) if mode == "int" else t)

    # wyświetlenie λᵢ
    for val in lambda_i_list:
        lambda_listbox.insert(tk.END, f"{val:.4f}")

    # generowanie μᵢ
    for _ in arrivals:
        g_raw = random.gauss(N, S)
        g_clip = max(MIN_D, min(MAX_D, g_raw))
        g_int = int(g_clip)
        gauss_raw_list.append(g_raw)
        gauss_clip_list.append(g_clip)
        gauss_int_list.append(g_int)
        durations.append(g_int)

    # zmienne symulacji
    idx = 0
    time_now = 0.0
    queue = []
    channels = [None for _ in range(CH)]
    served = 0
    total_wait = 0.0
    completed = 0
    rejected = 0

    times = []
    rhos = []
    Qs = []
    Ws = []

    # zmienne pomocnicze
    last_poisson_x = 0.0
    last_gauss_x1 = 0.0
    last_gauss_x2 = 0.0
    last_gauss_X = 0
    last_arrival_time = 0.0
    last_service_time = 0

    # plik wynikowy
    f = open("wyniki.txt", "w")
    f.write("lambda N sigma Min Max Channels QueueMax SimTime\n")
    f.write(f"{L} {N} {S} {MIN_D} {MAX_D} {CH} {QMAX} {TMAX}\n")
    f.write("t rho Q W\n")

    # ============================================================
    #  WYKRESY ρ/Q/W
    # ============================================================

    fig = Figure(figsize=(7, 6), dpi=100)
    ax1 = fig.add_subplot(311)
    ax2 = fig.add_subplot(312)
    ax3 = fig.add_subplot(313)

    canvas_plot = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas_plot.draw()
    canvas_plot.get_tk_widget().pack(fill="both", expand=True)

    # ============================================================
    #  WYKRESY POISSONA
    # ============================================================

    fig_p = Figure(figsize=(7, 4), dpi=100)
    axp1 = fig_p.add_subplot(121)
    axp2 = fig_p.add_subplot(122)

    canvas_poisson = FigureCanvasTkAgg(fig_p, master=plot_frame_poisson)
    canvas_poisson.draw()
    canvas_poisson.get_tk_widget().pack(fill="both", expand=True)

    def update_poisson_plots():
        axp1.clear()
        axp2.clear()

        axp1.plot(range(1, len(lambda_i_list) + 1), lambda_i_list, color="purple")
        axp1.set_title("Proces Poissona (λᵢ)")
        axp1.grid(True)

        axp2.hist(lambda_i_list, bins=20, color="orange", edgecolor="black")
        axp2.set_title("Histogram λᵢ")
        axp2.grid(True)

        canvas_poisson.draw()

    update_poisson_plots()

    # ============================================================
    #  WYKRESY ρ/Q/W
    # ============================================================

    def update_plots():
        ax1.clear()
        ax2.clear()
        ax3.clear()

        ax1.plot(times, rhos, color="red")
        ax1.set_ylabel("ρ")
        ax1.grid(True)

        ax2.plot(times, Qs, color="green")
        ax2.set_ylabel("Q")
        ax2.grid(True)

        ax3.plot(times, Ws, color="blue")
        ax3.set_ylabel("W")
        ax3.set_xlabel("czas [s]")
        ax3.grid(True)

        canvas_plot.draw()

    # ============================================================
    #  RYSOWANIE KANAŁÓW
    # ============================================================

    def draw_channels():
        canvas.delete("all")
        w = 560
        h = 80
        x0 = 20
        y0 = 40
        cw = w / CH
        for i in range(CH):
            x1 = x0 + i * cw
            x2 = x1 + cw - 5
            y1 = y0
            y2 = y0 + h
            if channels[i] is None:
                color = "lightgray"
                txt = ""
            else:
                color = "red"
                txt = str(channels[i]["rem"])
            canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")
            canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2, text=txt)

    # ============================================================
    #  STATYSTYKI
    # ============================================================

    def update_stats():
        lambda_i = L
        mu_i = 1.0 / N if N > 0 else 0.0
        rho_i = rhos[-1] if rhos else 0.0
        next_arrival = (arrivals[idx] - time_now) if idx < len(arrivals) else -1
        total_clients = idx
        poisson_count = len(lambda_i_list)
        gauss_count = len(gauss_raw_list)

        label_poisson_x.config(text=f"Poisson X: {last_poisson_x:.4f}")
        label_lambda_counter.config(text=f"Licznik lambda: {lambda_i:.4f}")
        label_gauss_x1.config(text=f"Gauss x1: {last_gauss_x1:.4f}")
        label_gauss_x2.config(text=f"Gauss x2: {last_gauss_x2:.4f}")
        label_gauss_X.config(text=f"Gauss X: {last_gauss_X}")

        label_poisson_count.config(text=f"Liczba Poissona: {poisson_count}")
        label_gauss_count.config(text=f"Liczba Gaussa: {gauss_count}")
        label_clients_count.config(text=f"Liczba klientów: {total_clients}")
        label_arrival_time.config(text=f"Czas przyjścia: {last_arrival_time:.2f}")
        label_service_time.config(text=f"Czas obsługi: {last_service_time}")
        label_lambda_i.config(text=f"Lambda i: {lambda_i:.4f}")
        label_mu_i.config(text=f"Mi i: {mu_i:.4f}")
        label_rho_i.config(text=f"Ro i: {rho_i:.4f}")

        label_queue_len.config(text=f"Kolejka: {len(queue)}")
        label_served.config(text=f"Obsłużone połączenia: {served}")
        label_next_call.config(
            text=f"Czas do nast. poł.: {next_arrival:.2f}" if next_arrival >= 0 else "Czas do nast. poł.: -"
        )
        label_rejected.config(text=f"Odrzucone: {rejected}")
        label_sim_time.config(text=f"Czas symulacji: {time_now:.0f}s")

    # ============================================================
    #  GŁÓWNA FUNKCJA KROKOWA (a–e)
    # ============================================================

    def step():
        nonlocal idx, time_now, served, total_wait, completed, rejected
        nonlocal last_poisson_x, last_gauss_x1, last_gauss_x2, last_gauss_X
        nonlocal last_arrival_time, last_service_time
        nonlocal lambda_i_list, gauss_int_list

        # koniec symulacji
        if time_now >= TMAX:
            avg_W = total_wait / completed if completed else 0.0
            f.write("\n# PODSUMOWANIE\n")
            f.write(f"# Obsłużonych: {served}\n")
            f.write(f"# Odrzuconych: {rejected}\n")
            f.write(f"# Średni czas oczekiwania W: {avg_W}\n")
            f.close()
            return

        # ========================================================
        # (a) WYBÓR k ELEMENTÓW λᵢ
        # ========================================================
        s = 0.0
        k = 0
        while k < len(lambda_i_list) and s + lambda_i_list[k] < 1.0:
            s += lambda_i_list[k]
            k += 1
        if k == 0 and lambda_i_list:
            k = 1

        # ========================================================
        # (b) UMIESZCZENIE k KLIENTÓW
        # ========================================================
        for i in range(k):
            if i >= len(gauss_int_list):
                break
            service_time = gauss_int_list[i]

            placed = False
            for c in range(CH):
                if channels[c] is None:
                    channels[c] = {"rem": service_time, "arr": time_now, "start": time_now}
                    placed = True
                    break

            if not placed:
                if len(queue) < QMAX:
                    queue.append({"dur": service_time, "arr": time_now})
                else:
                    rejected += 1

        # ========================================================
        # (d) USUNIĘCIE k ELEMENTÓW
        # ========================================================
        lambda_i_list = lambda_i_list[k:]
        gauss_int_list = gauss_int_list[k:]

        # ========================================================
        # (e) OBSŁUGA KANAŁÓW
        # ========================================================
        for c in range(CH):
            if channels[c] is None and queue:
                client = queue.pop(0)
                channels[c] = {
                    "rem": client["dur"],
                    "arr": client["arr"],
                    "start": time_now
                }

        for c in range(CH):
            if channels[c] is not None:
                channels[c]["rem"] -= 1
                if channels[c]["rem"] <= 0:
                    served += 1
                    wait = channels[c]["start"] - channels[c]["arr"]
                    total_wait += max(0, wait)
                    completed += 1
                    channels[c] = None

        # ========================================================
        # (c) LICZENIE ρ, Q, W
        # ========================================================
        busy = sum(1 for c in channels if c is not None)
        rho = busy / CH
        Q = len(queue)
        W = total_wait / completed if completed else 0.0

        times.append(time_now)
        rhos.append(rho)
        Qs.append(Q)
        Ws.append(W)

        f.write(f"{time_now:.0f} {rho} {Q} {W}\n")

        info_label.config(text=f"t={time_now:.0f}s  ρ={rho:.2f}  Q={Q}  W={W:.2f}s")

        draw_channels()
        update_plots()
        update_stats()

        time_now += 1.0
        root.after(50, step)

    step()


# ============================================================
#  GUI — WERSJA A (LEWA STRONA GUI, PRAWA STRONA WYKRESY)
# ============================================================

root = tk.Tk()
root.title("Symulator stacji bazowej")

# główna ramka
main_frame = tk.Frame(root)
main_frame.pack(fill="both", expand=True)

# lewa strona
left_frame = tk.Frame(main_frame)
left_frame.pack(side="left", fill="both", expand=True)

# prawa strona
right_frame = tk.Frame(main_frame)
right_frame.pack(side="right", fill="both", expand=True)

# ------------------------------------------------------------
# PARAMETRY
# ------------------------------------------------------------

frame = tk.Frame(left_frame)
frame.pack()

tk.Label(frame, text="λ – natężenie ruchu").grid(row=0, column=0)
entry_lambda = tk.Entry(frame); entry_lambda.insert(0, "0.5"); entry_lambda.grid(row=0, column=1)

tk.Label(frame, text="N – średnia długość rozmowy [s]").grid(row=1, column=0)
entry_N = tk.Entry(frame); entry_N.insert(0, "60"); entry_N.grid(row=1, column=1)

tk.Label(frame, text="σ – odchylenie standardowe").grid(row=2, column=0)
entry_sigma = tk.Entry(frame); entry_sigma.insert(0, "10"); entry_sigma.grid(row=2, column=1)

tk.Label(frame, text="Minimalny czas połączenia [s]").grid(row=3, column=0)
entry_min = tk.Entry(frame); entry_min.insert(0, "10"); entry_min.grid(row=3, column=1)

tk.Label(frame, text="Maksymalny czas połączenia [s]").grid(row=4, column=0)
entry_max = tk.Entry(frame); entry_max.insert(0, "120"); entry_max.grid(row=4, column=1)

tk.Label(frame, text="Liczba kanałów").grid(row=5, column=0)
entry_channels = tk.Entry(frame); entry_channels.insert(0, "5"); entry_channels.grid(row=5, column=1)

tk.Label(frame, text="Długość kolejki").grid(row=6, column=0)
entry_queue = tk.Entry(frame); entry_queue.insert(0, "10"); entry_queue.grid(row=6, column=1)

tk.Label(frame, text="Czas symulacji [s]").grid(row=7, column=0)
entry_time = tk.Entry(frame); entry_time.insert(0, "300"); entry_time.grid(row=7, column=1)

mode_var = tk.StringVar(value="int")
tk.Label(frame, text="Tryb czasu przyjścia:").grid(row=8, column=0, sticky="w")
tk.Radiobutton(frame, text="Dyskretny (int)", variable=mode_var, value="int").grid(row=8, column=1, sticky="w")
tk.Radiobutton(frame, text="Ciągły (float)", variable=mode_var, value="float").grid(row=9, column=1, sticky="w")

tk.Button(frame, text="Start", command=start_sim).grid(row=10, column=0, columnspan=2)

# ------------------------------------------------------------
# KANAŁY
# ------------------------------------------------------------

canvas = tk.Canvas(left_frame, width=600, height=200, bg="white")
canvas.pack()

info_label = tk.Label(left_frame, text="", font=("Arial", 12))
info_label.pack()

# ------------------------------------------------------------
# STATYSTYKI
# ------------------------------------------------------------

stats_frame_top = tk.Frame(left_frame)
stats_frame_top.pack()

label_poisson_x = tk.Label(stats_frame_top, text="Poisson X: -")
label_poisson_x.grid(row=0, column=0)

label_lambda_counter = tk.Label(stats_frame_top, text="Licznik lambda: -")
label_lambda_counter.grid(row=0, column=1)

label_gauss_x1 = tk.Label(stats_frame_top, text="Gauss x1: -")
label_gauss_x1.grid(row=1, column=0)

label_gauss_x2 = tk.Label(stats_frame_top, text="Gauss x2: -")
label_gauss_x2.grid(row=1, column=1)

label_gauss_X = tk.Label(stats_frame_top, text="Gauss X: -")
label_gauss_X.grid(row=1, column=2)

stats_frame_mid = tk.Frame(left_frame)
stats_frame_mid.pack()

label_poisson_count = tk.Label(stats_frame_mid, text="Liczba Poissona: -")
label_poisson_count.grid(row=0, column=0)

label_gauss_count = tk.Label(stats_frame_mid, text="Liczba Gaussa: -")
label_gauss_count.grid(row=0, column=1)

label_clients_count = tk.Label(stats_frame_mid, text="Liczba klientów: -")
label_clients_count.grid(row=0, column=2)

label_arrival_time = tk.Label(stats_frame_mid, text="Czas przyjścia: -")
label_arrival_time.grid(row=1, column=0)

label_service_time = tk.Label(stats_frame_mid, text="Czas obsługi: -")
label_service_time.grid(row=1, column=1)

label_lambda_i = tk.Label(stats_frame_mid, text="Lambda i: -")
label_lambda_i.grid(row=1, column=2)

label_mu_i = tk.Label(stats_frame_mid, text="Mi i: -")
label_mu_i.grid(row=2, column=0)

label_rho_i = tk.Label(stats_frame_mid, text="Ro i: -")
label_rho_i.grid(row=2, column=1)

stats_frame_bottom = tk.Frame(left_frame)
stats_frame_bottom.pack()

label_queue_len = tk.Label(stats_frame_bottom, text="Kolejka: -")
label_queue_len.grid(row=0, column=0, sticky="w")

label_served = tk.Label(stats_frame_bottom, text="Obsłużone połączenia: -")
label_served.grid(row=0, column=1, sticky="w")

label_next_call = tk.Label(stats_frame_bottom, text="Czas do nast. poł.: -")
label_next_call.grid(row=1, column=0, sticky="w")

label_rejected = tk.Label(stats_frame_bottom, text="Odrzucone: -")
label_rejected.grid(row=1, column=1, sticky="w")

label_sim_time = tk.Label(stats_frame_bottom, text="Czas symulacji: -")
label_sim_time.grid(row=2, column=0, sticky="w")

# ------------------------------------------------------------
# LISTA λᵢ
# ------------------------------------------------------------

lambda_frame = tk.Frame(left_frame)
lambda_frame.pack(fill="both", expand=False)

tk.Label(lambda_frame, text="Lista λᵢ (interarrival times):").pack(anchor="w")
lambda_scroll = tk.Scrollbar(lambda_frame, orient="vertical")
lambda_listbox = tk.Listbox(lambda_frame, height=6, yscrollcommand=lambda_scroll.set, width=40)
lambda_scroll.config(command=lambda_listbox.yview)
lambda_scroll.pack(side="right", fill="y")
lambda_listbox.pack(side="left", fill="both", expand=True)

# ------------------------------------------------------------
# PRAWA STRONA – WYKRESY
# ------------------------------------------------------------

plot_frame = tk.Frame(right_frame)
plot_frame.pack(fill="both", expand=True)

plot_frame_poisson = tk.Frame(right_frame)
plot_frame_poisson.pack(fill="both", expand=True)

# ------------------------------------------------------------
# START PĘTLI ZDARZEŃ
# ------------------------------------------------------------

root.mainloop()