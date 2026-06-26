from flask import Flask, request, redirect, url_for, session, render_template_string, Response
import os
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-key")
DATABASE = os.environ.get("DATABASE_PATH", "calorie_app.db")


def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db


def create_database():
    db = get_db()
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    db.execute("""
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
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS walking_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            steps INTEGER NOT NULL,
            height REAL NOT NULL,
            gender TEXT NOT NULL,
            minutes REAL,
            distance_km REAL NOT NULL,
            speed_kmh REAL,
            goal_percent REAL NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    db.commit()
    db.close()


create_database()

STYLE = """
<style>
:root{--green:#16a34a;--dark:#15803d;--soft:#ecfdf5;--text:#1f2937;--muted:#6b7280}
*{box-sizing:border-box}
body{margin:0;font-family:Arial,Tahoma,sans-serif;background:linear-gradient(135deg,#ecfdf5,#f8fffb);color:var(--text);min-height:100vh}
nav{display:flex;justify-content:space-between;align-items:center;padding:18px 7%;background:#fff;box-shadow:0 2px 15px rgba(0,0,0,.07);position:sticky;top:0;z-index:10}
.logo{font-size:26px;font-weight:700;color:var(--green);text-decoration:none}
.links{display:flex;gap:14px;align-items:center;flex-wrap:wrap}
a{text-decoration:none;color:inherit}
.plain{font-weight:700;color:#374151}
.btn{border:0;border-radius:12px;padding:12px 20px;background:var(--green);color:#fff;cursor:pointer;font-size:16px;display:inline-block}
.btn:hover{background:var(--dark)}
.btn.outline{background:#fff;color:var(--green);border:1px solid var(--green)}
.container{width:90%;max-width:1120px;margin:auto}
.hero{min-height:66vh;display:grid;grid-template-columns:1.1fr .9fr;gap:38px;align-items:center;padding:60px 0}
.hero h1{font-size:clamp(40px,6vw,70px);line-height:1.1;margin:0 0 18px}
.hero p{font-size:19px;color:#4b5563;line-height:1.75}
.green{color:var(--green)}
.illustration{background:linear-gradient(145deg,#dcfce7,#fff);border-radius:32px;padding:24px;box-shadow:0 20px 55px rgba(22,163,74,.15)}
.illustration svg{width:100%;height:auto;display:block}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;padding-bottom:65px}
.card{background:#fff;border-radius:20px;padding:26px;box-shadow:0 8px 28px rgba(0,0,0,.07)}
.center{text-align:center}
.icon{font-size:44px;margin-bottom:12px}
.form-card{max-width:560px;margin:50px auto;padding:32px;background:#fff;border-radius:22px;box-shadow:0 10px 35px rgba(0,0,0,.09)}
label{display:block;margin:16px 0 7px;font-weight:700}
input,select{width:100%;padding:13px;border:1px solid #d1d5db;border-radius:11px;font-size:16px;background:#fff}
.full{width:100%;margin-top:22px}
.message{padding:12px;border-radius:10px;background:#fee2e2;color:#b91c1c;text-align:center;margin-bottom:14px}
.success{background:#dcfce7;color:#166534}
.results{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;margin:24px 0}
.number{font-size:34px;font-weight:700;color:var(--green)}
.welcome{margin-top:35px;background:linear-gradient(135deg,#16a34a,#22c55e);color:#fff;padding:30px;border-radius:22px}
table{width:100%;border-collapse:collapse}
th,td{padding:11px;border-bottom:1px solid #e5e7eb;text-align:center}
th{background:#f0fdf4}
.table-wrap{overflow-x:auto}
.progress{height:16px;border-radius:999px;background:#e5e7eb;overflow:hidden;margin-top:12px}
.progress div{height:100%;background:linear-gradient(90deg,#16a34a,#22c55e)}
.note{background:#fffbeb;border-left:5px solid #f59e0b;border-radius:12px;padding:14px 16px;color:#92400e;margin-top:18px}
.walk-layout{display:grid;grid-template-columns:.9fr 1.1fr;gap:24px;align-items:start;padding:45px 0 65px}
.small{font-size:14px;color:var(--muted)}
@media(max-width:850px){.hero,.walk-layout{grid-template-columns:1fr}.hero{text-align:center}.grid,.results{grid-template-columns:1fr}}
@media(max-width:680px){.links .plain{display:none}nav{padding:14px 5%}}
</style>
"""

HERO_SVG = """
<svg viewBox="0 0 620 480">
  <rect x="20" y="20" width="580" height="440" rx="38" fill="#f0fdf4"/>
  <circle cx="480" cy="110" r="52" fill="#bbf7d0"/>
  <circle cx="130" cy="370" r="65" fill="#dcfce7"/>
  <circle cx="320" cy="112" r="38" fill="#f6c28b"/>
  <path d="M285 97c8-44 70-51 87-13-17-8-32-9-50-3-15 5-26 12-37 16z" fill="#1f2937"/>
  <path d="M279 163c26-12 63-12 89 0 29 14 46 43 44 76l-4 79H239l-4-79c-2-33 15-62 44-76z" fill="#16a34a"/>
  <path d="M250 211l-72 55M403 210l66 61" stroke="#166534" stroke-width="22" stroke-linecap="round"/>
  <path d="M279 316l-42 95M363 316l47 95" stroke="#1f2937" stroke-width="26" stroke-linecap="round"/>
  <rect x="75" y="70" width="150" height="100" rx="22" fill="#fff" stroke="#bbf7d0" stroke-width="4"/>
  <text x="150" y="108" text-anchor="middle" font-size="22" font-family="Arial" fill="#166534">8,240</text>
  <text x="150" y="140" text-anchor="middle" font-size="16" font-family="Arial" fill="#6b7280">ก้าววันนี้</text>
  <rect x="416" y="310" width="145" height="90" rx="22" fill="#fff" stroke="#bbf7d0" stroke-width="4"/>
  <text x="488" y="347" text-anchor="middle" font-size="22" font-family="Arial" fill="#166534">5.8 km</text>
  <text x="488" y="376" text-anchor="middle" font-size="16" font-family="Arial" fill="#6b7280">ระยะเดิน</text>
</svg>
"""

WALK_SVG = """
<svg viewBox="0 0 520 390">
  <rect x="20" y="20" width="480" height="350" rx="34" fill="#f0fdf4"/>
  <path d="M65 315C160 230 270 325 455 190" fill="none" stroke="#86efac" stroke-width="18" stroke-linecap="round"/>
  <circle cx="285" cy="92" r="34" fill="#f6c28b"/>
  <path d="M255 82c12-31 52-34 66-6-26-9-47-5-66 6z" fill="#1f2937"/>
  <path d="M255 138c31-18 71-5 84 29l20 55-51 20-25-49-38 54-43-27 53-82z" fill="#16a34a"/>
  <path d="M307 239l62 76M272 235l-45 85" stroke="#1f2937" stroke-width="22" stroke-linecap="round"/>
  <path d="M333 169l68 34M250 166l-62 37" stroke="#166534" stroke-width="18" stroke-linecap="round"/>
  <circle cx="100" cy="105" r="42" fill="#dcfce7"/>
  <text x="100" y="112" text-anchor="middle" font-size="22" font-family="Arial" fill="#166534">10K</text>
  <circle cx="430" cy="90" r="42" fill="#dcfce7"/>
  <text x="430" y="98" text-anchor="middle" font-size="19" font-family="Arial" fill="#166534">GO!</text>
</svg>
"""


def nav():
    if "user_id" in session:
        return """
        <nav><a class="logo" href="/">Calorie Fit</a><div class="links">
        <a class="plain" href="/dashboard">แดชบอร์ด</a>
        <a class="plain" href="/calculator">คำนวณแคลอรี</a>
        <a class="plain" href="/walking">คำนวณการเดิน</a>
        <a class="btn outline" href="/logout">ออกจากระบบ</a>
        </div></nav>
        """
    return """
    <nav><a class="logo" href="/">Calorie Fit</a><div class="links">
    <a class="plain" href="/calculator">คำนวณแคลอรี</a>
    <a class="plain" href="/walking">คำนวณการเดิน</a>
    <a class="plain" href="/login">เข้าสู่ระบบ</a>
    <a class="btn" href="/register">สมัครสมาชิก</a>
    </div></nav>
    """


def page(title, body):
    return f"""<!doctype html><html lang="th"><head>
    <meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
    <title>{title}</title>
    <meta name="description" content="เว็บคำนวณ BMI BMR แคลอรี และระยะทางการเดินในแต่ละวัน">
    {STYLE}</head><body>{nav()}{body}</body></html>"""


@app.route("/")
def home():
    body = f"""
    <main class="container">
      <section class="hero">
        <div>
          <h1>สุขภาพดีขึ้นได้<br><span class="green">ในทุกก้าวของคุณ</span></h1>
          <p>คำนวณ BMI, BMR, พลังงานต่อวัน และประเมินระยะทางจากจำนวนก้าวเดิน พร้อมบันทึกประวัติในระบบเดียว</p>
          <div class="links"><a class="btn" href="/calculator">คำนวณแคลอรี</a><a class="btn outline" href="/walking">คำนวณการเดิน</a></div>
        </div>
        <div class="illustration">{HERO_SVG}</div>
      </section>
      <section class="grid">
        <div class="card center"><div class="icon">⚖️</div><h2>BMI และ BMR</h2><p>ประเมินรูปร่างและพลังงานพื้นฐาน</p></div>
        <div class="card center"><div class="icon">🚶</div><h2>ระยะเดินต่อวัน</h2><p>แปลงจำนวนก้าวเป็นระยะทาง</p></div>
        <div class="card center"><div class="icon">📊</div><h2>บันทึกย้อนหลัง</h2><p>ดูข้อมูลสุขภาพและการเดินย้อนหลัง</p></div>
      </section>
    </main>"""
    return page("Calorie Fit – สุขภาพและการเดิน", body)


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
    body = f"""<main class="form-card"><h1 class="center green">สมัครสมาชิก</h1>
    {f'<div class="message">{message}</div>' if message else ''}
    <form method="post"><label>ชื่อ</label><input name="name" required>
    <label>อีเมล</label><input type="email" name="email" required>
    <label>รหัสผ่าน</label><input type="password" name="password" required>
    <label>ยืนยันรหัสผ่าน</label><input type="password" name="confirm" required>
    <button class="btn full">สมัครสมาชิก</button></form></main>"""
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
    body = f"""<main class="form-card"><h1 class="center green">เข้าสู่ระบบ</h1>
    {f'<div class="{cls}">{message}</div>' if message else ''}
    <form method="post"><label>อีเมล</label><input type="email" name="email" required>
    <label>รหัสผ่าน</label><input type="password" name="password" required>
    <button class="btn full">เข้าสู่ระบบ</button></form></main>"""
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
            bmi = weight / ((height / 100) ** 2)
            bmr = 10 * weight + 6.25 * height - 5 * age + (5 if gender == "male" else -161)
            tdee = bmr * activity
            calories = max(1000, tdee + {"lose": -500, "maintain": 0, "gain": 300}[goal])
            status = "น้ำหนักน้อย" if bmi < 18.5 else "ปกติ" if bmi < 23 else "น้ำหนักเกิน" if bmi < 25 else "อ้วนระดับ 1" if bmi < 30 else "อ้วนระดับ 2"
            goal_text = {"lose": "ลดน้ำหนัก", "maintain": "รักษาน้ำหนัก", "gain": "เพิ่มน้ำหนัก"}[goal]
            if "user_id" in session:
                db = get_db()
                db.execute("""INSERT INTO health_records
                    (user_id,gender,age,weight,height,activity,goal,bmi,bmr,calories)
                    VALUES(?,?,?,?,?,?,?,?,?,?)""",
                    (session["user_id"], gender, age, weight, height, activity, goal_text, bmi, bmr, calories))
                db.commit()
                db.close()
            result = f"""<div class="results">
            <div class="card center"><p>BMI</p><div class="number">{bmi:.2f}</div><p>{status}</p></div>
            <div class="card center"><p>BMR</p><div class="number">{bmr:.0f}</div><p>kcal/วัน</p></div>
            <div class="card center"><p>แคลอรีเป้าหมาย</p><div class="number">{calories:.0f}</div><p>kcal/วัน</p></div>
            </div>"""
        except (ValueError, KeyError, ZeroDivisionError):
            error = "กรุณากรอกข้อมูลให้ถูกต้อง"
    body = f"""<main class="container"><div class="form-card"><h1 class="center green">คำนวณแคลอรี</h1>
    {f'<div class="message">{error}</div>' if error else ''}
    <form method="post">
    <label>เพศ</label><select name="gender" required><option value="">เลือก</option><option value="male">ชาย</option><option value="female">หญิง</option></select>
    <label>อายุ</label><input type="number" name="age" min="1" max="120" required>
    <label>น้ำหนัก (กก.)</label><input type="number" step="0.1" name="weight" min="1" required>
    <label>ส่วนสูง (ซม.)</label><input type="number" step="0.1" name="height" min="1" required>
    <label>กิจกรรม</label><select name="activity" required><option value="">เลือก</option><option value="1.2">น้อยมาก</option><option value="1.375">1–3 วัน/สัปดาห์</option><option value="1.55">3–5 วัน/สัปดาห์</option><option value="1.725">6–7 วัน/สัปดาห์</option><option value="1.9">หนักมาก</option></select>
    <label>เป้าหมาย</label><select name="goal" required><option value="">เลือก</option><option value="lose">ลดน้ำหนัก</option><option value="maintain">รักษาน้ำหนัก</option><option value="gain">เพิ่มน้ำหนัก</option></select>
    <button class="btn full">คำนวณ</button></form></div>{result}</main>"""
    return page("คำนวณแคลอรี – Calorie Fit", body)


@app.route("/walking", methods=["GET", "POST"])
def walking():
    result = ""
    error = ""
    if request.method == "POST":
        try:
            steps = int(request.form["steps"])
            height = float(request.form["height"])
            gender = request.form["gender"]
            minutes_text = request.form.get("minutes", "").strip()
            minutes = float(minutes_text) if minutes_text else None
            if steps < 0 or height <= 0 or (minutes is not None and minutes <= 0):
                raise ValueError
            stride_cm = height * (0.415 if gender == "male" else 0.413)
            distance_km = (steps * stride_cm) / 100000
            goal_percent = min((steps / 10000) * 100, 100)
            speed_kmh = distance_km / (minutes / 60) if minutes else None
            if "user_id" in session:
                db = get_db()
                db.execute("""INSERT INTO walking_records
                    (user_id,steps,height,gender,minutes,distance_km,speed_kmh,goal_percent)
                    VALUES(?,?,?,?,?,?,?,?)""",
                    (session["user_id"], steps, height, gender, minutes, distance_km, speed_kmh, goal_percent))
                db.commit()
                db.close()
            speed_text = f"{speed_kmh:.2f}" if speed_kmh is not None else "—"
            speed_label = "กม./ชม." if speed_kmh is not None else "กรอกเวลาเพื่อคำนวณ"
            result = f"""<div class="results">
            <div class="card center"><p>ระยะทาง</p><div class="number">{distance_km:.2f}</div><p>กิโลเมตร</p></div>
            <div class="card center"><p>ความยาวก้าว</p><div class="number">{stride_cm:.1f}</div><p>เซนติเมตร</p></div>
            <div class="card center"><p>ความเร็วเฉลี่ย</p><div class="number">{speed_text}</div><p>{speed_label}</p></div>
            </div>
            <div class="card"><h3>เป้าหมาย 10,000 ก้าว</h3>
            <p>วันนี้คุณทำได้ <strong>{steps:,} ก้าว</strong> หรือ {goal_percent:.1f}% ของเป้าหมาย</p>
            <div class="progress"><div style="width:{goal_percent:.1f}%"></div></div></div>
            <div class="note">ระยะทางเป็นค่าประมาณจากส่วนสูงและจำนวนก้าวจริง อุปกรณ์แต่ละชนิดอาจวัดต่างกันเล็กน้อย</div>"""
        except (ValueError, KeyError, ZeroDivisionError):
            error = "กรุณากรอกข้อมูลให้ถูกต้อง"
    body = f"""<main class="container"><section class="walk-layout">
    <div class="illustration">{WALK_SVG}</div>
    <div class="form-card" style="margin:0;max-width:none"><h1 class="center green">คำนวณระยะทางเดิน</h1>
    <p class="center small">ใส่จำนวนก้าวในแต่ละวัน ระบบจะประมาณระยะทางให้</p>
    {f'<div class="message">{error}</div>' if error else ''}
    <form method="post">
    <label>จำนวนก้าววันนี้</label><input type="number" name="steps" min="0" required placeholder="เช่น 8240">
    <label>ส่วนสูง (ซม.)</label><input type="number" name="height" min="1" step="0.1" required placeholder="เช่น 165">
    <label>เพศ</label><select name="gender" required><option value="">เลือก</option><option value="male">ชาย</option><option value="female">หญิง</option></select>
    <label>เวลาที่ใช้เดิน (นาที) — ไม่บังคับ</label><input type="number" name="minutes" min="1" step="0.1" placeholder="เช่น 75">
    <button class="btn full">คำนวณระยะทาง</button></form></div>
    </section>{result}</main>"""
    return page("คำนวณระยะทางเดิน – Calorie Fit", body)


@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    db = get_db()
    health_records = db.execute("SELECT * FROM health_records WHERE user_id=? ORDER BY id DESC LIMIT 10", (session["user_id"],)).fetchall()
    walking_records = db.execute("SELECT * FROM walking_records WHERE user_id=? ORDER BY id DESC LIMIT 10", (session["user_id"],)).fetchall()
    db.close()

    health_rows = "".join(
        f"<tr><td>{r['created_at']}</td><td>{r['weight']:.1f}</td><td>{r['bmi']:.2f}</td><td>{r['calories']:.0f}</td><td>{r['goal']}</td></tr>"
        for r in health_records
    )

    walk_rows = ""
    for r in walking_records:
        speed_text = f"{r['speed_kmh']:.2f}" if r["speed_kmh"] is not None else "—"
        walk_rows += (
            f"<tr><td>{r['created_at']}</td><td>{r['steps']:,}</td>"
            f"<td>{r['distance_km']:.2f}</td><td>{speed_text}</td>"
            f"<td>{r['goal_percent']:.1f}%</td></tr>"
        )

    health_html = f"""<div class="card"><h2>ประวัติสุขภาพ</h2><div class="table-wrap"><table>
    <tr><th>วันที่</th><th>น้ำหนัก</th><th>BMI</th><th>แคลอรี</th><th>เป้าหมาย</th></tr>{health_rows}</table></div></div>""" if health_rows else """<div class="card center"><h2>ยังไม่มีข้อมูลสุขภาพ</h2><a class="btn" href="/calculator">เริ่มคำนวณ</a></div>"""

    walk_html = f"""<div class="card"><h2>ประวัติการเดิน</h2><div class="table-wrap"><table>
    <tr><th>วันที่</th><th>จำนวนก้าว</th><th>ระยะทาง</th><th>ความเร็ว</th><th>เป้าหมาย</th></tr>{walk_rows}</table></div></div>""" if walk_rows else """<div class="card center"><h2>ยังไม่มีข้อมูลการเดิน</h2><a class="btn" href="/walking">เริ่มบันทึกการเดิน</a></div>"""

    body = f"""<main class="container"><section class="welcome">
    <h1>สวัสดี {session['user_name']}</h1><p>ดูประวัติสุขภาพและการเดินของคุณ</p></section>
    <div style="height:22px"></div><div class="grid" style="grid-template-columns:1fr 1fr;padding-bottom:65px">{health_html}{walk_html}</div></main>"""
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
      <url><loc>{base}/walking</loc></url>
      <url><loc>{base}/login</loc></url>
      <url><loc>{base}/register</loc></url>
    </urlset>"""
    return Response(xml, mimetype="application/xml")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
