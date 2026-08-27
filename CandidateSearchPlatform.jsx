import React, { useState } from 'react';
import { Search, MapPin, Briefcase, Award, CheckCircle, Download, Send } from 'lucide-react';

export default function CandidateSearchPlatform() {
  const [formData, setFormData] = useState({
    job_title: 'مطور React',
    city: 'الرياض',
    work_type: 'full_time',
    min_experience: 3,
    max_salary: 15000,
    skills: 'React, TypeScript, Tailwind'
  });

  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState([
    {
      candidate_id: "cand-001",
      first_name: "أحمد",
      job_title: "مطور واجهات أمامية أول (Senior React Developer)",
      city: "الرياض",
      years_of_experience: 5,
      education: "بكالوريوس علوم حاسب",
      match_percentage: 95,
      resume_url: "#"
    },
    {
      candidate_id: "cand-002",
      first_name: "سارة",
      job_title: "مطورة Frontend & React",
      city: "الرياض",
      years_of_experience: 3,
      education: "بكالوريوس تقنية معلومات",
      match_percentage: 91,
      resume_url: "#"
    },
    {
      candidate_id: "cand-003",
      first_name: "محمود",
      job_title: "مطور Full Stack (React / Node)",
      city: "جدة",
      years_of_experience: 4,
      education: "هندسة برمجيات",
      match_percentage: 84,
      resume_url: "#"
    }
  ]);

  const handleSearch = (e) => {
    e.preventDefault();
    setLoading(true);
    // محاكاة استدعاء API الـ Backend
    setTimeout(() => {
      setLoading(false);
    }, 600);
  };

  return (
    <div className="min-h-screen bg-slate-50 font-sans text-slate-800" dir="rtl">
      {/* رأس الصفحة والهوية */}
      <header className="bg-white border-b border-slate-200 py-4 px-6 sticky top-0 z-10 shadow-sm flex justify-between items-center">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-indigo-600 flex items-center justify-center text-white font-bold text-xl shadow-indigo-100 shadow-lg">
            S
          </div>
          <div>
            <h1 className="text-xl font-bold text-slate-900">سيرة تك | SeeraTech</h1>
            <p className="text-xs text-slate-500">منصة المطابقة الفورية والذكية للمرشحين</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-xs bg-indigo-50 text-indigo-700 px-3 py-1.5 rounded-full font-medium">
            رصيدك: 12 سيرة ذاتية
          </span>
          <button className="bg-indigo-600 hover:bg-indigo-700 text-white text-sm px-4 py-2 rounded-lg transition-all">
            لوحة التحكم
          </button>
        </div>
      </header>

      {/* المحتوى الرئيسي */}
      <main className="max-w-7xl mx-auto px-4 py-8 grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* نموذج البحث واستقبال متطلبات الشركة */}
        <section className="lg:col-span-4 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm h-fit">
          <h2 className="text-lg font-bold text-slate-900 mb-4 flex items-center gap-2">
            <Search className="w-5 h-5 text-indigo-600" />
            تحديد متطلبات الوظيفة
          </h2>

          <form onSubmit={handleSearch} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">المسمى الوظيفي المطلوب</label>
              <input
                type="text"
                value={formData.job_title}
                onChange={(e) => setFormData({...formData, job_title: e.target.value})}
                className="w-full text-sm px-3.5 py-2.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-500 outline-none"
                placeholder="مثال: مطور برمجيات، محاسب..."
                required
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">المدينة</label>
                <input
                  type="text"
                  value={formData.city}
                  onChange={(e) => setFormData({...formData, city: e.target.value})}
                  className="w-full text-sm px-3.5 py-2.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-500 outline-none"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">نوع العمل</label>
                <select
                  value={formData.work_type}
                  onChange={(e) => setFormData({...formData, work_type: e.target.value})}
                  className="w-full text-sm px-3.5 py-2.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-500 outline-none bg-white"
                >
                  <option value="full_time">دوام كامل</option>
                  <option value="part_time">دوام جزئي</option>
                  <option value="remote">عن بعد</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">الخبرة (سنوات)</label>
                <input
                  type="number"
                  value={formData.min_experience}
                  onChange={(e) => setFormData({...formData, min_experience: Number(e.target.value)})}
                  className="w-full text-sm px-3.5 py-2.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-500 outline-none"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">الحد الأقصى للراتب</label>
                <input
                  type="number"
                  value={formData.max_salary}
                  onChange={(e) => setFormData({...formData, max_salary: Number(e.target.value)})}
                  className="w-full text-sm px-3.5 py-2.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-500 outline-none"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">المهارات المفتاحية (مفصولة بفواصل)</label>
              <input
                type="text"
                value={formData.skills}
                onChange={(e) => setFormData({...formData, skills: e.target.value})}
                className="w-full text-sm px-3.5 py-2.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-500 outline-none"
                placeholder="React, SQL, Excel..."
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-3 rounded-xl transition-all shadow-md shadow-indigo-100 flex items-center justify-center gap-2"
            >
              {loading ? "جاري المطابقة بالذكاء الاصطناعي..." : "بحث وتوليد المرشحين فوراً"}
            </button>
          </form>
        </section>

        {/* عرض نتائج المطابقة والترشيح */}
        <section className="lg:col-span-8 space-y-4">
          <div className="flex justify-between items-center mb-2">
            <h3 className="font-bold text-slate-900 text-lg">المرشحون المطابقون ({results.length})</h3>
            <span className="text-xs text-slate-500">مرتبة تلقائياً بنسبة التطابق الأعلى</span>
          </div>

          {results.map((cand, idx) => (
            <div key={idx} className="bg-white border border-slate-200 rounded-2xl p-5 hover:shadow-md transition-shadow relative overflow-hidden">
              {/* شريط نسبة التطابق */}
              <div className="flex justify-between items-start">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-bold text-slate-900 text-base">المرشح: {cand.first_name} (معرف: {cand.candidate_id})</span>
                    <span className="bg-emerald-50 text-emerald-700 text-xs px-2.5 py-0.5 rounded-full font-bold flex items-center gap-1">
                      <CheckCircle className="w-3.5 h-3.5" />
                      تطابق {cand.match_percentage}%
                    </span>
                  </div>
                  <h4 className="text-indigo-600 font-medium text-sm">{cand.job_title}</h4>
                </div>
              </div>

              {/* تفاصيل المرشح السريعة */}
              <div className="grid grid-cols-3 gap-2 my-4 text-xs text-slate-600 bg-slate-50 p-3 rounded-xl">
                <div className="flex items-center gap-1.5">
                  <MapPin className="w-4 h-4 text-slate-400" />
                  <span>{cand.city}</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <Briefcase className="w-4 h-4 text-slate-400" />
                  <span>{cand.years_of_experience} سنوات خبرة</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <Award className="w-4 h-4 text-slate-400" />
                  <span className="truncate">{cand.education}</span>
                </div>
              </div>

              {/* إجراءات العميل */}
              <div className="flex items-center justify-end gap-3 pt-2 border-t border-slate-100">
                <button className="flex items-center gap-1.5 text-xs text-slate-600 hover:text-indigo-600 px-3 py-2 rounded-lg border border-slate-200 hover:border-indigo-200 transition-all">
                  <Download className="w-3.5 h-3.5" />
                  معاينة السيرة الذاتية (مغلقة)
                </button>
                <button className="flex items-center gap-1.5 text-xs bg-slate-900 hover:bg-slate-800 text-white px-4 py-2 rounded-lg font-medium transition-all">
                  <Send className="w-3.5 h-3.5" />
                  طلب بيانات التواصل والتوظيف
                </button>
              </div>
            </div>
          ))}
        </section>
      </main>
    </div>
  );
}
