import difflib
import tkinter as tk
from tkinter import filedialog, messagebox

# Global değişkenler
file1_path = None
file2_path = None
dark_mode = False  # Varsayılan light mode

def highlight_diff(line1, line2):
    matcher = difflib.SequenceMatcher(None, line1, line2)
    res1, res2 = [], []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            # Burada bile eşleşmeleri "değişmiş" gibi işaretle
            res1.append(("red", line1[i1:i2]))
            res2.append(("green", line2[j1:j2]))
        elif tag == "replace":
            res1.append(("red", line1[i1:i2]))
            res2.append(("green", line2[j1:j2]))
        elif tag == "delete":
            res1.append(("red", line1[i1:i2]))
        elif tag == "insert":
            res2.append(("green", line2[j1:j2]))
    return res1, res2

def compare_texts(event=None):
    diff_box.delete("1.0", tk.END)
    f1_lines = text1.get("1.0", tk.END).splitlines()
    f2_lines = text2.get("1.0", tk.END).splitlines()

    max_lines = max(len(f1_lines), len(f2_lines))
    differences_found = False

    for i in range(max_lines):
        l1 = f1_lines[i] if i < len(f1_lines) else ""
        l2 = f2_lines[i] if i < len(f2_lines) else ""

        if l1 != l2:
            differences_found = True
            res1, res2 = highlight_diff(l1, l2)

            diff_box.insert(tk.END, f"Line {i+1} (Source): ", "line")
            for item in res1:
                if isinstance(item, tuple):
                    tag, content = item
                    diff_box.insert(tk.END, content, tag)
                else:
                    diff_box.insert(tk.END, item)
            diff_box.insert(tk.END, "\n")

            diff_box.insert(tk.END, f"Line {i+1} (Target): ", "line")
            for item in res2:
                if isinstance(item, tuple):
                    tag, content = item
                    diff_box.insert(tk.END, content, tag)
                else:
                    diff_box.insert(tk.END, item)
            diff_box.insert(tk.END, "\n\n")

    if not differences_found:
        diff_box.insert(tk.END, "No differences detected – the texts are identical.", "identical")

def load_files():
    global file1_path, file2_path
    file1_path = filedialog.askopenfilename(title="Select Source File")
    file2_path = filedialog.askopenfilename(title="Select Target File")

    if not file1_path or not file2_path:
        messagebox.showwarning("Warning", "Source and Target files must be selected!")
        return

    with open(file1_path, "r", encoding="utf-8") as f:
        content1 = f.read()
    with open(file2_path, "r", encoding="utf-8") as f:
        content2 = f.read()

    text1.delete("1.0", tk.END)
    text1.insert("1.0", content1)
    text2.delete("1.0", tk.END)
    text2.insert("1.0", content2)

    compare_texts()

def save_files():
    global file1_path, file2_path
    if not file1_path or not file2_path:
        messagebox.showwarning("Warning", "You need to load files first!")
        return

    content1 = text1.get("1.0", tk.END).rstrip("\n")
    content2 = text2.get("1.0", tk.END).rstrip("\n")

    with open(file1_path, "w", encoding="utf-8") as f:
        f.write(content1)
    with open(file2_path, "w", encoding="utf-8") as f:
        f.write(content2)

    messagebox.showinfo("Saved", "Files have been updated and saved successfully!")

def toggle_theme():
    global dark_mode
    dark_mode = not dark_mode

    if dark_mode:
        bg_main = "#0d1b2a"
        bg_text = "#1b263b"
        fg_text = "white"
        line_color = "cyan"
        toggle_btn.config(text="☀ Light Mode")
    else:
        bg_main = "white"
        bg_text = "white"
        fg_text = "black"
        line_color = "#3a506b"
        toggle_btn.config(text="🌙 Dark Mode")

    # Arka plan güncelleme
    root.configure(bg=bg_main)
    top_bar.configure(bg=bg_main)
    top_frame.configure(bg=bg_main)
    frame.configure(bg=bg_main)
    source_frame.configure(bg=bg_main)
    target_frame.configure(bg=bg_main)

    lbl_source.configure(bg=bg_main, fg=line_color)
    lbl_target.configure(bg=bg_main, fg=line_color)

    text1.configure(bg=bg_text, fg=fg_text, insertbackground=fg_text)
    text2.configure(bg=bg_text, fg=fg_text, insertbackground=fg_text)
    diff_box.configure(bg=bg_text, fg=fg_text)

    diff_box.tag_config("line", foreground=line_color)

# --- UI ---
root = tk.Tk()
root.title("Live File Comparison Tool")
root.overrideredirect(True)     # Kenarlık kaldır
root.state("zoomed")            # Tam ekran aç

# Üst menü bar
top_bar = tk.Frame(root, bg="white", relief="raised", bd=0, height=30)
top_bar.pack(fill="x", side="top")

app_title = tk.Label(top_bar, text=" Live File Comparison Tool ",
                     bg="white", fg="#3a506b", font=("Arial", 11, "bold"))
app_title.pack(side="left", padx=10)

# Minimize & Exit
btn_min = tk.Button(top_bar, text="_", command=lambda: root.iconify(),
                    bg="#3a506b", fg="white", bd=0, width=3, font=("Arial", 10, "bold"))
btn_min.pack(side="right", padx=2)

btn_exit = tk.Button(top_bar, text="X", command=lambda: root.destroy(),
                     bg="red", fg="white", bd=0, width=3, font=("Arial", 10, "bold"))
btn_exit.pack(side="right", padx=2)

# Dark/Light Mode Toggle
toggle_btn = tk.Button(top_bar, text="🌙 Dark Mode", command=toggle_theme,
                       bg="#3a506b", fg="white", font=("Arial", 10, "bold"))
toggle_btn.pack(side="right", padx=5)

# Üst menü - dosya yükleme & kaydetme butonları
top_frame = tk.Frame(root, bg="white")
top_frame.pack(pady=5)

btn_load = tk.Button(top_frame, text="Load Files", command=load_files,
                     bg="#3a506b", fg="white", font=("Arial", 11, "bold"))
btn_load.pack(side="left", padx=5)

btn_save = tk.Button(top_frame, text="Save Changes", command=save_files,
                     bg="#3a506b", fg="white", font=("Arial", 11, "bold"))
btn_save.pack(side="left", padx=5)

frame = tk.Frame(root, bg="white")
frame.pack(fill="both", expand=True, padx=10, pady=10)

# Sol - Source
source_frame = tk.Frame(frame, bg="white")
source_frame.grid(row=0, column=0, sticky="nsew", padx=5)

lbl_source = tk.Label(source_frame, text="Source", bg="white",
                      fg="#3a506b", font=("Arial", 12, "bold"))
lbl_source.pack(anchor="n")

text1 = tk.Text(source_frame, wrap="word", font=("Courier", 11),
                bg="white", fg="black", insertbackground="black")
text1.pack(fill="both", expand=True)

# Sağ - Target
target_frame = tk.Frame(frame, bg="white")
target_frame.grid(row=0, column=1, sticky="nsew", padx=5)

lbl_target = tk.Label(target_frame, text="Target", bg="white",
                      fg="#3a506b", font=("Arial", 12, "bold"))
lbl_target.pack(anchor="n")

text2 = tk.Text(target_frame, wrap="word", font=("Courier", 11),
                bg="white", fg="black", insertbackground="black")
text2.pack(fill="both", expand=True)

# Grid ayarları (eşit boyut)
frame.columnconfigure(0, weight=1)
frame.columnconfigure(1, weight=1)
frame.rowconfigure(0, weight=1)

# Farkların çıktısı altta
diff_box = tk.Text(root, wrap="word", font=("Courier", 11),
                   bg="white", fg="black")
diff_box.pack(fill="both", expand=True, padx=10, pady=10)

# Tag stilleri
diff_box.tag_config("red", foreground="red", font=("Courier", 11, "bold"))
diff_box.tag_config("green", foreground="green", font=("Courier", 11, "bold"))
diff_box.tag_config("line", foreground="#3a506b", font=("Courier", 11, "bold"))
diff_box.tag_config("identical", foreground="gray", font=("Courier", 11, "italic"))

# Her tuş sonrası karşılaştırma
text1.bind("<KeyRelease>", compare_texts)
text2.bind("<KeyRelease>", compare_texts)

root.mainloop()

