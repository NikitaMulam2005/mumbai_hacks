import React, { useState, useEffect } from 'react';
import { 
  ShieldAlert, 
  Train, 
  Cpu, 
  Search, 
  FileText, 
  MessageSquare, 
  CheckCircle, 
  Zap,
  Info,
  Droplets,
  ArrowRight
} from 'lucide-react';

const About = () => {
  const [activeStep, setActiveStep] = useState(0);

  // Animation loop for the pipeline visualization
  useEffect(() => {
    const interval = setInterval(() => {
      setActiveStep((prev) => (prev + 1) % 4);
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  const glassCardClass = "backdrop-blur-xl bg-white/10 border border-white/20 shadow-[0_8px_32px_0_rgba(31,38,135,0.37)] rounded-2xl p-6 hover:bg-white/15 transition-all duration-300 transform hover:-translate-y-1";
  
  const pipelineSteps = [
    { 
      id: 0, 
      title: "Detector", 
      icon: Search, 
      desc: "Extracts key entities & claims", 
      color: "text-cyan-400", 
      bg: "bg-cyan-500/20" 
    },
    { 
      id: 1, 
      title: "Verifier", 
      icon: FileText, 
      desc: "Checks datasets & RSS feeds", 
      color: "text-purple-400", 
      bg: "bg-purple-500/20" 
    },
    { 
      id: 2, 
      title: "Explainer", 
      icon: Cpu, 
      desc: "Generates logic & reasoning", 
      color: "text-pink-400", 
      bg: "bg-pink-500/20" 
    },
    { 
      id: 3, 
      title: "Verdict", 
      icon: CheckCircle, 
      desc: "Delivers final classification", 
      color: "text-emerald-400", 
      bg: "bg-emerald-500/20" 
    }
  ];

  return (
    // <div className="min-h-screen bg-slate-950 text-slate-100 font-sans selection:bg-cyan-500 selection:text-white overflow-x-hidden relative">
    <div >
      
      {/* Background Ambience (Mumbai Night/Monsoon Vibe) */}
      <div className="fixed inset-0 -z-10">
        <div className="absolute top-[-10%] left-[-10%] w-[500px] h-[500px] bg-purple-900/40 rounded-full blur-[120px] animate-pulse"></div>
        <div className="absolute bottom-[-10%] right-[-10%] w-[600px] h-[600px] bg-cyan-900/30 rounded-full blur-[120px] animate-pulse delay-1000"></div>
        <div className="absolute top-[40%] left-[50%] transform -translate-x-1/2 w-[800px] h-[400px] bg-blue-900/20 rounded-full blur-[100px]"></div>
        
        {/* Abstract Rain Effect */}
        {/* <div className="absolute inset-0 opacity-20" style={{ backgroundImage: 'url("https://www.transparenttextures.com/patterns/stardust.png")' }}></div> */}
      </div>

      <div className="relative -z-10 max-w-6xl mx-auto px-6 pt-16 space-y-20">
        
        {/* 1. Title Section */}
        <header className="text-center space-y-6 animate-fade-in-up">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 backdrop-blur-md text-sm font-medium text-cyan-300 mb-4">
            <Zap size={16} className="animate-bounce" />
            <span>Live at MumbaiHacks 2025</span>
          </div>
          
          <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight text-white/70">
            About <span className="bg-clip-text text-transparent bg-linear-to-r from-cyan-400 via-blue-400 to-purple-500 drop-shadow-[0_0_15px_rgba(6,182,212,0.5)]">TruthPulse</span>
          </h1>
          
          <p className="text-xl text-slate-300 max-w-2xl mx-auto leading-relaxed">
            Navigating the chaos of the information age with the precision of AI.
          </p>
        </header>

        {/* 2. Glass Cards Grid */}
        <section className="grid md:grid-cols-1 gap-8">
          
          {/* Card 1: What We Do */}
          <div className={glassCardClass}>
            <div className="flex items-center gap-4 mb-6">
              <div className="p-3.5 bg-linear-to-br from-cyan-500/20 to-blue-500/20 rounded-xl border border-cyan-500/30 text-cyan-300 shadow-lg shadow-cyan-500/10">
                <ShieldAlert size={32} />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-white">The Mission</h2>
                <p className="text-xs text-cyan-200/70 font-mono tracking-wider uppercase">Project Objective</p>
              </div>
            </div>
            
            <p className="text-slate-300 mb-6 leading-relaxed">
              Misinformation spreads faster than a viral tweet. TruthPulse acts as a digital immune system, providing real-time analysis to separate fact from fiction.
            </p>
            <p className="text-slate-300 mb-6 leading-relaxed">TruthPulse is dedicated to combating misinformation by providing instant, AI-powered claim verification for the people of Mumbai and beyond.
               In an era where false information spreads faster than truth, we stand as a beacon of accuracy and transparency.
            </p>
            <p className="text-slate-300 mb-6 leading-relaxed">Built specifically for MumbaiHacks, our platform combines cutting-edge AI technology with local datasets and real-time feeds to deliver verdicts you can trust. 
              We believe in making fact-checking accessible to everyone, from kids to the elderly.</p>
          </div>
        </section>

        {/* 3. Pipeline Visualization */}
        <section className={`${glassCardClass} !p-0 overflow-hidden`}>
          <div className="p-8 border-b border-white/10">
            <div className="flex items-center gap-3 mb-2">
              <Cpu className="text-pink-400" />
              <h2 className="text-2xl font-bold text-white">The Agent Pipeline</h2>
            </div>
            <p className="text-slate-400 text-sm">
              A high-level view of how our 4-agent system processes a single claim.
            </p>
          </div>

          <div className="p-8 md:p-12 relative">
            {/* Connecting Line */}
            <div className="hidden md:block absolute top-[50%] left-12 right-12 h-1 bg-slate-800 -translate-y-1/2 rounded-full overflow-hidden">
               {/* Animated Progress Line */}
               <div className="h-full bg-linear-to-r from-cyan-500 via-purple-500 to-emerald-500 w-full animate-[shimmer_2s_infinite] opacity-50"></div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-8 relative">
              {pipelineSteps.map((step, index) => (
                <div 
                  key={step.id} 
                  className={`relative flex flex-col items-center text-center transition-all duration-500 ${
                    activeStep === index ? 'opacity-100 scale-105' : 'opacity-70 scale-95'
                  }`}
                >
                  {/* Step Number Badge */}
                  <div className="absolute -top-3 right-1/2 translate-x-[200%] md:translate-x-8 bg-slate-900 text-[10px] font-mono border border-white/10 px-2 py-0.5 rounded text-slate-400">
                    0{index + 1}
                  </div>

                  {/* Icon Circle */}
                  <div className={`w-20 h-20 rounded-2xl ${step.bg} border border-white/10 flex items-center justify-center mb-6 shadow-[0_0_20px_rgba(0,0,0,0.3)] backdrop-blur-md z-10 transition-all duration-500 ${activeStep === index ? 'ring-2 ring-white/50 shadow-[0_0_30px_rgba(255,255,255,0.2)]' : ''}`}>
                    <step.icon size={32} className={`${step.color}`} />
                  </div>

                  {/* Text */}
                  <h3 className={`text-lg font-bold text-white mb-2 ${activeStep === index ? 'text-transparent bg-clip-text bg-linear-to-r from-white to-slate-400' : ''}`}>
                    {step.title}
                  </h3>
                  <p className="text-sm text-slate-400 leading-tight px-2">
                    {step.desc}
                  </p>
                  
                  {/* Active Indicator (Mobile only) */}
                  {activeStep === index && (
                    <div className="md:hidden mt-4 text-xs font-mono text-cyan-400 animate-bounce">
                      Processing...
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
          
          <div className="bg-black/20 p-4 border-t border-white/5 flex items-center justify-between text-xs text-slate-500 font-mono">
            <span>SYSTEM STATUS: ONLINE</span>
            <span>LATENCY: 42ms</span>
          </div>
        </section>

        <section className="grid md:grid-cols-2 gap-8">
          
          {/* Card 1 */}
          <div className={glassCardClass}>
            <div className="flex items-center gap-4 mb-6">
              {/* <div className="p-3.5 bg-linear-to-br from-cyan-500/20 to-blue-500/20 rounded-xl border border-cyan-500/30 text-cyan-300 shadow-lg shadow-cyan-500/10">
                <ShieldAlert size={32} />
              </div> */}
              <div>
                <h2 className="text-2xl font-bold text-white">AI-Powered</h2>
              </div>
            </div>
            
            <p className="text-slate-300 mb-6 leading-relaxed">
              Advanced natural language processing and machine learning algorithms analyze claims 
                  with unprecedented accuracy.
            </p>
          </div>

          {/* Card 2 */}
          <div className={glassCardClass}>
            <div className="flex items-center gap-4 mb-6">
              <div>
                <h2 className="text-2xl font-bold text-white">Real-Time</h2>
              </div>
            </div>
            
            <p className="text-slate-300 mb-6 leading-relaxed">
              Get instant verification results within seconds. No waiting, no delays 
                  truth at the speed of light.
            </p>
          </div>

          {/* Card 3 */}
          <div className={glassCardClass}>
            <div className="flex items-center gap-4 mb-6">
              <div>
                <h2 className="text-2xl font-bold text-white">Multi-Source</h2>
              </div>
            </div>
            
            <p className="text-slate-300 mb-6 leading-relaxed">
              We check Kaggle datasets, RSS feeds, official alerts, and fact-checking databases 
                  for comprehensive verification.
            </p>
          </div>

          {/* Card 4 */}
          <div className={glassCardClass}>
            <div className="flex items-center gap-4 mb-6">
              <div>
                <h2 className="text-2xl font-bold text-white">Transparent</h2>
              </div>
            </div>
            
            <p className="text-slate-300 mb-6 leading-relaxed">
              Every verdict shows exactly which sources were checked and how they contributed 
                  to the final result.
            </p>
          </div>
        </section>

        <section className="grid md:grid-cols-1 gap-8">
          {/* Why Mumbai Theme */}
          <div className={glassCardClass}>
            <div className="flex items-center gap-4 mb-6">
              <div>
                <h2 className="text-2xl font-bold text-white">Why Mumbai-Themed?</h2>
              </div>
            </div>
            
            <p className="text-slate-300 mb-6 leading-relaxed">
              Mumbai is not just India's financial capital – it's a city that never sleeps, where information 
                flows as constantly as the local trains. The city's iconic landmarks inspire our design: the 
                Sea Link represents our connections to multiple data sources and Marine Drive symbolizes our 
                smooth user experience.
            </p>
            <p className="text-slate-300 mb-6 leading-relaxed">TruthPulse is dedicated to combating misinformation by providing instant, AI-powered claim verification for the people of Mumbai and beyond.
               Created for MumbaiHacks, TruthPulse embodies the spirit of Mumbai: fast, reliable, and 
                always moving forward. Just as Mumbaikars rely on their local trains to get them where 
                they need to go, they can rely on TruthPulse to get them to the truth.
            </p>
            </div>
        </section>
      </div>
    </div>
  );
};

export default About;