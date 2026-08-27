"""
main.py
--------
هذا هو ملف تشغيل السيرفر الأساسي (FastAPI).
لتشغيله: uvicorn main:app --reload
"""
import os
import json
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv

import sheets_service as db
from matching_engine import rank_candidates

load_dotenv()

app = FastAPI(title="تطابُق - Tatabuq API", version="1.0.0")

FRONTEND_URL = os.getenv("FRONTEND_URL", "*")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # في الإنتاج غيّريها لرابط الفرونت اند فقط
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ================= Pydantic Models =================

class JobSearchRequest(BaseModel):
    job_title: str
    city: Optional[str] = ""
    work_type: Optional[str] = ""
    years_experience: Optional[float] = 0
    education: Optional[str] = ""
    expected_salary: Optional[float] = 0
    skills: Optional[List[str]] = []
    client_email: Optional[str] = ""
    min_score: Optional[float] = 40


class ContactRequestIn(BaseModel):
    client_email: str
    candidate_id: str
    job_title_searched: str
    match_score: float


class CandidateIn(BaseModel):
    full_name: str
    phone: Optional[str] = ""
    email: Optional[str] = ""
    job_title: str
    city: str
    work_type: Optional[str] = "دوام كامل"
    gender: Optional[str] = ""
    years_experience: float
    education: str
    expected_salary: Optional[float] = 0
    skills: Optional[str] = ""
    languages: Optional[str] = ""
    certificates: Optional[str] = ""
    cv_file_url: Optional[str] = ""
    status: Optional[str] = "متاح"


class CandidateUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    job_title: Optional[str] = None
    city: Optional[str] = None
    work_type: Optional[str] = None
    gender: Optional[str] = None
    years_experience: Optional[float] = None
    education: Optional[str] = None
    expected_salary: Optional[float] = None
    skills: Optional[str] = None
    languages: Optional[str] = None
    certificates: Optional[str] = None
    cv_file_url: Optional[str] = None
    status: Optional[str] = None


class ClientIn(BaseModel):
    company_name: str
    contact_name: str
    email: str
    phone: Optional[str] = ""
    plan: Optional[str] = "الأساسية"


class RequestStatusUpdate(BaseModel):
    status: str  # "معتمد" أو "مرفوض" أو "قيد المراجعة"


def anonymize_candidate(candidate: dict, revealed: bool = False) -> dict:
    """يخفي بيانات المرشح الحساسة قبل موافقة الطلب/الدفع - حماية الخصوصية."""
    safe = {
        "id": candidate.get("id"),
        "display_name": f"مرشح رقم {candidate.get('id')}" if not revealed else candidate.get("full_name"),
        "city": candidate.get("city"),
        "work_type": candidate.get("work_type"),
        "years_experience": candidate.get("years_experience"),
        "education": candidate.get("education"),
        "skills": candidate.get("skills"),
        "languages": candidate.get("languages"),
        "match_score": candidate.get("match_score"),
        "match_breakdown": candidate.get("match_breakdown"),
        "cv_file_url": candidate.get("cv_file_url") if revealed else None,
        "phone": candidate.get("phone") if revealed else None,
        "email": candidate.get("email") if revealed else None,
    }
    return safe


# ================= Endpoints: البحث والمطابقة =================

@app.post("/api/search")
def search_candidates(req: JobSearchRequest):
    """المعادل البرمجي لخطوة (1) و(2) و(3) في وصف المشروع: استقبال طلب + بحث + مطابقة."""
    all_candidates = db.list_candidates()
    job_request = req.model_dump()
    ranked = rank_candidates(job_request, all_candidates, min_score=req.min_score)

    db.log_search(
        client_email=req.client_email,
        job_title=req.job_title,
        city=req.city,
        filters_json=json.dumps(job_request, ensure_ascii=False),
        results_count=len(ranked),
    )

    results = [anonymize_candidate(c, revealed=False) for c in ranked[:50]]
    return {"count": len(results), "results": results}


@app.post("/api/contact-request")
def create_contact_request(req: ContactRequestIn):
    """خطوة (5): طلب بيانات التواصل - يسجل الطلب فقط، لا يفشي البيانات فوراً."""
    result = db.add_request(
        client_email=req.client_email,
        candidate_id=req.candidate_id,
        job_title_searched=req.job_title_searched,
        match_score=req.match_score,
    )
    return {"message": "تم تسجيل طلب التواصل، سيتم إرسال بيانات المرشح بعد اعتماد الطلب", "request": result}


@app.get("/api/contact-request/{request_id}/reveal")
def reveal_candidate_if_approved(request_id: str):
    """يفشي بيانات المرشح فقط إذا كان الطلب معتمداً (بعد الدفع أو موافقة الإدارة)."""
    requests_list = db.list_requests()
    target = next((r for r in requests_list if str(r.get("id")) == str(request_id)), None)
    if not target:
        raise HTTPException(404, "الطلب غير موجود")
    if target.get("status") != "معتمد":
        raise HTTPException(403, "الطلب لم يُعتمد بعد")

    candidates = db.list_candidates()
    candidate = next((c for c in candidates if str(c.get("id")) == str(target.get("candidate_id"))), None)
    if not candidate:
        raise HTTPException(404, "المرشح غير موجود")

    candidate["match_score"] = target.get("match_score")
    return anonymize_candidate(candidate, revealed=True)


# ================= Endpoints: إدارة المرشحين (لوحة التحكم) =================

@app.get("/api/admin/candidates")
def admin_list_candidates():
    return db.list_candidates()


@app.post("/api/admin/candidates")
def admin_add_candidate(candidate: CandidateIn):
    return db.add_candidate(candidate.model_dump())


@app.put("/api/admin/candidates/{candidate_id}")
def admin_update_candidate(candidate_id: str, updates: CandidateUpdate):
    clean_updates = {k: v for k, v in updates.model_dump().items() if v is not None}
    result = db.update_candidate(candidate_id, clean_updates)
    if not result:
        raise HTTPException(404, "المرشح غير موجود")
    return result


@app.delete("/api/admin/candidates/{candidate_id}")
def admin_delete_candidate(candidate_id: str):
    success = db.delete_candidate(candidate_id)
    if not success:
        raise HTTPException(404, "المرشح غير موجود")
    return {"message": "تم حذف المرشح بنجاح"}


# ================= Endpoints: إدارة العملاء =================

@app.get("/api/admin/clients")
def admin_list_clients():
    return db.list_clients()


@app.post("/api/admin/clients")
def admin_add_client(client: ClientIn):
    existing = db.find_client_by_email(client.email)
    if existing:
        raise HTTPException(400, "عميل بهذا البريد الإلكتروني موجود بالفعل")
    return db.add_client(client.model_dump())


# ================= Endpoints: طلبات التواصل (إدارة) =================

@app.get("/api/admin/requests")
def admin_list_requests():
    return db.list_requests()


@app.put("/api/admin/requests/{request_id}/status")
def admin_update_request_status(request_id: str, body: RequestStatusUpdate):
    result = db.update_request_status(request_id, body.status)
    if not result:
        raise HTTPException(404, "الطلب غير موجود")
    return {"message": f"تم تحديث حالة الطلب إلى: {body.status}"}


# ================= Endpoints: التقارير =================

@app.get("/api/admin/reports/summary")
def reports_summary():
    candidates = db.list_candidates()
    clients = db.list_clients()
    requests_list = db.list_requests()
    search_logs = db.get_search_log_ws().get_all_records()

    job_title_counts = {}
    for log in search_logs:
        jt = log.get("job_title", "غير محدد")
        job_title_counts[jt] = job_title_counts.get(jt, 0) + 1
    top_jobs = sorted(job_title_counts.items(), key=lambda x: x[1], reverse=True)[:10]

    return {
        "total_candidates": len(candidates),
        "total_clients": len(clients),
        "total_searches": len(search_logs),
        "total_requests": len(requests_list),
        "pending_requests": len([r for r in requests_list if r.get("status") == "قيد المراجعة"]),
        "approved_requests": len([r for r in requests_list if r.get("status") == "معتمد"]),
        "top_requested_jobs": [{"job_title": j, "count": c} for j, c in top_jobs],
    }


@app.get("/")
def root():
    return {"status": "تطابُق API يعمل بنجاح", "docs": "/docs"}
