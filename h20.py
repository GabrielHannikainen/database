import sqlite3
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox, ttk

DB_PATH = "gabriel.db"

COLUMNS = [
    "id",
    "title",
    "director",
    "release_year",
    "genre",
    "duration",
    "rating",
    "language",
    "country",
    "description",
]

HEADERS = {
    "id": "ID",
    "title": "Pealkiri",
    "director": "Režissöör",
    "release_year": "Aasta",
    "genre": "Žanr",
    "duration": "Kestus",
    "rating": "Reiting",
    "language": "Keel",
    "country": "Riik",
    "description": "Kirjeldus",
}

FIELD_MAP = {
    "Pealkiri": "title",
    "Režissöör": "director",
    "Aasta": "release_year",
    "Žanr": "genre",
    "Kestus": "duration",
    "Reiting": "rating",
    "Keel": "language",
    "Riik": "country",
    "Kirjeldus": "description",
}


def get_connection():
    return sqlite3.connect(DB_PATH)


def fetch_movies(search_text=""):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        if search_text:
            pattern = f"%{search_text}%"
            cursor.execute(
                """
                SELECT id, title, director, release_year, genre, duration, rating, language, country, description
                FROM movies
                WHERE title LIKE ? OR director LIKE ? OR genre LIKE ?
                ORDER BY id DESC
                """,
                (pattern, pattern, pattern),
            )
        else:
            cursor.execute(
                """
                SELECT id, title, director, release_year, genre, duration, rating, language, country, description
                FROM movies
                ORDER BY id DESC
                """
            )
        return cursor.fetchall()
    finally:
        conn.close()


def refresh_table(*_):
    for item in tree.get_children():
        tree.delete(item)

    try:
        for row in fetch_movies(search_var.get().strip()):
            tree.insert("", tk.END, values=row)
    except sqlite3.Error as error:
        messagebox.showerror("Viga", f"Andmete kuvamine ebaõnnestus:\n{error}")


def open_insert_form():
    try:
        subprocess.Popen([sys.executable, "h17.py"])
    except Exception as error:
        messagebox.showerror("Viga", f"Sisestusvormi avamine ebaõnnestus:\n{error}")


def open_update_form():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Valik puudub", "Vali tabelist rida, mida soovid muuta.")
        return

    values = tree.item(selected[0], "values")
    movie_id = int(values[0])

    edit_window = tk.Toplevel(root)
    edit_window.title("Muuda filmi andmeid")
    edit_window.transient(root)
    edit_window.grab_set()

    labels = ["Pealkiri", "Režissöör", "Aasta", "Žanr", "Kestus", "Reiting", "Keel", "Riik", "Kirjeldus"]
    entries = {}

    record = {
        "title": values[1],
        "director": values[2],
        "release_year": values[3],
        "genre": values[4],
        "duration": values[5],
        "rating": values[6],
        "language": values[7],
        "country": values[8],
        "description": values[9],
    }

    for i, label in enumerate(labels):
        label_text = f"{label} *" if label == "Pealkiri" else label
        tk.Label(edit_window, text=label_text).grid(row=i, column=0, padx=10, pady=5, sticky="e")
        entry = tk.Entry(edit_window, width=40)
        entry.grid(row=i, column=1, padx=10, pady=5)

        value = record[FIELD_MAP[label]]
        if value is None:
            value = ""
        entry.insert(0, str(value))
        entries[label] = entry

    tk.Label(edit_window, text="* kohustuslik väli", fg="red").grid(
        row=len(labels), column=0, columnspan=2, pady=(0, 8)
    )

    def update_data():
        title = entries["Pealkiri"].get().strip()
        if not title:
            messagebox.showwarning("Puuduv kohustuslik väli", 'Väli "Pealkiri" on kohustuslik.', parent=edit_window)
            entries["Pealkiri"].focus_set()
            return

        director = entries["Režissöör"].get().strip() or None
        genre = entries["Žanr"].get().strip() or None
        language = entries["Keel"].get().strip() or None
        country = entries["Riik"].get().strip() or None
        description = entries["Kirjeldus"].get().strip() or None

        year_text = entries["Aasta"].get().strip()
        duration_text = entries["Kestus"].get().strip()
        rating_text = entries["Reiting"].get().strip()

        try:
            release_year = int(year_text) if year_text else None
            duration = int(duration_text) if duration_text else None
            rating = float(rating_text) if rating_text else None
        except ValueError:
            messagebox.showerror(
                "Vigane sisend",
                "Aasta ja kestus peavad olema täisarvud, reiting peab olema komaarv.",
                parent=edit_window,
            )
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE movies
                SET title = ?, director = ?, release_year = ?, genre = ?, duration = ?, rating = ?, language = ?, country = ?, description = ?
                WHERE id = ?
                """,
                (title, director, release_year, genre, duration, rating, language, country, description, movie_id),
            )
            conn.commit()

            if cursor.rowcount == 0:
                messagebox.showerror("Muutmine ebaõnnestus", "Kirjet ei leitud või muutmist ei toimunud.", parent=edit_window)
            else:
                messagebox.showinfo("Muutmine õnnestus", "Andmed uuendati edukalt.", parent=edit_window)
                edit_window.destroy()
                refresh_table()

        except sqlite3.Error as error:
            messagebox.showerror("Muutmine ebaõnnestus", f"Andmete muutmisel tekkis viga:\n{error}", parent=edit_window)
        finally:
            if "conn" in locals():
                conn.close()

    tk.Button(edit_window, text="Salvesta muudatused", command=update_data).grid(
        row=len(labels) + 1, column=0, columnspan=2, pady=12
    )


def delete_selected_row():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Valik puudub", "Vali tabelist rida, mida soovid kustutada.")
        return

    values = tree.item(selected[0], "values")
    movie_id = int(values[0])
    title = values[1]

    confirm = messagebox.askyesno(
        "Kustutamise kinnitus",
        f'Kas soovid kindlasti kustutada filmi "{title}" (ID: {movie_id})?'
    )
    if not confirm:
        return

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM movies WHERE id = ?", (movie_id,))
        conn.commit()

        if cursor.rowcount == 0:
            messagebox.showerror("Kustutamine ebaõnnestus", "Kirjet ei leitud või seda ei saanud kustutada.")
        else:
            messagebox.showinfo("Kustutamine õnnestus", "Rida kustutati edukalt.")
            refresh_table()  # värskendab andmed pärast kustutamist

    except sqlite3.Error as error:
        messagebox.showerror("Kustutamine ebaõnnestus", f"Kustutamisel tekkis viga:\n{error}")
    finally:
        if "conn" in locals():
            conn.close()


root = tk.Tk()
root.title("Filmiandmebaasi vaade")
root.geometry("1200x540")

controls = tk.Frame(root)
controls.pack(fill="x", padx=10, pady=8)

tk.Label(controls, text="Otsi (pealkiri/režissöör/žanr):").pack(side="left")
search_var = tk.StringVar()
search_entry = tk.Entry(controls, textvariable=search_var, width=40)
search_entry.pack(side="left", padx=(6, 8))
search_entry.bind("<KeyRelease>", refresh_table)

tk.Button(controls, text="Otsi", command=refresh_table).pack(side="left", padx=(0, 8))
tk.Button(controls, text="Ava sisestamise vorm", command=open_insert_form).pack(side="left", padx=(0, 8))
tk.Button(controls, text="Muuda valitud rida", command=open_update_form).pack(side="left", padx=(0, 8))
tk.Button(controls, text="Kustuta valitud rida", command=delete_selected_row).pack(side="left")

table_frame = tk.Frame(root)
table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

tree = ttk.Treeview(table_frame, columns=COLUMNS, show="headings")
for col in COLUMNS:
    tree.heading(col, text=HEADERS[col])
    width = 130 if col != "description" else 280
    if col == "id":
        width = 60
    tree.column(col, width=width, anchor="w")

scroll_y = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
scroll_x = ttk.Scrollbar(table_frame, orient="horizontal", command=tree.xview)
tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

tree.grid(row=0, column=0, sticky="nsew")
scroll_y.grid(row=0, column=1, sticky="ns")
scroll_x.grid(row=1, column=0, sticky="ew")

table_frame.grid_rowconfigure(0, weight=1)
table_frame.grid_columnconfigure(0, weight=1)

refresh_table()
root.mainloop()
