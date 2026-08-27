import os
import pandas as pd
import psycopg2
from psycopg2.extras import execute_batch

# إعدادات الاتصال بقاعدة البيانات (يمكنك وضع الرابط من Supabase أو Neon)
DB_CONNECTION = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/recruitment_db")

def clean_skills(skills_raw):
    """تحويل المهارات من نص مفصول بفواصل إلى قائمة نظيفة"""
    if pd.isna(skills_raw):
        return []
    if isinstance(skills_raw, list):
        return skills_raw
    return [s.strip().lower() for s in str(skills_raw).split(",") if s.strip()]

def import_candidates(csv_or_excel_path):
    print(f"[*] جاري قراءة الملف: {csv_or_excel_path}")
    
    if csv_or_excel_path.endswith('.csv'):
        df = pd.read_csv(csv_or_excel_path)
    else:
        df = pd.read_excel(csv_or_excel_path)
        
    print(f"[*] تم العثور على {len(df)} مرشح.")

    # تجهيز وتنظيف البيانات
    candidates_to_insert = []
    for _, row in df.iterrows():
        full_name = str(row.get('Name', '') or row.get('الاسم', '')).strip()
        first_name = full_name.split()[0] if full_name else 'مرشح'
        
        candidate_data = (
            full_name,
            first_name,
            str(row.get('Email', '') or row.get('البريد', '')).strip().lower(),
            str(row.get('Phone', '') or row.get('الهاتف', '')).strip(),
            str(row.get('Job Title', '') or row.get('المسمى الوظيفي', '')).strip(),
            str(row.get('City', '') or row.get('المدينة', '')).strip(),
            str(row.get('Work Type', 'full_time') or row.get('نوع العمل', 'full_time')).strip(),
            str(row.get('Gender', '') or row.get('الجنس', '')).strip(),
            int(row.get('Experience', 0) or row.get('سنوات الخبرة', 0) or 0),
            str(row.get('Education', '') or row.get('المؤهل', '')).strip(),
            float(row.get('Expected Salary', 0) or row.get('الراتب المتوقع', 0) or 0),
            clean_skills(row.get('Skills') or row.get('المهارات')),
            str(row.get('Resume URL', '') or row.get('رابط السيرة الذاتية', '')).strip()
        )
        candidates_to_insert.append(candidate_data)

    # الإدخال السريع لقاعدة البيانات
    conn = psycopg2.connect(DB_CONNECTION)
    cursor = conn.cursor()

    query = """
    INSERT INTO candidates (
        full_name, first_name, email, phone, job_title, city, 
        work_type, gender, years_of_experience, education, 
        expected_salary, skills, resume_url
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (email) DO NOTHING;
    """

    print("[*] جاري رفع البيانات إلى قاعدة البيانات...")
    execute_batch(cursor, query, candidates_to_insert, page_size=500)
    conn.commit()
    cursor.close()
    conn.close()

    print("[✓] تم استيراد جميع المرشحين بنجاح!")

if __name__ == "__main__":
    # ضع اسم الملف المصدر من Google Sheet بعد تحميله كـ CSV/Excel
    import_candidates("candidates.csv")
