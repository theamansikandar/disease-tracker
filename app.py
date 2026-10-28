from flask import Flask, request, render_template_string
import sqlite3, os
app = Flask(__name__)
DB = os.environ.get("DB_PATH", "cases.db")

def db():
    c = sqlite3.connect(DB); c.row_factory = sqlite3.Row
    c.execute("""CREATE TABLE IF NOT EXISTS cases(id INTEGER PRIMARY KEY AUTOINCREMENT,
      patient TEXT, age INTEGER, disease TEXT, location TEXT, date TEXT, status TEXT)""")
    return c

PAGE = """<!doctype html><title>Disease Tracker v3</title>
<style>body{font-family:sans-serif;max-width:560px;margin:40px auto}
input,select,button{width:100%;padding:8px;margin:5px 0;box-sizing:border-box}
.ok{background:#d4edda;padding:10px;border-radius:6px}</style>
<h2>🦠 Disease Tracker <small>(v3 - Add, View &amp; Filter)</small></h2>
<p><a href="/">Add Case</a> | <a href="/cases">View Cases</a></p>
{% if msg %}<div class=ok>{{msg}}</div>{% endif %}
<form method=post>
<input name=patient placeholder="Patient name" required>
<input name=age type=number min=0 max=120 placeholder="Age" required>
<input name=disease placeholder="Disease (e.g. Dengue)" required>
<input name=location placeholder="Location / City" required>
<input name=date type=date required>
<select name=status><option>Active</option><option>Recovered</option><option>Deceased</option></select>
<button>Add Case</button></form>"""

@app.route("/", methods=["GET", "POST"])
def add():
    msg = None
    if request.method == "POST":
        f = request.form
        with db() as c:
            c.execute("INSERT INTO cases(patient,age,disease,location,date,status) VALUES(?,?,?,?,?,?)",
                      (f["patient"], f["age"], f["disease"], f["location"], f["date"], f["status"]))
        msg = "Case added successfully!"
    return render_template_string(PAGE, msg=msg)

LIST = """<!doctype html><title>Cases v3</title>
<style>body{font-family:sans-serif;max-width:900px;margin:40px auto}
table{border-collapse:collapse;width:100%}td,th{border:1px solid #ccc;padding:6px}th{background:#eee}</style>
<h2>🦠 All Cases <small>(v3)</small></h2><p><a href="/">+ Add Case</a></p>
<form method=get style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px">
<input name=location placeholder="Filter by location" value="{{q.location}}">
<label>From <input type=date name=date_from value="{{q.date_from}}"></label>
<label>To <input type=date name=date_to value="{{q.date_to}}"></label>
<select name=sort><option value=date {{'selected' if q.sort=='date'}}>Sort: Date</option>
<option value=location {{'selected' if q.sort=='location'}}>Sort: Location</option></select>
<select name=order><option value=desc {{'selected' if q.order=='desc'}}>Desc</option>
<option value=asc {{'selected' if q.order=='asc'}}>Asc</option></select>
<button>Apply</button> <a href="/cases">Reset</a></form>
<table><tr><th>ID</th><th>Patient</th><th>Age</th><th>Disease</th><th>Location</th><th>Date</th><th>Status</th></tr>
{% for r in rows %}<tr><td>{{r.id}}</td><td>{{r.patient}}</td><td>{{r.age}}</td><td>{{r.disease}}</td>
<td>{{r.location}}</td><td>{{r.date}}</td><td>{{r.status}}</td></tr>
{% else %}<tr><td colspan=7>No cases yet.</td></tr>{% endfor %}</table>"""

@app.route("/cases")
def view():
    a = request.args
    q = {"location": a.get("location", "").strip(), "date_from": a.get("date_from", ""),
         "date_to": a.get("date_to", ""), "sort": a.get("sort", "date"), "order": a.get("order", "desc")}
    sql, p = "SELECT * FROM cases WHERE 1=1", []
    if q["location"]: sql += " AND location LIKE ?"; p.append(f"%{q['location']}%")
    if q["date_from"]: sql += " AND date >= ?"; p.append(q["date_from"])
    if q["date_to"]: sql += " AND date <= ?"; p.append(q["date_to"])
    col = "location" if q["sort"] == "location" else "date"      # whitelist -> no SQL injection
    sql += f" ORDER BY {col} {'ASC' if q['order'] == 'asc' else 'DESC'}"
    with db() as c:
        rows = c.execute(sql, p).fetchall()
    return render_template_string(LIST, rows=rows, q=q)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
