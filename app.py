from flask import Flask, request, redirect, url_for, session, render_template_string, Response
import os
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-key")

DATABASE = os.environ.get("DATABASE_PATH", "calorie_app.db")


def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def create_database():
    connection = get_db()
    connection.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    connection.execute("""
        CREATE TABLE IF NOT EXISTS health_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            gender TEXT NOT NULL,
            age INTEGER NOT NULL,
            weight REAL NOT NULL,
            height REAL NOT NULL,
            activity REAL NOT NULL,
            goal TEXT NOT NULL,
            bmi REAL NOT NULL,
            bmr REAL NOT NULL,
            calories REAL NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    connection.commit()
    connection.close()


create_database()

STYLE = """
<style>
*{box-sizing:border-box}
body{margin:0;font-family:Arial,Tahoma,sans-serif;background:linear-gradient(135deg,#ecfdf5,#f8fffb);color:#1f2937;min-height:100vh}
nav{display:flex;justify-content:space-between;align-items:center;padding:18px 7%;background:#fff;box-shadow:0 2px 15px rgba(0,0,0,.07)}
.logo{font-size:26px;font-weight:700;color:#16a34a;text-decoration:none}
.links{display:flex;gap:12px;align-items:center}
a{text-decoration:none}
.btn{border:0;border-radius:12px;padding:12px 20px;background:#16a34a;color:#fff;cursor:pointer;font-size:16px;display:inline-block}
.btn.outline{background:#fff;color:#16a34a;border:1px solid #16a34a}
.container{width:90%;max-width:1050px;margin:auto}
.hero{min-height:62vh;display:flex;align-items:center;justify-content:center;text-align:center;padding:50px 20px}
.hero h1{font-size:clamp(38px,6vw,66px);line-height:1.12;margin:0 0 18px}
.green{color:#16a34a}
.hero p{font-size:19px;color:#4b5563;line-height:1.7}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;padding-bottom:60px}
.card{background:#fff;border-radius:20px;padding:26px;box-shadow:0 8px 28px rgba(0,0,0,.07)}
.center{text-align:center}
.form-card{max-width:520px;margin:50px auto;padding:32px;background:#fff;border-radius:22px;box-shadow:0 10px 35px rgba(0,0,0,.09)}
h1,h2,h3{margin-top:0}
label{display:block;margin:16px 0 7px;font-weight:700}
input,select{width:100%;padding:13px;border:1px solid #d1d5db;border-radius:11px;font-size:16px}
.full{width:100%;margin-top:22px}
.message{padding:12px;border-radius:10px;background:#fee2e2;color:#b91c1c;text-align:center;margin-bottom:14px}
.success{background:#dcfce7;color:#166534}
.results{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;margin:24px 0}
.number{font-size:34px;font-weight:700;color:#16a34a}
.welcome{margin-top:35px;background:linear-gradient(135deg,#16a34a,#22c55e);color:#fff;padding:30px;border-radius:22px}
table{width:100%;border-collapse:collapse}
th,td{padding:11px;border-bottom:1px solid #e5e7eb;text-align:center}
th{background:#f0fdf4}
.table-wrap{overflow-x:auto}
@media(max-width:760px){.grid,.results{grid-template-columns:1fr}.links .plain{display:none}}
</style>
"""


def nav():
    if "user_id" in session:
        return """
        <nav><a class="logo" href="/">Calorie Fit</a>
        <div class="links"><a class="plain" href="/dashboard">แดชบอร์ด</a>
        <a class="plain" href="/calculator">คำนวณ</a>
        <a class="btn outline" href="/logout">ออกจากระบบ</a></div></nav>
        """
    return """
    <nav><a class="logo" href="/">Calorie Fit</a>
    <div class="links"><a class="plain" href="/login">เข้าสู่ระบบ</a>
    <a class="btn" href="/register">สมัครสมาชิก</a></div></nav>
    """


def page(title, body, description="เว็บคำนวณ BMI BMR และแคลอรี พร้อมระบบสมาชิก"):
    return f"""<!doctype html><html lang="th"><head>
    <meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
    <title>{title}</title>
    <meta name="description" content="{description}">
    {STYLE}</head><body>{nav()}{body}</body></html>"""


@app.route("/")
def home():
    body = """
    <section class="hero"><div>
      <h1>ดูแลสุขภาพด้วย<br><span class="green">การคำนวณแคลอรี</span></h1>
      <p>คำนวณ BMI, BMR และพลังงานที่ควรได้รับต่อวัน<br>พร้อมบันทึกผลและติดตามสุขภาพในระบบเดียว</p>
      <a class="btn" href="/calculator">เริ่มต้นใช้งาน</a>
    </div></section>
    <section class="container grid">
      <div class="card center"><h2>⚖️ BMI</h2><p>ตรวจสอบดัชนีมวลกาย</p></div>
      <div class="card center"><h2>🔥 BMR/TDEE</h2><p>คำนวณพลังงานต่อวัน</p></div>
      <div class="card center"><h2>📊 ประวัติ</h2><p>บันทึกผลสำหรับสมาชิก</p></div>
    </section>
    """
    return page("Calorie Fit – คำนวณ BMI และแคลอรี", body)


@app.route("/register", methods=["GET", "POST"])
def register():
    message = ""
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm", "")
        if not name or not email or not password:
            message = "กรุณากรอกข้อมูลให้ครบ"
        elif len(password) < 6:
            message = "รหัสผ่านต้องมีอย่างน้อย 6 ตัวอักษร"
        elif password != confirm:
            message = "รหัสผ่านไม่ตรงกัน"
        else:
            db = get_db()
            exists = db.execute("SELECT id FROM users WHERE email=?", (email,)).fetchone()
            if exists:
                message = "อีเมลนี้ถูกใช้งานแล้ว"
                db.close()
            else:
                db.execute("INSERT INTO users(name,email,password) VALUES(?,?,?)",
                           (name, email, generate_password_hash(password)))
                db.commit()
                db.close()
                return redirect(url_for("login", ok=1))
    body = f"""
    <main class="form-card"><h1 class="center green">สมัครสมาชิก</h1>
    {f'<div class="message">{message}</div>' if message else ''}
    <form method="post">
      <label>ชื่อ</label><input name="name" required>
      <label>อีเมล</label><input type="email" name="email" required>
      <label>รหัสผ่าน</label><input type="password" name="password" required>
      <label>ยืนยันรหัสผ่าน</label><input type="password" name="confirm" required>
      <button class="btn full">สมัครสมาชิก</button>
    </form><p class="center"><a href="/login">มีบัญชีแล้ว</a></p></main>"""
    return page("สมัครสมาชิก – Calorie Fit", body)


@app.route("/login", methods=["GET", "POST"])
def login():
    message = "สมัครสมาชิกสำเร็จ กรุณาเข้าสู่ระบบ" if request.args.get("ok") else ""
    success = bool(request.args.get("ok"))
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        db.close()
        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            return redirect(url_for("dashboard"))
        message = "อีเมลหรือรหัสผ่านไม่ถูกต้อง"
        success = False
    cls = "message success" if success else "message"
    body = f"""
    <main class="form-card"><h1 class="center green">เข้าสู่ระบบ</h1>
    {f'<div class="{cls}">{message}</div>' if message else ''}
    <form method="post">
      <label>อีเมล</label><input type="email" name="email" required>
      <label>รหัสผ่าน</label><input type="password" name="password" required>
      <button class="btn full">เข้าสู่ระบบ</button>
    </form><p class="center"><a href="/register">สมัครสมาชิก</a></p></main>"""
    return page("เข้าสู่ระบบ – Calorie Fit", body)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


@app.route("/calculator", methods=["GET", "POST"])
def calculator():
    result = ""
    error = ""
    if request.method == "POST":
        try:
            gender = request.form["gender"]
            age = int(request.form["age"])
            weight = float(request.form["weight"])
            height = float(request.form["height"])
            activity = float(request.form["activity"])
            goal = request.form["goal"]
            if min(age, weight, height) <= 0:
                raise ValueError
            bmi = weight / ((height / 100) ** 2)
            bmr = 10 * weight + 6.25 * height - 5 * age + (5 if gender == "male" else -161)
            tdee = bmr * activity
            adjust = {"lose": -500, "maintain": 0, "gain": 300}[goal]
            calories = max(1000, tdee + adjust)
            status = ("น้ำหนักน้อย" if bmi < 18.5 else "ปกติ" if bmi < 23 else
                      "น้ำหนักเกิน" if bmi < 25 else "อ้วนระดับ 1" if bmi < 30 else "อ้วนระดับ 2")
            goal_text = {"lose": "ลดน้ำหนัก", "maintain": "รักษาน้ำหนัก", "gain": "เพิ่มน้ำหนัก"}[goal]
            if "user_id" in session:
                db = get_db()
                db.execute("""INSERT INTO health_records
                    (user_id,gender,age,weight,height,activity,goal,bmi,bmr,calories)
                    VALUES(?,?,?,?,?,?,?,?,?,?)""",
                    (session["user_id"], gender, age, weight, height, activity,
                     goal_text, bmi, bmr, calories))
                db.commit()
                db.close()
            result = f"""
            <div class="results">
              <div class="card center"><p>BMI</p><div class="number">{bmi:.2f}</div><p>{status}</p></div>
              <div class="card center"><p>BMR</p><div class="number">{bmr:.0f}</div><p>kcal/วัน</p></div>
              <div class="card center"><p>เป้าหมาย</p><div class="number">{calories:.0f}</div><p>kcal/วัน</p></div>
            </div>"""
        except (ValueError, KeyError, ZeroDivisionError):
            error = "กรุณากรอกข้อมูลให้ถูกต้อง"
    body = f"""
    <main class="container">
    <div class="form-card"><h1 class="center green">คำนวณแคลอรี</h1>
    {f'<div class="message">{error}</div>' if error else ''}
    <form method="post">
      <label>เพศ</label><select name="gender" required><option value="">เลือก</option><option value="male">ชาย</option><option value="female">หญิง</option></select>
      <label>อายุ</label><input type="number" name="age" min="1" max="120" required>
      <label>น้ำหนัก (กก.)</label><input type="number" step="0.1" name="weight" min="1" required>
      <label>ส่วนสูง (ซม.)</label><input type="number" step="0.1" name="height" min="1" required>
      <label>กิจกรรม</label><select name="activity" required>
        <option value="">เลือก</option><option value="1.2">น้อยมาก</option>
        <option value="1.375">1–3 วัน/สัปดาห์</option><option value="1.55">3–5 วัน/สัปดาห์</option>
        <option value="1.725">6–7 วัน/สัปดาห์</option><option value="1.9">หนักมาก</option>
      </select>
      <label>เป้าหมาย</label><select name="goal" required>
        <option value="">เลือก</option><option value="lose">ลดน้ำหนัก</option>
        <option value="maintain">รักษาน้ำหนัก</option><option value="gain">เพิ่มน้ำหนัก</option>
      </select>
      <button class="btn full">คำนวณ</button>
    </form></div>{result}</main>"""
    return page("คำนวณ BMI และแคลอรี – Calorie Fit", body)


@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    db = get_db()
    records = db.execute("""SELECT * FROM health_records WHERE user_id=?
                          ORDER BY id DESC LIMIT 10""", (session["user_id"],)).fetchall()
    db.close()
    rows = "".join(
        f"<tr><td>{r['created_at']}</td><td>{r['weight']:.1f}</td><td>{r['bmi']:.2f}</td><td>{r['calories']:.0f}</td><td>{r['goal']}</td></tr>"
        for r in records
    )
    history = f"""<div class="card"><h2>ประวัติการคำนวณ</h2><div class="table-wrap"><table>
    <tr><th>วันที่</th><th>น้ำหนัก</th><th>BMI</th><th>แคลอรี</th><th>เป้าหมาย</th></tr>{rows}</table></div></div>""" if rows else """
    <div class="card center"><h2>ยังไม่มีข้อมูล</h2><a class="btn" href="/calculator">เริ่มคำนวณ</a></div>"""
    body = f"""<main class="container"><section class="welcome">
    <h1>สวัสดี {session['user_name']}</h1><p>ข้อมูลสุขภาพของคุณ</p></section>
    <div style="height:22px"></div>{history}</main>"""
    return page("แดชบอร์ด – Calorie Fit", body)


@app.route("/robots.txt")
def robots():
    base = request.url_root.rstrip("/")
    return Response(f"User-agent: *\nAllow: /\nSitemap: {base}/sitemap.xml\n", mimetype="text/plain")


@app.route("/sitemap.xml")
def sitemap():
    base = request.url_root.rstrip("/")
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
      <url><loc>{base}/</loc></url>
      <url><loc>{base}/calculator</loc></url>
      <url><loc>{base}/login</loc></url>
      <url><loc>{base}/register</loc></url>
    </urlset>"""
    return Response(xml, mimetype="application/xml")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
