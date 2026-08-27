import os
import re
import time
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

# 1. رابط قاعدة البيانات - منفذ 6543 (Transaction Pooler المخصص للرفع السحابي)
# استبدل كلمة المرور مكان [YOUR-PASSWORD]
DB_CONNECTION = "postgresql://postgres.sdlvrtzgmerzwfkycswf:Rasheh2026#@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres?sslmode=require"

COLUMN_MAPPINGS = {
    'full_name': ['name', 'full name', 'الاسم', 'اسم المرشح', 'الاسم الكامل', 'اسم الموظف'],
    'email': ['email', 'e-mail', 'البريد', 'البريد الالكتروني', 'الايميل'],
    'phone': ['phone', 'mobile', 'telephone', 'الهاتف', 'الجوال', 'رقم الهاتف', 'الموبايل'],
    'job_title': ['job title', 'title', 'position', 'المسمى الوظيفي', 'الوظيفة', 'المسمى'],
    'city': ['city', 'location', 'المدينة', 'الموقع', 'مكان الاقامة'],
    'work_type': ['work type', 'job type', 'نوع العمل', 'نوع الدوام'],
    'gender': ['gender', 'sex', 'الجنس', 'النوع'],
    'years_of_experience': ['experience', 'years of experience', 'exp', 'الخبرة', 'سنوات الخبرة'],
    'education': ['education', 'degree', 'المؤهل', 'المؤهل العلمي', 'الدرجة العلمية'],
    'expected_salary': ['salary', 'expected salary', 'الراتب', 'الراتب المتوقع'],
    'skills': ['skills', 'key skills', 'المهارات', 'المهارات المفتاحية'],
    'resume_url': ['resume', 'cv', 'resume url', 'cv url', 'السيرة الذاتية', 'رابط السيرة الذاتية', 'ملف cv']
}

def find_column(df_columns, possible_names):
    for col in df_columns:
        clean_col = str(col).strip().lower()
        if clean_col in possible_names:
            return col
    return None

def clean_skills(raw_skills):
    if pd.isna(raw_skills):
        return []
    skills_list = re.split(r'[,،؛\n]+', str(raw_skills))
    return [s.strip() for s in skills_list if s.strip()]

def clean_number(val, default=0):
    if pd.isna(val):
        return default
    nums = re.findall(r'\d+', str(val))
    return int(nums[0]) if nums else default

def upload_excel_to_supabase(file_path):
    print(f"[*] جاري قراءة ملف الإكسيل: {file_path}")
    
    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
    else:
        df = pd.read_excel(file_path)

    print(f"[*] إجمالي الصفوف المكتشفة: {len(df)} مرشح.")

    matched_cols = {}
    for standard_key, aliases in COLUMN_MAPPINGS.items():
        matched_cols[standard_key] = find_column(df.columns, aliases)

    candidates = []

    for idx, row in df.iterrows():
        name_col = matched_cols['full_name']
        full_name = str(row[name_col]).strip() if name_col and pd.notna(row[name_col]) else f"مرشح_{idx+1}"
        first_name = full_name.split()[0] if full_name else "مرشح"

        email_col = matched_cols['email']
        if email_col and pd.notna(row[email_col]) and '@' in str(row[email_col]):
            email = str(row[email_col]).strip().lower()
        else:
            email = f"cand_{idx+1}_{int(time.time())}@rasheh.local"

        phone_col = matched_cols['phone']
        phone = str(row[phone_col]).strip() if phone_col and pd.notna(row[phone_col]) else None

        job_col = matched_cols['job_title']
        job_title = str(row[job_col]).strip() if job_col and pd.notna(row[job_col]) else "عام"

        city_col = matched_cols['city']
        city = str(row[city_col]).strip() if city_col and pd.notna(row[city_col]) else "غير محدد"

        work_type_col = matched_cols['work_type']
        work_type = str(row[work_type_col]).strip() if work_type_col and pd.notna(row[work_type_col]) else "full_time"

        gender_col = matched_cols['gender']
        gender = str(row[gender_col]).strip() if gender_col and pd.notna(row[gender_col]) else None

        exp_col = matched_cols['years_of_experience']
        years_exp = clean_number(row[exp_col]) if exp_col else 0

        edu_col = matched_cols['education']
        education = str(row[edu_col]).strip() if edu_col and pd.notna(row[edu_col]) else "غير محدد"

        salary_col = matched_cols['expected_salary']
        salary = clean_number(row[salary_col]) if salary_col else 0

        skills_col = matched_cols['skills']
        skills = clean_skills(row[skills_col]) if skills_col else []

        resume_col = matched_cols['resume_url']
        resume_url = str(row[resume_col]).strip() if resume_col and pd.notna(row[resume_col]) else None

        candidates.append((
            full_name, first_name, email, phone, job_title, 
            city, work_type, gender, years_exp, education, 
            salary, skills, resume_url
        ))

    print(f"[*] تم تجهيز {len(candidates)} سجل للرفع...")
    print("[*] جاري فتح الاتصال بـ Supabase عبر منفذ الـ Pooler (6543)...")

    conn = psycopg2.connect(DB_CONNECTION)
    cursor = conn.cursor()
    print("[✓] تم الاتصال بنجاح!")

    query = """
    INSERT INTO candidates (
        full_name, first_name, email, phone, job_title, 
        city, work_type, gender, years_of_experience, education, 
        expected_salary, skills, resume_url
    ) VALUES %s
    ON CONFLICT (email) DO UPDATE SET
        job_title = EXCLUDED.job_title,
        city = EXCLUDED.city,
        skills = EXCLUDED.skills,
        updated_at = NOW();
    """

    # استخدام دفعات صغيرة سريعة (100 في كل دفعة) متوافقة مع Supabase PgBouncer
    batch_size = 100
    total_batches = (len(candidates) + batch_size - 1) // batch_size

    for i in range(0, len(candidates), batch_size):
        batch = candidates[i:i + batch_size]
        execute_values(cursor, query, batch)
        conn.commit()
        batch_num = (i // batch_size) + 1
        print(f"[*] تم رفع الدفعة ({batch_num}/{total_batches}) - الإجمالي المرفوع: {min(i + batch_size, len(candidates))} مرشح")

    cursor.close()
    conn.close()

    print(f"\n=======================================================")
    print(f"[✓] مبروك! تم رفع كامل قاعدة البيانات ({len(candidates)} مرشح) بنجاح تام!")
    print(f"=======================================================\n")

if __name__ == "__main__":
    EXCEL_FILE = "cvs.xlsx"
    upload_excel_to_supabase(EXCEL_FILE)
