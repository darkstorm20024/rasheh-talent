from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
import uvicorn

app = FastAPI(title="منصة رشّح - باقات الاشتراكات وشحن الرصيد")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_URL = "postgresql://postgres.sdlvrtzgmerzwfkycswf:Rasheh2026#@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres?sslmode=require"

def get_db():
    return psycopg2.connect(DB_URL, cursor_factory=RealDictCursor)

# تعريف الباقات التجارية للمنصة
PRICING_PLANS = {
    "starter": {"name": "باقة الانطلاق", "credits": 5, "price": 199, "currency": "SAR"},
    "pro": {"name": "باقة الشركات المتقدمة", "credits": 25, "price": 699, "currency": "SAR"},
    "unlimited": {"name": "باقة التوظيف المفتوحة", "credits": 100, "price": 1999, "currency": "SAR"}
}

class BuyCreditsPayload(BaseModel):
    client_email: str
    client_name: str
    client_phone: str
    plan_id: str  # starter, pro, unlimited

class RequestWithCreditsPayload(BaseModel):
    candidate_id: str
    client_email: str

# 1. شحن الرصيد وشراء باقة
@app.post("/api/billing/buy-plan")
def buy_plan(payload: BuyCreditsPayload):
    if payload.plan_id not in PRICING_PLANS:
        raise HTTPException(status_code=400, detail="الباقة المختارة غير متوفرة")

    plan = PRICING_PLANS[payload.plan_id]
    conn = get_db()
    cursor = conn.cursor()

    # تسجيل العميل أو تحديث رصيده
    cursor.execute("""
        INSERT INTO clients (company_name, contact_name, email, phone, credits_balance)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (email) DO UPDATE SET
            credits_balance = clients.credits_balance + EXCLUDED.credits_balance,
            phone = EXCLUDED.phone
        RETURNING id, credits_balance;
    """, (
        payload.client_name, payload.client_name, 
        payload.client_email.strip().lower(), payload.client_phone, 
        plan['credits']
    ))
    client = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()

    return {
        "success": True,
        "message": f"تم تفعيل {plan['name']} بنجاح وإضافة {plan['credits']} سيرة ذاتية إلى رصيدكم!",
        "new_balance": client['credits_balance']
    }

# 2. فحص رصيد العميل الحالي
@app.get("/api/billing/balance/{email}")
def check_balance(email: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT credits_balance, company_name FROM clients WHERE email = %s;", (email.strip().lower(),))
    client = cursor.fetchone()
    cursor.close()
    conn.close()

    if not client:
        return {"credits_balance": 0, "registered": False}
    return {"credits_balance": client['credits_balance'], "registered": True, "company_name": client['company_name']}

# 3. فتح السيرة الذاتية عبر خصم 1 رصيد
@app.post("/api/billing/unlock-candidate")
def unlock_candidate(payload: RequestWithCreditsPayload):
    conn = get_db()
    cursor = conn.cursor()

    # فحص رصيد العميل
    cursor.execute("SELECT id, credits_balance FROM clients WHERE email = %s;", (payload.client_email.strip().lower(),))
    client = cursor.fetchone()

    if not client or client['credits_balance'] < 1:
        cursor.close()
        conn.close()
        return {
            "success": False,
            "error_code": "NO_CREDITS",
            "message": "رصيدك غير كافٍ لفتح بيانات المرشح، يرجى ترقية الباقة."
        }

    # جلب بيانات المرشح
    cursor.execute("SELECT * FROM candidates WHERE id = %s;", (payload.candidate_id,))
    cand = cursor.fetchone()

    # خصم 1 من الرصيد
    new_balance = client['credits_balance'] - 1
    cursor.execute("UPDATE clients SET credits_balance = %s WHERE id = %s;", (new_balance, client['id']))

    # تسجيل الطلب
    cursor.execute("""
        INSERT INTO contact_requests (client_id, candidate_id, status, paid_amount)
        VALUES (%s, %s, 'unlocked', 1.00);
    """, (client['id'], payload.candidate_id))

    conn.commit()
    cursor.close()
    conn.close()

    return {
        "success": True,
        "remaining_credits": new_balance,
        "message": f"تم خصم 1 سيرة ذاتية من رصيدك. الرصيد المتبقي: {new_balance}",
        "candidate": {
            "full_name": cand['full_name'],
            "phone": cand['phone'],
            "email": cand['email'],
            "job_title": cand['job_title'],
            "city": cand['city'],
            "resume_url": cand['resume_url']
        }
    }

if __name__ == "__main__":
    uvicorn.run("billing_api:app", host="127.0.0.1", port=8001, reload=True)
