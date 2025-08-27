import tkinter as tk
from tkinter import filedialog, messagebox
from DMO import run_pipeline

def browse_folder(entry):
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        entry.delete(0, tk.END)
        entry.insert(0, folder_selected)

def run():
    input_folder = input_folder_entry.get()
    rules_dir = rules_dir_entry.get()
    output_dir = output_dir_entry.get()
    isVendor = is_vendor_var.get()
    isCustomer = is_customer_var.get()
    isMaterial = is_material_var.get()
    materialType = material_type_entry.get()
    preprocess = preprocess_var.get()

    if not input_folder or not rules_dir or not output_dir:
        messagebox.showerror("Missing Input", "Please fill all required fields.")
        return

    try:
        result = run_pipeline(
            input_folder, isVendor, isCustomer, isMaterial,
            materialType, rules_dir, output_dir, preprocess
        )
        output_text.delete(1.0, tk.END)
        output_text.insert(tk.END, result)
        messagebox.showinfo("Success", "Processing complete!")
    except Exception as e:
        output_text.delete(1.0, tk.END)
        output_text.insert(tk.END, f"Error: {e}")
        messagebox.showerror("Error", str(e))

root = tk.Tk()
root.title("Data Processing GUI")

# Input Folder
tk.Label(root, text="Input Folder:").grid(row=0, column=0, sticky="e")
input_folder_entry = tk.Entry(root, width=50)
input_folder_entry.grid(row=0, column=1)
tk.Button(root, text="Browse", command=lambda: browse_folder(input_folder_entry)).grid(row=0, column=2)

# Rules Directory
tk.Label(root, text="Rules Directory:").grid(row=1, column=0, sticky="e")
rules_dir_entry = tk.Entry(root, width=50)
rules_dir_entry.grid(row=1, column=1)
tk.Button(root, text="Browse", command=lambda: browse_folder(rules_dir_entry)).grid(row=1, column=2)

# Output Directory
tk.Label(root, text="Output Directory:").grid(row=2, column=0, sticky="e")
output_dir_entry = tk.Entry(root, width=50)
output_dir_entry.grid(row=2, column=1)
tk.Button(root, text="Browse", command=lambda: browse_folder(output_dir_entry)).grid(row=2, column=2)

# Checkboxes
is_vendor_var = tk.BooleanVar(value=True)
is_customer_var = tk.BooleanVar(value=False)
is_material_var = tk.BooleanVar(value=False)
preprocess_var = tk.BooleanVar(value=True)

tk.Checkbutton(root, text="Is Vendor?", variable=is_vendor_var).grid(row=3, column=0, sticky="w")
tk.Checkbutton(root, text="Is Customer?", variable=is_customer_var).grid(row=3, column=1, sticky="w")
tk.Checkbutton(root, text="Is Material?", variable=is_material_var).grid(row=3, column=2, sticky="w")
tk.Checkbutton(root, text="Preprocess?", variable=preprocess_var).grid(row=4, column=0, sticky="w")

# Material Type
tk.Label(root, text="Material Type:").grid(row=4, column=1, sticky="e")
material_type_entry = tk.Entry(root, width=20)
material_type_entry.grid(row=4, column=2)

# Run Button
tk.Button(root, text="Run Pipeline", command=run, bg="green", fg="white").grid(row=5, column=1, pady=10)

# Output Text
output_text = tk.Text(root, height=10, width=80)
output_text.grid(row=6, column=0, columnspan=3, padx=10, pady=10)

root.mainloop()