-- ==============================================================================
-- 1. Candidates Table (جدول المرشحين)
-- ==============================================================================
CREATE TABLE candidates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL, -- للاستعراض للعميل للحفاظ على الخصوصية
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(50),
    job_title VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL,
    work_type VARCHAR(50) NOT NULL, -- full_time, part_time, remote
    gender VARCHAR(20),
    years_of_experience INT DEFAULT 0,
    education VARCHAR(255),
    expected_salary NUMERIC(12, 2),
    skills TEXT[] DEFAULT '{}', -- مصفوفة المهارات
    resume_url TEXT,
    raw_resume_text TEXT,
    status VARCHAR(50) DEFAULT 'active', -- active, hired, inactive
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ==============================================================================
-- 2. Clients Table (جدول الشركات / أصحاب العمل)
-- ==============================================================================
CREATE TABLE clients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_name VARCHAR(255) NOT NULL,
    contact_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(50),
    credits_balance INT DEFAULT 0, -- رصيد فتح السير الذاتية والتواصل
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ==============================================================================
-- 3. Search Queries Log (سجل عمليات البحث)
-- ==============================================================================
CREATE TABLE search_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID REFERENCES clients(id) ON DELETE SET NULL,
    job_title VARCHAR(255),
    city VARCHAR(100),
    work_type VARCHAR(50),
    min_experience INT,
    expected_salary NUMERIC(12, 2),
    skills_requested TEXT[],
    results_count INT DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ==============================================================================
-- 4. Contact Requests & Purchases (طلبات التواصل والتحميل)
-- ==============================================================================
CREATE TABLE contact_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    candidate_id UUID NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
    status VARCHAR(50) DEFAULT 'pending', -- pending, approved, rejected, paid
    paid_amount NUMERIC(10, 2) DEFAULT 0.00,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- الفهارس لتحسين سرعة البحث
CREATE INDEX idx_candidates_job_title ON candidates (job_title);
CREATE INDEX idx_candidates_city ON candidates (city);
CREATE INDEX idx_candidates_experience ON candidates (years_of_experience);
