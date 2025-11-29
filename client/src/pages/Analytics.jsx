import React, { useState, useEffect } from 'react';
import {
  PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, CartesianGrid
} from 'recharts';
import { Search, Loader2, CheckCircle2, XCircle, HelpCircle, TrendingUp, Calendar, Hash } from 'lucide-react';

const AnalyticsDashboard = () => {
  const [claims, setClaims] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const entriesPerPage = 10;

  useEffect(() => {
    let cancelled = false;

    const fetchClaims = async () => {
      try {
        const res = await fetch('http://localhost:8000/ui/claims');
        if (!res.ok) throw new Error(`HTTP ${res.status}`);

        const data = await res.json();
        if (!cancelled) {
          const normalized = (data.claims || []).map((c, idx) => ({
            id: c.id || idx + 1,
            claim: c.claim || "Unknown claim",
            verdict: (c.verdict || "unverified").toLowerCase(),
            confidence: Number(c.confidence || 0),
            category: (c.category || "General").toString(),
            createdAt: c.verified_at || c.saved_at || new Date().toISOString(),
            sources_count: c.sources_count || 0
          }));
          setClaims(normalized);
        }
      } catch (err) {
        console.error("Failed to fetch from backend:", err);
        if (!cancelled) setClaims([]);
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    fetchClaims();
    const interval = setInterval(fetchClaims, 8000);
    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, []);

  // === STATS ===
  const total = claims.length;
  const trueCount = claims.filter(c => c.verdict === 'true').length;
  const falseCount = claims.filter(c => c.verdict === 'false').length;
  const avgConfidence = total > 0
    ? Math.round(claims.reduce((s, c) => s + c.confidence, 0) / total * 100)
    : 0;

  const pieData = [
    { name: 'True', value: trueCount },
    { name: 'False', value: falseCount },
    { name: 'Mixed/Unverified', value: total - trueCount - falseCount }
  ];
  const COLORS = ['#10B981', '#EF4444', '#F59E0B'];

  const categoryData = claims.reduce((acc, c) => {
    const cat = c.category || "Unknown";
    acc[cat] = (acc[cat] || 0) + 1;
    return acc;
  }, {});

  const barData = Object.entries(categoryData)
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 10);

  // === FILTER & PAGINATION ===
  const filtered = claims.filter(c =>
    c.claim.toLowerCase().includes(searchTerm.toLowerCase()) ||
    c.category.toLowerCase().includes(searchTerm.toLowerCase()) ||
    c.verdict.includes(searchTerm.toLowerCase())
  );

  const sorted = filtered.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
  const paginated = sorted.slice((currentPage - 1) * entriesPerPage, currentPage * entriesPerPage);
  const totalPages = Math.ceil(filtered.length / entriesPerPage);

  const getVerdictBadge = (v) => {
    if (v === 'true') return { color: 'emerald', icon: <CheckCircle2 className="w-4 h-4" /> };
    if (v === 'false') return { color: 'rose', icon: <XCircle className="w-4 h-4" /> };
    return { color: 'amber', icon: <HelpCircle className="w-4 h-4" /> };
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-16 h-16 animate-spin text-cyan-400 mx-auto mb-6" />
          <p className="text-2xl text-slate-300">Loading TruthPulse Analytics...</p>
        </div>
      </div>
    );
  }

  return (
    // <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white p-6">
    <div >
      {/* Header */}
      <div className="text-center mb-12">
        <h1 className="text-6xl font-black bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 to-purple-500 mb-3">
          TruthPulse Analytics
        </h1>
        <p className="text-xl text-slate-300">Live AI Fact-Checking Dashboard</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-6 max-w-7xl mx-auto mb-12">
        <div className="bg-white/10 backdrop-blur-xl border border-white/20 rounded-2xl p-6 text-center">
          <Hash className="w-10 h-10 text-cyan-400 mx-auto mb-3" />
          <p className="text-4xl font-bold">{total}</p>
          <p className="text-slate-400">Total Claims</p>
        </div>
        <div className="bg-emerald-500/10 border border-emerald-500/30 rounded-2xl p-6 text-center">
          <CheckCircle2 className="w-10 h-10 text-emerald-400 mx-auto mb-3" />
          <p className="text-4xl font-bold text-emerald-400">{trueCount}</p>
          <p className="text-slate-300">True</p>
        </div>
        <div className="bg-rose-500/10 border border-rose-500/30 rounded-2xl p-6 text-center">
          <XCircle className="w-10 h-10 text-rose-400 mx-auto mb-3" />
          <p className="text-4xl font-bold text-rose-400">{falseCount}</p>
          <p className="text-slate-300">False</p>
        </div>
        <div className="bg-purple-500/10 border border-purple-500/30 rounded-2xl p-6 text-center">
          <TrendingUp className="w-10 h-10 text-purple-400 mx-auto mb-3" />
          <p className="text-4xl font-bold text-purple-400">{avgConfidence}%</p>
          <p className="text-slate-300">Avg Confidence</p>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 max-w-7xl mx-auto mb-12">
        <div className="bg-white/10 backdrop-blur-xl border border-white/20 rounded-3xl p-8">
          <h2 className="text-2xl font-bold mb-6 text-center">Verdict Distribution</h2>
          <ResponsiveContainer width="100%" height={320}>
            <PieChart>
              <Pie data={pieData} cx="50%" cy="50%" innerRadius={70} outerRadius={110} dataKey="value">
                {pieData.map((_, i) => <Cell key={i} fill={COLORS[i]} />)}
              </Pie>
              <Tooltip contentStyle={{ background: '#1e293b', borderRadius: '12px', border: '1px solid #475569' }} />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white/10 backdrop-blur-xl border border-white/20 rounded-3xl p-8">
          <h2 className="text-2xl font-bold mb-6 text-center">Top Categories</h2>
          <ResponsiveContainer width="100%" height={320}>
            <BarChart data={barData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="name" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" />
              <Tooltip contentStyle={{ background: '#1e293b', borderRadius: '12px' }} />
              <Bar dataKey="count" fill="#8b5cf6" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Claims Table */}
      <div className="max-w-7xl mx-auto">
        <div className="bg-white/10 backdrop-blur-xl border border-white/20 rounded-3xl overflow-hidden">
          <div className="p-6 border-b border-white/10 flex flex-col md:flex-row justify-between items-center gap-4">
            <h2 className="text-2xl font-bold flex items-center gap-3">
              <Calendar className="w-8 h-8 text-cyan-400" />
              Recent Verifications
            </h2>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
              <input
              type="text"
              placeholder="Search claims, categories..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-11 pr-4 py-3 bg-slate-800/50 border border-slate-700 rounded-xl focus:ring-2 focus:ring-purple-500 w-80"
            />
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-white/5 text-left text-sm font-bold text-slate-400 uppercase tracking-wider">
                <tr>
                  <th className="px-6 py-4">#</th>
                  <th className="px-6 py-4">Claim</th>
                  <th className="px-6 py-4">Category</th>
                  <th className="px-6 py-4">Verdict</th>
                  <th className="px-6 py-4">Confidence</th>
                  <th className="px-6 py-4">Date</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/10">
                {paginated.length > 0 ? paginated.map((c, i) => {
                  const badge = getVerdictBadge(c.verdict);
                  return (
                    <tr key={c.id} className="hover:bg-white/5 transition-colors">
                      <td className="px-6 py-4 text-slate-400">{i + 1 + (currentPage - 1) * entriesPerPage}</td>
                      <td className="px-6 py-4 max-w-md truncate font-medium">{c.claim}</td>
                      <td className="px-6 py-4">
                        <span className="px-3 py-1 bg-purple-500/20 text-purple-300 rounded-full text-xs font-bold">
                          {c.category}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full bg-${badge.color}-500/20 text-${badge.color}-300 border border-${badge.color}-500/30`}>
                          {badge.icon}
                          <span className="font-bold uppercase text-xs">{c.verdict}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-3">
                          <div className="w-20 bg-slate-700 rounded-full h-2">
                            <div className={`h-2 rounded-full bg-${c.confidence > 0.8 ? 'emerald' : c.confidence > 0.5 ? 'yellow' : 'rose'}-500`} style={{ width: `${c.confidence * 100}%` }} />
                          </div>
                          <span className="text-sm">{(c.confidence * 100).toFixed(0)}%</span>
                        </div>
                      </td>
                      <td className="px-6 py-4 text-sm text-slate-400">
                        {new Date(c.createdAt).toLocaleDateString()}
                      </td>
                    </tr>
                  );
                }) : (
                  <tr>
                    <td colSpan={6} className="text-center py-16 text-slate-500">
                      <Search className="w-12 h-12 mx-auto mb-3 opacity-50" />
                      <p>No claims found</p>
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="p-4 border-t border-white/10 flex justify-center gap-2">
              {Array.from({ length: totalPages }, (_, i) => (
                <button
                  key={i}
                  onClick={() => setCurrentPage(i + 1)}
                  className={`px-4 py-2 rounded-lg transition ${currentPage === i + 1 ? 'bg-purple-600 text-white' : 'bg-white/10 hover:bg-white/20'}`}
                >
                  {i + 1}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AnalyticsDashboard;