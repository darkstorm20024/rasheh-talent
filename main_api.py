from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
import json
import os
import uvicorn

app = FastAPI(title="منصة رشّح - المنظومة الكاملة مع بوابات الدفع")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_URL = "postgresql://postgres.sdlvrtzgmerzwfkycswf:Rasheh2026#@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres?sslmode=require"
CMS_FILE = "site_content.json"

ADMIN_CREDENTIALS = {
    "admin@rasheh.com": "Rasheh2026#",
    "admin@gmail.com": "Rasheh2026#"
}

DEFAULT_CONTENT = {
    "video_url": "https://www.youtube.com/embed/dQw4w9WgXcQ",
    "video_title": "كيف توفر منصة رشّح 80% من وقت ومصاريف التوظيف؟",
    "video_desc": "شاهد العرض التوضيحي لمعرفة كيف يقوم محرك الفرز بتحليل المسميات وسنوات الخبرة والمهارات لمطابقة المرشح الأنسب مع شاغرك الوظيفي فوراً.",
    "social_links": {
        "whatsapp": "https://wa.me/966500000000",
        "linkedin": "https://linkedin.com/company/rasheh",
        "twitter": "https://x.com/rasheh_talent",
        "instagram": "https://instagram.com/rasheh_talent"
    },
    "bank_details": {
        "bank_name": "مصرف الراجحي (Al Rajhi Bank)",
        "account_name": "مؤسسة منصة رشح لتقنية المعلومات",
        "iban": "SA0380000000608010167519",
        "account_number": "608010167519"
    },
    "paypal_email": "payments@rasheh.com",
    "testimonials": [
        {
            "id": 1,
            "name": "سلطان القحطاني",
            "role": "الرئيس التنفيذي | شركة الأفق التقنية",
            "rating": 5,
            "comment": "وفرت علينا المنصة عناء الإعلانات الطويلة. قمت بالبحث عن مدير مبيعات بخبرة 8 سنوات ووجدت 4 مرشحين ممتازين وتواصلت معهم في نفس اليوم."
        },
        {
            "id": 2,
            "name": "م. ريم العتيبي",
            "role": "مديرة الموارد البشرية | مؤسسة بناء المستقبل",
            "rating": 5,
            "comment": "دقة المطابقة الذكية ونظام الرصيد ممتاز جداً. كل الكفاءات حقيقية وتم رفع الـ CV والتواصل معهم بكل سلاسة وشفافية."
        },
        {
            "id": 3,
            "name": "خالد الشمري",
            "role": "مؤسس شريك | وكالة التسويق الرقمي",
            "rating": 5,
            "comment": "أفضل منصة SaaS عربية للتوظيف الفوري جربتها حتى الآن، قاعدة بيانات ضخمة ومنظمة والبحث ثنائي اللغة يعمل باحترافية."
        }
    ],
    "news": [
        {
            "id": 1,
            "badge": "تقرير التوظيف 2026",
            "image_url": "https://images.unsplash.com/photo-1551836022-d5d88e9218df?w=600&auto=format&fit=crop&q=60",
            "title": "أكثر 10 تخصصات وإدارات طلباً في الشركات السعودية",
            "desc": "دراسة شاملة وتفصيلية حول رواتب ومؤهلات قطاعات الإدارة والتقنية والمبيعات في السوق الخليجي وكيفية استقطاب أفضل المواهب والكوادر الجاهزة للعمل الفوري."
        },
        {
            "id": 2,
            "badge": "تحديث المنصة",
            "image_url": "https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=600&auto=format&fit=crop&q=60",
            "title": "إطلاق محرك الفرز الذكي ثنائي اللغة (عربي / إنجليزي)",
            "desc": "كيف يساعد نظام الترجمة الآلية في العثور على المرشحين بدقة تامة ومطابقة الكفاءات بغض النظر عن لغة البحث المستخدمة."
        },
        {
            "id": 3,
            "badge": "دليل الشركات",
            "image_url": "https://images.unsplash.com/photo-1497215728101-856f4ea42174?w=600&auto=format&fit=crop&q=60",
            "title": "5 خطوات لاختيار الموظف المناسب وتقليل نسبة التسرب",
            "desc": "طرق فحص المقابلات الوظيفية والمطابقة السلوكية مع بيئة العمل لضمان استقرار الموظف ورفع كفاءة الإنتاج داخل المؤسسة."
        }
    ]
}

def load_content():
    if not os.path.exists(CMS_FILE):
        with open(CMS_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONTENT, f, ensure_ascii=False, indent=2)
        return DEFAULT_CONTENT
    with open(CMS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        if "bank_details" not in data:
            data["bank_details"] = DEFAULT_CONTENT["bank_details"]
        if "paypal_email" not in data:
            data["paypal_email"] = DEFAULT_CONTENT["paypal_email"]
        return data

def save_content(data):
    with open(CMS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_db():
    return psycopg2.connect(DB_URL, cursor_factory=RealDictCursor)

PRICING_PLANS = {
    "starter": {"name": "باقة الانطلاق", "credits": 5, "price": 199, "usd_price": 53},
    "pro": {"name": "باقة الشركات المتقدمة", "credits": 25, "price": 699, "usd_price": 186},
    "unlimited": {"name": "باقة التوظيف المفتوحة", "credits": 100, "price": 1999, "usd_price": 533}
}

class RegisterPayload(BaseModel):
    company_name: str
    contact_name: str
    email: str
    phone: str
    password: str

class LoginPayload(BaseModel):
    email: str
    password: str

class MatchRequest(BaseModel):
    job_title: str
    city: Optional[str] = None
    min_experience: Optional[int] = 0
    skills: List[str] = []

class BankTransferPayload(BaseModel):
    client_email: str
    plan_id: str
    sender_name: str
    bank_name: str
    amount: float

class PayPalSuccessPayload(BaseModel):
    client_email: str
    plan_id: str
    order_id: str

class UnlockPayload(BaseModel):
    candidate_id: str
    client_email: str

# ==================== 1. التوثيق ====================

@app.post("/api/auth/register")
def register_client(payload: RegisterPayload):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM clients WHERE email = %s;", (payload.email.strip().lower(),))
    if cursor.fetchone():
        cursor.close()
        conn.close()
        raise HTTPException(status_code=400, detail="البريد مسجل بالفعل")

    is_admin = payload.email.strip().lower() in ADMIN_CREDENTIALS

    cursor.execute("""
        INSERT INTO clients (company_name, contact_name, email, phone, credits_balance)
        VALUES (%s, %s, %s, %s, 2)
        RETURNING company_name, email, credits_balance;
    """, (payload.company_name, payload.contact_name, payload.email.strip().lower(), payload.phone))
    new_user = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()
    return {
        "success": True, 
        "message": "تم إنشاء الحساب بنجاح!", 
        "user": {
            "company_name": new_user['company_name'],
            "email": new_user['email'],
            "credits_balance": new_user['credits_balance'],
            "is_admin": is_admin
        }
    }

@app.post("/api/auth/login")
def login_client(payload: LoginPayload):
    email_clean = payload.email.strip().lower()

    if email_clean in ADMIN_CREDENTIALS:
        if payload.password == ADMIN_CREDENTIALS[email_clean]:
            return {
                "success": True,
                "message": "مرحباً بك يا مدير المنصة!",
                "user": {
                    "company_name": "إدارة منصة رشّح",
                    "email": email_clean,
                    "credits_balance": 9999,
                    "is_admin": True
                }
            }
        else:
            raise HTTPException(status_code=401, detail="كلمة مرور الإدارة غير صحيحة")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT company_name, email, phone, credits_balance FROM clients WHERE email = %s;", (email_clean,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if not user:
        raise HTTPException(status_code=404, detail="البريد غير مسجل، يرجى إنشاء حساب جديد")

    return {
        "success": True, 
        "message": f"أهلاً بك {user['company_name']}", 
        "user": {
            "company_name": user['company_name'],
            "email": user['email'],
            "phone": user['phone'],
            "credits_balance": user['credits_balance'],
            "is_admin": False
        }
    }

# ==================== 2. بوابات الدفع (PayPal + التحويل البنكي السعودي) ====================

@app.post("/api/billing/paypal-success")
def paypal_payment_success(payload: PayPalSuccessPayload):
    """تفعيل الرصيد الفوري بعد الدفع بـ PayPal"""
    plan = PRICING_PLANS.get(payload.plan_id)
    if not plan:
        raise HTTPException(status_code=400, detail="الباقة غير معروفة")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE clients 
        SET credits_balance = credits_balance + %s 
        WHERE email = %s 
        RETURNING credits_balance;
    """, (plan['credits'], payload.client_email.strip().lower()))
    res = cursor.fetchone()

    # تسجيل المعاملة
    cursor.execute("""
        INSERT INTO contact_requests (client_id, candidate_id, status, paid_amount)
        SELECT id, gen_random_uuid(), 'paypal_paid', %s FROM clients WHERE email = %s;
    """, (plan['price'], payload.client_email.strip().lower()))

    conn.commit()
    cursor.close()
    conn.close()

    return {
        "success": True, 
        "message": f"تم استلام الدفعة عبر PayPal بنجاح وتفعيل {plan['name']} (+{plan['credits']} CV)!", 
        "new_balance": res['credits_balance']
    }

@app.post("/api/billing/bank-transfer")
def submit_bank_transfer(payload: BankTransferPayload):
    """تسجيل إشعار التحويل البنكي السعودي لمراجعته واعتماده"""
    plan = PRICING_PLANS.get(payload.plan_id)
    if not plan:
        raise HTTPException(status_code=400, detail="الباقة غير معروفة")

    conn = get_db()
    cursor = conn.cursor()
    
    # تفعيل فوري أو تسجيل كطلب قيد المراجعة (هنا نقوم بالتفعيل مع تسجيل بيانات المحول)
    cursor.execute("""
        UPDATE clients 
        SET credits_balance = credits_balance + %s 
        WHERE email = %s 
        RETURNING credits_balance, id;
    """, (plan['credits'], payload.client_email.strip().lower()))
    client = cursor.fetchone()

    cursor.execute("""
        INSERT INTO contact_requests (client_id, candidate_id, status, paid_amount)
        VALUES (%s, gen_random_uuid(), %s, %s);
    """, (client['id'], f"تحويل بنكي - {payload.bank_name} ({payload.sender_name})", plan['price']))

    conn.commit()
    cursor.close()
    conn.close()

    return {
        "success": True,
        "message": f"تم استلام إشعار التحويل البنكي لحساب ({payload.bank_name}) وتفعيل الباقة فوراً! رصيدك: {client['credits_balance']} CV",
        "new_balance": client['credits_balance']
    }

@app.post("/api/cms/update-payment-gateways")
def update_payment_gateways(payload: dict):
    """تعديل بيانات الحساب البنكي السعودي والـ PayPal من لوحة الإدارة"""
    content = load_content()
    if "bank_details" in payload:
        content["bank_details"] = payload["bank_details"]
    if "paypal_email" in payload:
        content["paypal_email"] = payload["paypal_email"]
    save_content(content)
    return {"success": True, "message": "تم تحديث بيانات الحساب البنكي والـ PayPal بنجاح!"}

# ==================== 3. البحث والمطابقة ====================

TRANSLATION_MAP = {
    "business administration": ["business administration", "إدارة أعمال", "ادارة اعمال", "business", "management", "specialist"],
    "إدارة أعمال": ["business administration", "إدارة أعمال", "ادارة اعمال", "business", "management"],
    "accounting": ["accounting", "accountant", "محاسبة", "محاسب", "مالية"],
    "محاسب": ["accounting", "accountant", "محاسبة", "محاسب", "مالية"],
    "sales": ["sales", "مبيعات", "مسؤول مبيعات", "ممثل مبيعات"],
    "marketing": ["marketing", "تسويق", "مسوق"],
    "hr": ["hr", "human resources", "موارد بشرية", "شؤون موظفين"],
    "software": ["software", "developer", "برمجة", "مطور", "مبرمج"]
}

def calculate_smart_match(candidate: dict, criteria: MatchRequest) -> tuple[int, bool]:
    score = 0.0
    cand_combined = f"{str(candidate.get('job_title') or '')} {str(candidate.get('education') or '')}".lower()
    req_title = criteria.job_title.lower().strip()

    cand_exp = candidate.get('years_of_experience') or 0
    if criteria.min_experience and criteria.min_experience > 0:
        if cand_exp < criteria.min_experience:
            return 0, False

    search_keywords = [req_title]
    for key, synonyms in TRANSLATION_MAP.items():
        if key in req_title:
            search_keywords.extend(synonyms)
            break
        for syn in synonyms:
            if syn in req_title:
                search_keywords.extend(synonyms)
                break
    search_keywords = list(set([k.lower() for k in search_keywords]))

    title_matched = False
    for kw in search_keywords:
        if kw in cand_combined or any(w in cand_combined for w in kw.split() if len(w) > 2):
            score += 50.0
            title_matched = True
            break

    if not title_matched:
        return 0, False

    score += 25.0
    cand_city = str(candidate.get('city') or '').lower()
    if criteria.city and criteria.city.lower() in cand_city:
        score += 25.0
    else:
        score += 25.0

    return min(100, int(round(score))), True

@app.post("/api/match-candidates")
def match_candidates(req: MatchRequest):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM candidates WHERE status = 'active';")
        candidates = cursor.fetchall()
        cursor.close()
        conn.close()

        results = []
        for c in candidates:
            score, is_match = calculate_smart_match(c, req)
            if is_match and score >= 40:
                results.append({
                    "candidate_id": str(c['id']),
                    "full_name": c['full_name'],
                    "job_title": c['job_title'],
                    "city": c['city'],
                    "years_of_experience": c['years_of_experience'],
                    "education": c['education'],
                    "gender": c['gender'],
                    "match_percentage": score
                })

        results.sort(key=lambda x: (x['match_percentage'], x['years_of_experience']), reverse=True)
        return {"total": len(results), "candidates": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/billing/unlock-candidate")
def unlock_candidate(payload: UnlockPayload):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, credits_balance FROM clients WHERE email = %s;", (payload.client_email.strip().lower(),))
    client = cursor.fetchone()

    if not client or client['credits_balance'] < 1:
        cursor.close()
        conn.close()
        return {"success": False, "error_code": "NO_CREDITS", "message": "رصيد شركتك غير كافٍ."}

    cursor.execute("SELECT * FROM candidates WHERE id = %s;", (payload.candidate_id,))
    cand = cursor.fetchone()

    new_balance = client['credits_balance'] - 1
    cursor.execute("UPDATE clients SET credits_balance = %s WHERE id = %s;", (new_balance, client['id']))
    cursor.execute("INSERT INTO contact_requests (client_id, candidate_id, status) VALUES (%s, %s, 'unlocked');", (client['id'], payload.candidate_id))
    conn.commit()
    cursor.close()
    conn.close()

    return {
        "success": True,
        "new_balance": new_balance,
        "candidate": {
            "full_name": cand['full_name'],
            "phone": cand['phone'] or "غير متوفر",
            "email": cand['email'],
            "resume_url": cand['resume_url'] or "تم توفير الملف"
        }
    }

# ==================== 4. لوحة الإدارة ====================

@app.get("/api/admin/candidates")
def get_admin_candidates(limit: int = 100):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, full_name, job_title, city, years_of_experience, education, phone, email, resume_url
        FROM candidates 
        ORDER BY years_of_experience DESC, full_name ASC 
        LIMIT %s;
    """, (limit,))
    candidates = cursor.fetchall()
    cursor.close()
    conn.close()
    return {"candidates": candidates, "count": len(candidates)}

@app.get("/api/admin/clients")
def get_admin_clients():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, company_name, contact_name, email, phone, credits_balance, created_at
        FROM clients 
        ORDER BY created_at DESC;
    """)
    clients = cursor.fetchall()
    cursor.close()
    conn.close()
    return {"clients": clients, "count": len(clients)}

@app.get("/api/admin/stats")
def get_admin_stats():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as total FROM candidates;")
    total_cand = cursor.fetchone()['total']
    cursor.execute("SELECT COUNT(*) as total_req FROM contact_requests;")
    total_req = cursor.fetchone()['total_req']
    cursor.execute("SELECT COUNT(*) as total_clients FROM clients;")
    total_clients = cursor.fetchone()['total_clients']
    cursor.close()
    conn.close()
    return {"total_candidates": total_cand, "total_requests": total_req, "total_clients": total_clients}

@app.get("/api/cms/content")
def get_site_content():
    return load_content()

@app.post("/api/cms/update-socials")
def update_socials(payload: dict):
    content = load_content()
    content['social_links'] = payload
    save_content(content)
    return {"success": True, "message": "تم تحديث روابط السوشيال ميديا بنجاح!"}

@app.post("/api/cms/update-video")
def update_video(payload: dict):
    content = load_content()
    content['video_url'] = payload.get('video_url', content['video_url'])
    content['video_title'] = payload.get('video_title', content['video_title'])
    content['video_desc'] = payload.get('video_desc', content['video_desc'])
    save_content(content)
    return {"success": True, "message": "تم تحديث الفيديو بنجاح!"}

@app.post("/api/cms/add-testimonial")
def add_testimonial(payload: dict):
    content = load_content()
    new_t = {
        "id": int(len(content['testimonials']) + 1),
        "name": payload.get('name', 'عميل موثوق'),
        "role": payload.get('role', 'صاحب عمل'),
        "rating": 5,
        "comment": payload.get('comment', '')
    }
    content['testimonials'].insert(0, new_t)
    save_content(content)
    return {"success": True, "message": "تمت إضافة الرأي بنجاح!"}

@app.post("/api/cms/add-news")
def add_news(payload: dict):
    content = load_content()
    default_img = "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=600&auto=format&fit=crop&q=60"
    new_n = {
        "id": int(len(content['news']) + 1),
        "badge": payload.get('badge', 'تقرير وإحصائيات'),
        "image_url": payload.get('image_url') or default_img,
        "title": payload.get('title', ''),
        "desc": payload.get('desc', '')
    }
    content['news'].insert(0, new_n)
    save_content(content)
    return {"success": True, "message": "تم نشر المقال بنجاح!"}

if __name__ == "__main__":
    uvicorn.run("main_api:app", host="127.0.0.1", port=8000, reload=True)
