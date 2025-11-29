import React, { useState, useEffect } from 'react';
import {
  Activity, Search, Rss, Database, FileText, XCircle,
  CheckCircle2, Share2, RotateCcw, ShieldCheck, Train
} from 'lucide-react';

/* --- STYLES --- */
const styles = `
  .glass-panel {
    background: rgba(15, 23, 42, 0.8);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.6);
  }
  .verdict-glow-green { text-shadow: 0 0 20px rgba(34, 197, 94, 0.6); }
  .verdict-glow-red { text-shadow: 0 0 20px rgba(239, 68, 68, 0.6); }
  @keyframes pulse { 0%,100% { opacity: 0.6; } 50% { opacity: 1; } }
`;

/* --- REAL BACKEND CALL --- */
async function verifyClaimWithBackend(claimText) {
  try {
    const res = await fetch("http://localhost:8000/ui/verify", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ claim: claimText })
    });

    if (!res.ok) throw new Error("Network error");

    const data = await res.json();

    return {
      verdict: data.verdict,
      confidence: data.confidence,
      category: data.category || "General",
      rationale: data.rationale,
      sources: data.evidence.map(ev => ({
        title: ev.title || "Source Document",
        url: ev.url,
        status: ev.stance === "support"
          ? (data.verdict === "true" ? "Supports Claim" : "Contradicts Claim")
          : ev.stance === "refute"
          ? (data.verdict === "false" ? "Supports Verdict" : "Contradicts Verdict")
          : "Neutral / Partial",
        time: ev.published ? new Date(ev.published).toLocaleDateString() : "Historical"
      }))
    };
  } catch (err) {
    console.error("Verification failed:", err);
    return {
      verdict: "unverified",
      confidence: 0.1,
      rationale: "Could not connect to verification engine. Please check your backend.",
      sources: []
    };
  }
}

export default function Home() {
  const [status, setStatus] = useState('idle');
  const [claim, setClaim] = useState('');
  const [resultTab, setResultTab] = useState('general');
  const [currentStep, setCurrentStep] = useState(0);
  const [resultData, setResultData] = useState(null);

  const steps = [
    { text: 'Analyzing claim...', icon: Search },
    { text: 'Searching knowledge base...', icon: Database },
    { text: 'Cross-checking sources...', icon: Rss },
    { text: 'Generating verdict...', icon: FileText }
  ];

  useEffect(() => {
    if (status !== 'processing') return;

    let step = 0;
    const interval = setInterval(() => {
      step++;
      setCurrentStep(step);
      if (step >= steps.length) {
        clearInterval(interval);
        verifyClaimWithBackend(claim).then(data => {
          setResultData(data);
          setStatus('complete');
        });
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [status, claim]);

  const handleCopyVerdict = async () => {
    if (!resultData) return;
    const text = [
      `Claim: "${claim}"`,
      `VERDICT: ${resultData.verdict.toUpperCase()} (${Math.round(resultData.confidence * 100)}% confident)`,
      `Category: ${resultData.category}`,
      ``,
      resultTab === 'kids' ? "Kid-Friendly:" : resultTab === 'elderly' ? "Clear Explanation:" : "Full Analysis:",
      resultTab === 'kids' ? getKidExplanation() :
      resultTab === 'elderly' ? getElderlyExplanation() :
      resultData.rationale,
      ``,
      "Sources Checked:",
      ...resultData.sources.map(s => `• ${s.title} — ${s.status} (${s.time})`),
      ``,
      `Verified by TruthPulse AI • ${new Date().toLocaleString()}`
    ].join("\n");

    await navigator.clipboard.writeText(text);
    alert("Verdict copied to clipboard!");
  };

  const getKidExplanation = () => {
    if (resultData.verdict === "true") return `Yay! This is TRUE! Lots of trusted news said the same thing.`;
    if (resultData.verdict === "false") return `Oops! This is NOT true. Some people made it up.`;
    if (resultData.verdict === "mixed") return `Hmm... some parts are true, some are not. Be careful!`;
    return `We couldn't find enough info. Better ask a teacher or parent!`;
  };

  const getElderlyExplanation = () => {
    if (resultData.verdict === "true") return `This information has been confirmed by reliable sources. You can trust it.`;
    if (resultData.verdict === "false") return `This claim is inaccurate and has been debunked by credible sources.`;
    if (resultData.verdict === "mixed") return `The claim contains some truth but also false parts. Proceed with caution.`;
    return `There is not enough reliable evidence to confirm this claim.`;
  };

  const handleReset = () => {
    setStatus('idle'); setClaim(''); setCurrentStep(0); setResultData(null); setResultTab('general');
  };

  return (
    // <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white overflow-x-hidden">
    <div >
      <style>{styles}</style>

      <div className="flex flex-col min-h-screen">
        <main className="flex-grow flex items-center justify-center p-4">
          <div className="w-full max-w-3xl">

            {/* IDLE STATE */}
            {status === 'idle' && (
              <div className="text-center mb-10 animate-in fade-in duration-1000">
                <h1 className="text-7xl font-black bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 to-purple-600 mb-4">
                  TruthPulse
                </h1>
                <p className="text-2xl text-slate-300">AI-Powered Claim Verification</p>
              </div>
            )}

            {/* MAIN CARD */}
            <div className="glass-panel rounded-3xl overflow-hidden shadow-2xl">

              {/* IDLE: Input */}
              {status === 'idle' && (
                <div className="p-10 space-y-8">
                  <div>
                    <label className="text-sm font-bold text-cyan-400 uppercase tracking-wider">Enter Your Claim</label>
                    <textarea
                      value={claim}
                      onChange={(e) => setClaim(e.target.value)}
                      placeholder="e.g. All schools in Delhi are closed due to pollution..."
                      className="w-full mt-3 h-48 bg-slate-900/70 border border-slate-700 rounded-2xl p-6 text-lg text-white placeholder:text-slate-400 resize-none focus:ring-4 focus:ring-purple-500/30 focus:border-purple-500 outline-none transition-all"

                    />
                    <div className="text-right text-xs text-white mt-2">{claim.length}/2000</div>
                  </div>

                  <button
                    onClick={() => claim.trim() && setStatus('processing')}
                    disabled={!claim.trim()}
                    className="w-full py-5 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 rounded-2xl font-bold text-xl flex items-center justify-center gap-3 transform hover:scale-[1.02] transition-all shadow-xl"
                  >
                    <Train className="w-6 h-6" />
                    VERIFY CLAIM NOW
                  </button>
                </div>
              )}

              {/* PROCESSING */}
              {status === 'processing' && (
                <div className="p-16 text-center space-y-12">
                  <Activity className="w-20 h-20 mx-auto text-purple-500 animate-spin" />
                  <h2 className="text-3xl font-bold">Verifying Your Claim...</h2>
                  <div className="space-y-6 max-w-md mx-auto">
                    {steps.map((s, i) => (
                      <div key={i} className={`flex items-center gap-4 text-left transition-all ${i < currentStep ? 'opacity-100' : 'opacity-40'}`}>
                        <div className={`w-10 h-10 rounded-full flex items-center justify-center ${i < currentStep ? 'bg-green-500' : 'bg-slate-700'}`}>
                          {i < currentStep ? <CheckCircle2 size={20} /> : <s.icon size={18} />}
                        </div>
                        <span className={i < currentStep ? 'text-green-400 font-medium' : 'text-slate-400'}>
                          {s.text}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* RESULT */}
              {status === 'complete' && resultData && (
                <div className="space-y-8 p-8 animate-in fade-in">

                  {/* Verdict Header */}
                  <div className={`text-center p-10 rounded-3xl ${resultData.verdict === "true" ? 'bg-green-900/30' : 'bg-red-900/30'}`}>
                    <div className={`inline-flex p-6 rounded-full mb-6 ${resultData.verdict === "true" ? 'bg-green-600' : 'bg-red-600'} shadow-2xl`}>
                      {resultData.verdict === "true" ? <CheckCircle2 size={64} /> : <XCircle size={64} />}
                    </div>
                    <h1 className={`text-6xl font-black ${resultData.verdict === "true" ? 'text-green-400 verdict-glow-green' : 'text-red-400 verdict-glow-red'}`}>
                      {resultData.verdict.toUpperCase()}
                    </h1>
                    <p className="text-2xl mt-4">
                      Confidence: <span className="font-bold">{Math.round(resultData.confidence * 100)}%</span>
                    </p>
                  </div>

                  {/* Audience Tabs */}
                  <div className="flex gap-2 bg-slate-800/50 p-1 rounded-2xl">
                    {['general', 'kids', 'elderly'].map(tab => (
                      <button
                        key={tab}
                        onClick={() => setResultTab(tab)}
                        className={`flex-1 py-3 rounded-xl font-bold capitalize transition-all ${resultTab === tab ? 'bg-purple-600 text-white shadow-lg' : 'text-slate-400'}`}
                      >
                        {tab === 'general' ? 'Full Analysis' : tab === 'kids' ? 'For Kids' : 'Clear & Simple'}
                      </button>
                    ))}
                  </div>

                  {/* Explanation */}
                  <div className="bg-slate-800/60 border border-slate-700 rounded-2xl p-8">
                    <div className="flex gap-4">
                      <ShieldCheck className="w-8 h-8 text-purple-400 flex-shrink-0" />
                      <p className="text-lg leading-relaxed">
                        {resultTab === 'kids' ? getKidExplanation() :
                         resultTab === 'elderly' ? getElderlyExplanation() :
                         resultData.rationale}
                      </p>
                    </div>
                  </div>

                  {/* Sources */}
                  <div>
                    <h3 className="text-sm font-bold text-slate-400 uppercase mb-4">Sources Verified ({resultData.sources.length})</h3>
                    <div className="space-y-3">
                      {resultData.sources.length > 0 ? resultData.sources.map((s, i) => (
                        <div key={i} className="bg-slate-800/40 border border-slate-700 rounded-xl p-4 flex justify-between items-start hover:bg-slate-800/60 transition-all">
                          <div>
                            <h4 className="font-semibold text-slate-200">{s.title}</h4>
                            <p className="text-xs text-slate-500 mt-1">{s.time}</p>
                          </div>
                          <span className={`text-xs font-bold px-3 py-1 rounded-full ${s.status.includes("Support") ? 'bg-green-900/60 text-green-300' : 'bg-red-900/60 text-red-300'}`}>
                            {s.status}
                          </span>
                        </div>
                      )) : (
                        <p className="text-slate-500 italic">No matching sources found in knowledge base.</p>
                      )}
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex gap-4 pt-6 border-t border-slate-700">
                    <button onClick={handleReset} className="flex-1 py-4 bg-slate-800 hover:bg-slate-700 rounded-xl font-bold flex items-center justify-center gap-2">
                      <RotateCcw size={20} /> Check Another
                    </button>
                    <button onClick={handleCopyVerdict} className="flex-1 py-4 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 rounded-xl font-bold flex items-center justify-center gap-2 shadow-xl">
                      <Share2 size={20} /> Copy Verdict
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}