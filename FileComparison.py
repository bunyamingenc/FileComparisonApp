import difflib
import tkinter as tk
from tkinter import filedialog, messagebox

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

def compare_files():
    file1 = filedialog.askopenfilename(title="Select First File")
    file2 = filedialog.askopenfilename(title="Select Second File")

    if not file1 or not file2:
        messagebox.showwarning("Warning", "Two files must be selected!")
        return

    with open(file1, "r", encoding="utf-8") as f:
        f1_lines = f.readlines()
    with open(file2, "r", encoding="utf-8") as f:
        f2_lines = f.readlines()

    text_box.delete("1.0", tk.END)

    max_lines = max(len(f1_lines), len(f2_lines))
    differences_found = False  # ✅ Fark olup olmadığını takip edecek

    for i in range(max_lines):
        l1 = f1_lines[i].rstrip("\n") if i < len(f1_lines) else ""
        l2 = f2_lines[i].rstrip("\n") if i < len(f2_lines) else ""

        if l1 != l2:
            differences_found = True  # ✅ Fark bulundu
            res1, res2 = highlight_diff(l1, l2)

            text_box.insert(tk.END, f"Line {i+1} (File1): ")
            for item in res1:
                if isinstance(item, tuple):
                    tag, content = item
                    text_box.insert(tk.END, content, tag)
                else:
                    text_box.insert(tk.END, item)
            text_box.insert(tk.END, "\n")

            text_box.insert(tk.END, f"Line {i+1} (File2): ")
            for item in res2:
                if isinstance(item, tuple):
                    tag, content = item
                    text_box.insert(tk.END, content, tag)
                else:
                    text_box.insert(tk.END, item)
            text_box.insert(tk.END, "\n\n")

    # ✅ Hiç fark yoksa mesaj göster
    if not differences_found:
        text_box.insert(tk.END, "No difference has been found, the files are identical.")


# Tkinter arayüz
root = tk.Tk()
root.title("File Comparison Tool")
root.geometry("800x600")

btn = tk.Button(root, text="Select and Compare Files", command=compare_files)
btn.pack(pady=10)

text_box = tk.Text(root, wrap="word", font=("Courier", 10))
text_box.pack(fill="both", expand=True)

# Renk tanımları
text_box.tag_config("red", foreground="red", font=("Courier", 10, "bold"))
text_box.tag_config("green", foreground="green", font=("Courier", 10, "bold"))

root.mainloop()
