import sqlite3
import tkinter as tk
from tkinter import messagebox

DB_PATH = "gabriel.db"


def submit_data():
    title = entries["Pealkiri"].get().strip()

    if not title:
        messagebox.showwarning("Puuduv kohustuslik väli", "Väli \"Pealkiri\" on kohustuslik.")
        entries["Pealkiri"].focus_set()
        return

    director = entries["Režissöör"].get().strip() or None
    genre = entries["Žanr"].get().strip() or None
    language = entries["Keel"].get().strip() or None
    country = entries["Riik"].get().strip() or None
    description = entries["Kirjeldus"].get().strip() or None

    release_year_text = entries["Aasta"].get().strip()
    duration_text = entries["Kestus"].get().strip()
    rating_text = entries["Reiting"].get().strip()

    try:
        release_year = int(release_year_text) if release_year_text else None
        duration = int(duration_text) if duration_text else None
        rating = float(rating_text) if rating_text else None
    except ValueError:
        messagebox.showerror("Vigane sisend", "Aasta ja kestus peavad olema täisarvud, reiting kümnendarv.")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO movies (title, director, release_year, genre, duration, rating, language, country, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (title, director, release_year, genre, duration, rating, language, country, description),
        )
        conn.commit()
        messagebox.showinfo("Õnnestus", "Filmi andmed lisati edukalt andmebaasi.")

        for entry in entries.values():
            entry.delete(0, tk.END)

    except sqlite3.Error as error:
        messagebox.showerror("Lisamine ebaõnnestus", f"Andmete lisamisel tekkis viga:\n{error}")
    finally:
        if "conn" in locals():
            conn.close()


root = tk.Tk()
root.title("Filmi andmete sisestamine")

labels = ["Pealkiri", "Režissöör", "Aasta", "Žanr", "Kestus", "Reiting", "Keel", "Riik", "Kirjeldus"]
entries = {}

for i, label in enumerate(labels):
    display_label = f"{label} *" if label == "Pealkiri" else label
    tk.Label(root, text=display_label).grid(row=i, column=0, padx=10, pady=5, sticky="e")
    entry = tk.Entry(root, width=40)
    entry.grid(row=i, column=1, padx=10, pady=5)
    entries[label] = entry

tk.Label(root, text="* kohustuslik väli", fg="red").grid(row=len(labels), column=0, columnspan=2, pady=(0, 8))

submit_button = tk.Button(root, text="Sisesta andmed", command=submit_data)
submit_button.grid(row=len(labels) + 1, column=0, columnspan=2, pady=12)

root.mainloop()
