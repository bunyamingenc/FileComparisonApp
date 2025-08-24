import difflib
import tkinter as tk
from tkinter import filedialog, messagebox

# Global değişkenler (dosya yolları tutulacak)
file1_path = None
file2_path = None

def highlight_diff(line1, line2):
    matcher = difflib.SequenceMatcher(None, line1, line2)
    res1, res2 = [], []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            res1.append(line1[i1:i2])
            res2.append(line2[j1:j2])
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

            diff_box.insert(tk.END, f"Line {i+1} (Text1): ", "line")
            for item in res1:
                if isinstance(item, tuple):
                    tag, content = item
                    diff_box.insert(tk.END, content, tag)
                else:
                    diff_box.insert(tk.END, item)
            diff_box.insert(tk.END, "\n")

            diff_box.insert(tk.END, f"Line {i+1} (Text2): ", "line")
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
    file1_path = filedialog.askopenfilename(title="Select First File")
    file2_path = filedialog.askopenfilename(title="Select Second File")

    if not file1_path or not file2_path:
        messagebox.showwarning("Warning", "Two files must be selected!")
        return

    with open(file1_path, "r", encoding="utf-8") as f:
        content1 = f.read()
    with open(file2_path, "r", encoding="utf-8") as f:
        content2 = f.read()

    text1.delete("1.0", tk.END)
    text1.insert("1.0", content1)
    text2.delete("1.0", tk.END)
    text2.insert("1.0", content2)

    compare_texts()  # ilk açılışta farkları hemen göster

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

# --- UI ---
root = tk.Tk()
root.title("Live File Comparison Tool")
root.geometry("1000x700")
root.configure(bg="#0d1b2a")  # koyu lacivert arka plan

# Üst menü - dosya yükleme & kaydetme butonları
top_frame = tk.Frame(root, bg="#0d1b2a")
top_frame.pack(pady=5)

btn_load = tk.Button(top_frame, text="Load Files", command=load_files,
                     bg="#1b263b", fg="white", font=("Arial", 11, "bold"))
btn_load.pack(side="left", padx=5)

btn_save = tk.Button(top_frame, text="Save Changes", command=save_files,
                     bg="#1b263b", fg="white", font=("Arial", 11, "bold"))
btn_save.pack(side="left", padx=5)

frame = tk.Frame(root, bg="#0d1b2a")
frame.pack(fill="both", expand=True, padx=10, pady=10)

# İki yazı kutusu yan yana
text1 = tk.Text(frame, wrap="word", font=("Courier", 11),
                bg="#1b263b", fg="white", insertbackground="white")
text2 = tk.Text(frame, wrap="word", font=("Courier", 11),
                bg="#1b263b", fg="white", insertbackground="white")
text1.pack(side="left", fill="both", expand=True, padx=5)
text2.pack(side="left", fill="both", expand=True, padx=5)

# Farkların çıktısı altta
diff_box = tk.Text(root, wrap="word", font=("Courier", 11),
                   bg="#0d1b2a", fg="white")
diff_box.pack(fill="both", expand=True, padx=10, pady=10)

# Tag stilleri
diff_box.tag_config("red", foreground="red", font=("Courier", 11, "bold"))
diff_box.tag_config("green", foreground="lightgreen", font=("Courier", 11, "bold"))
diff_box.tag_config("line", foreground="cyan", font=("Courier", 11, "bold"))
diff_box.tag_config("identical", foreground="gray", font=("Courier", 11, "italic"))

# Her tuş sonrası karşılaştırma
text1.bind("<KeyRelease>", compare_texts)
text2.bind("<KeyRelease>", compare_texts)

root.mainloop()
