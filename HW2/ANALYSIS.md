# วิเคราะห์เครือข่ายโดเมน MemeTracker

## ข้อมูลที่ใช้

ดึงจาก `quotes_2009-04.txt.gz` (SNAP MemeTracker) ตัวอย่างขนาด ~400MB (26.8
ล้านบรรทัด) แปลง P→L เป็นเอดจ์ระดับโดเมน ได้ 618,979 เอดจ์ / 323,793 โดเมน
แล้วคัดเฉพาะ **300 โดเมนที่มี weighted degree สูงสุด** มาสร้างกราฟ (แนวทางเดียว
กับ SET50 ใน HW1) เหลือ **291 โดเมน เชื่อมกันด้วย 2,160 เส้น** — คำนวณจริงด้วย
Neo4j GDS ทั้งหมด (ดู `cypher/`)

## แต่ละ metric ชี้อะไรต่างกัน

| Metric | Top domains | ความหมาย |
|---|---|---|
| **Degree** | golivewire.com, mashget.com, articlesbase.com | **Hub** — โพสต์ลิงก์ออกเยอะ (blog/aggregator) ส่วน wikipedia.org, news.google.com มี degree=0 เพราะไม่เคยเป็น "ต้นโพสต์" ในข้อมูลนี้ ถูกอ้างอิงอย่างเดียว |
| **Betweenness** | us.rd.yahoo.com, tinyurl.com | **Bridge** — บริการ redirect/ย่อลิงก์ เป็นสะพานเชื่อมชุมชนต่างกลุ่มเข้าด้วยกันจริง ๆ |
| **Closeness** | หลายโดเมนคะแนน = 1.0 | GDS normalize ตามขนาด component ของตัวเอง กลุ่มเล็กที่เชื่อมถึงกันหมดจึงได้เต็ม ไม่ได้แปลว่าสำคัญระดับกราฟทั้งหมด |
| **Eigenvector** | slickdeals.net ↔ forums.slickdeals.net | **ไม่ลู่เข้า** แม้ 1,000 รอบ (`didConverge=false`) เพราะกราฟมีทิศทาง+มี dangling node ค่าจึงกระจุกที่คู่ที่อ้างกันเอง — นี่คือปัญหาที่ PageRank (มี damping factor) ถูกออกแบบมาแก้ |
| **PageRank** | news.google.com, en.wikipedia.org, youtube.com, bbc.co.uk | **Authority** — ลู่เข้าใน 87 รอบ ได้เว็บอ้างอิง/สื่อหลักที่ถูกอ้างถึงบ่อยที่สุด ตรงกับความจริงในปี 2009 |
| **Bridges** | 53 เส้น เช่น en.wikipedia.org–marvel.wikia.com | เส้นที่ถ้าตัดออกกราฟจะขาดออกจากกัน สอดคล้องกับผล betweenness |

## Louvain community

**42 ชุมชน, modularity = 0.9054** (สูงมาก = กราฟแบ่งกลุ่มชัดเจน) โดยแบ่งตาม
**ภาษา/ภูมิภาค** เป็นหลัก มากกว่าหัวข้อเนื้อหา:

- 🇯🇵 ญี่ปุ่น: hatena, livedoor, amazon.co.jp
- 🇩🇪 เยอรมัน: bild.de, focus.de, google.de
- 🇧🇷 บราซิล: globo.com, globoesporte.com
- Craigslist: มิเรอร์ตามเมือง (newyork/sfbay/boston/...)
- สื่อภาษาอังกฤษหลัก: google news, wikipedia, bbc, nytimes, cnn

## สรุป

- **Hub** (degree) = ใครโพสต์ลิงก์ออกเยอะ
- **Bridge** (betweenness/bridges) = ใครเชื่อมชุมชนที่แยกกันอยู่เข้าด้วยกัน
- **Authority** (PageRank) = ใครถูกอ้างอิงจากแหล่งที่สำคัญ

ไม่มี metric ใด metric เดียวบอกครบทุกมิติ — ต้องดูร่วมกันถึงจะเห็นภาพเต็มของ
เครือข่าย
