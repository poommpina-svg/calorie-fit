CALORIE FIT — ชุดพร้อมนำขึ้นออนไลน์

ไฟล์สำคัญ:
- app.py                ตัวเว็บไซต์ทั้งหมด
- requirements.txt     รายการแพ็กเกจ
- render.yaml           ตั้งค่า Render อัตโนมัติ
- Procfile              คำสั่งเปิดเว็บ
- .gitignore            ป้องกันไฟล์ที่ไม่ควรอัปโหลด

วิธีทดสอบในเครื่อง:
1) เปิด Command Prompt ในโฟลเดอร์นี้
2) พิมพ์: py -m pip install -r requirements.txt
3) พิมพ์: py app.py
4) เปิด http://127.0.0.1:5000

วิธีนำขึ้นออนไลน์:
1) อัปโหลดไฟล์ทั้งหมดในโฟลเดอร์นี้ขึ้น GitHub repository
2) เข้า Render แล้วเลือก New > Blueprint
3) เชื่อม GitHub repository นี้
4) กด Apply ระบบจะอ่าน render.yaml และสร้างเว็บให้
5) เมื่อเสร็จจะได้ลิงก์ https://ชื่อเว็บ.onrender.com

หมายเหตุสำคัญ:
รุ่นนี้ใช้ SQLite เหมาะกับการทดลองและนำเสนอ
บริการฟรีของ Render อาจลบข้อมูลในไฟล์ฐานข้อมูลเมื่อระบบสร้าง instance ใหม่
หากเปิดให้บริการจริงและต้องเก็บสมาชิกถาวร ควรเปลี่ยนเป็นฐานข้อมูล PostgreSQL แบบถาวร

การให้ Google พบเว็บไซต์:
- เว็บมี robots.txt และ sitemap.xml พร้อมแล้ว
- นำ URL เว็บไปเพิ่มใน Google Search Console
- ส่ง sitemap ที่: https://ชื่อเว็บของคุณ/sitemap.xml
