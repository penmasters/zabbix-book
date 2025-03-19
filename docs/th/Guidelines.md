# แนวทางการร่วมพัฒนาการ 

## วิธีการร่วมสนับสนุน


- เซ็นเอกสาร [การโอนสิทธิ์](./files/form deed of transfer Book Zabbix.pdf) โดยแนะนำให้เซ็นแบบอิเล็กทรอนิกส์
- คัดลอกโปรเจคไปยังบัญชี Github ของคุณ
- คัดลอก Repository ลงในเครื่องคอมพิวเตอร์ของคุณ

- ติดตั้งซอฟต์แวร์ที่จำเป็นสำหรับ Mkdocs ตรวจสอบวิธีติดตั้งในไฟล์ how-to-install-mkdocs.md ที่โฟลเดอร์หลัก 
  สร้าง Branch ใหม่สำหรับแก้ไข
    - git branch "<ชื่อ branch ของคุณ>"
    - เปลี่ยนไปที่ branch ที่สร้าง:
    - git checkout "<ชื่อ branch ของคุณ>"
- แก้ไขไฟล์ที่ต้องการแก้ไขไฟล์และ Commit การเปลี่ยนแปลง
    - เพิ่มไฟล์ที่แก้ไข:
    - git add <ไฟล์ที่แก้ไข>
- Commit พร้อมใส่ข้อความอธิบาย:
    - git commit -m "ใส่ข้อความ commit ที่มีประโยชน์"
    - กลับไปที่ Branch หลัก
    - เปลี่ยนไปที่ main:
- git checkout main
    - รวมการเปลี่ยนแปลงล่าสุดจาก main:
- git pull origin main
    - รวม Branch ของคุณเข้ากับ Main
    - Merge branch ของคุณ:
- git merge "<ชื่อ branch ของคุณ>"
    - Push การเปลี่ยนแปลง:
- git push
    - ลบ Branch ที่ไม่ใช้งานแล้ว
    - คำสั่งลบ branch:
- git branch -d "<ชื่อ branch ของคุณ>"
    - สร้าง Pull Request
- เพื่อให้เราสามารถทำการ merge ได้ :)
