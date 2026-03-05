import sqlite3
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


def get_connection():
    return sqlite3.connect(DB_PATH)


def fetch_movies(search_text=""):
    conn = get_connection()
    try:
        cursor = conn.cursor()

        if search_text:
            query = """
                SELECT id, title, director, release_year, genre, duration, rating, language, country, description
                FROM movies
                WHERE title LIKE ? OR director LIKE ? OR genre LIKE ?
                ORDER BY id DESC
            """
            pattern = f"%{search_text}%"
            cursor.execute(query, (pattern, pattern, pattern))
        else:
            query = """
                SELECT id, title, director, release_year, genre, duration, rating, language, country, description
                FROM movies
                ORDER BY id DESC
            """
            cursor.execute(query)

        return cursor.fetchall()
    finally:
        conn.close()


def refresh_table(*_):
    for row_id in tree.get_children():
        tree.delete(row_id)

    try:
        rows = fetch_movies(search_var.get().strip())
        for row in rows:
            tree.insert("", tk.END, values=row)
    except sqlite3.Error as error:
        messagebox.showerror("Viga", f"Andmete kuvamine ebaõnnestus:\n{error}")


def open_insert_form():
    form = tk.Toplevel(root)
    form.title("Filmi andmete sisestamine")
    form.transient(root)
    form.grab_set()

    labels = ["Pealkiri", "Režissöör", "Aasta", "Žanr", "Kestus", "Reiting", "Keel", "Riik", "Kirjeldus"]
    entries = {}

    for i, label in enumerate(labels):
        label_text = f"{label} *" if label == "Pealkiri" else label
        tk.Label(form, text=label_text).grid(row=i, column=0, padx=10, pady=5, sticky="e")
        entry = tk.Entry(form, width=40)
        entry.grid(row=i, column=1, padx=10, pady=5)
        entries[label] = entry

    tk.Label(form, text="* kohustuslik väli", fg="red").grid(row=len(labels), column=0, columnspan=2, pady=(0, 8))

    def submit_data():
        title = entries["Pealkiri"].get().strip()
        if not title:
            messagebox.showwarning("Puuduv kohustuslik väli", 'Väli "Pealkiri" on kohustuslik.', parent=form)
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
                parent=form,
            )
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO movies (title, director, release_year, genre, duration, rating, language, country, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (title, director, release_year, genre, duration, rating, language, country, description),
            )
            conn.commit()
            messagebox.showinfo("Õnnestus", "Filmi andmed lisati edukalt.", parent=form)
            form.destroy()
            refresh_table()
        except sqlite3.Error as error:
            messagebox.showerror("Lisamine ebaõnnestus", f"Andmete lisamisel tekkis viga:\n{error}", parent=form)
        finally:
            if "conn" in locals():
                conn.close()

    tk.Button(form, text="Sisesta andmed", command=submit_data).grid(
        row=len(labels) + 1, column=0, columnspan=2, pady=12
    )


# Põhiaken (andmete kuvamine)
root = tk.Tk()
root.title("Filmiandmebaasi vaade")
root.geometry("1200x520")

top_frame = tk.Frame(root)
top_frame.pack(fill="x", padx=10, pady=8)

tk.Label(top_frame, text="Otsi (pealkiri/režissöör/žanr):").pack(side="left")
search_var = tk.StringVar()
search_entry = tk.Entry(top_frame, textvariable=search_var, width=40)
search_entry.pack(side="left", padx=(6, 8))
search_entry.bind("<KeyRelease>", refresh_table)

tk.Button(top_frame, text="Otsi", command=refresh_table).pack(side="left", padx=(0, 8))
tk.Button(top_frame, text="Ava sisestamise vorm", command=open_insert_form).pack(side="left")

table_frame = tk.Frame(root)
table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

tree = ttk.Treeview(table_frame, columns=COLUMNS, show="headings")
for col in COLUMNS:
    tree.heading(col, text=HEADERS[col])
    width = 130 if col != "description" else 280
    if col == "id":
        width = 60
    tree.column(col, width=width, anchor="w")

# Kerimisribad
scrollbar_y = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
scrollbar_x = ttk.Scrollbar(table_frame, orient="horizontal", command=tree.xview)
tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

tree.grid(row=0, column=0, sticky="nsew")
scrollbar_y.grid(row=0, column=1, sticky="ns")
scrollbar_x.grid(row=1, column=0, sticky="ew")

table_frame.grid_rowconfigure(0, weight=1)
table_frame.grid_columnconfigure(0, weight=1)

refresh_table()
root.mainloop()
