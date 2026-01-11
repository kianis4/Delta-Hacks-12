'use client';

import Link from 'next/link';
import { ArrowRight, Scale, Shield, Zap, Database, Terminal, Users, FileText, Gavel, BookOpen, Briefcase, Award } from 'lucide-react';
import { cn } from '@/lib/utils';

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-[#050A18] text-white selection:bg-[#C5A065] selection:text-white font-sans overflow-x-hidden relative">
      {/* Background Image with Overlay */}
      <div className="fixed inset-0 z-0">
          <img 
            src="/hero-bg.png" 
            alt="Office Skyline" 
            className="w-full h-full object-cover opacity-40 mix-blend-overlay"
          />
          <div className="absolute inset-0 bg-gradient-to-b from-[#050A18]/90 via-[#050A18]/80 to-[#050A18]" />
      </div>

      {/* Navbar */}
      <nav className="border-b border-white/5 bg-[#050A18]/80 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-24 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="w-10 h-10 bg-gradient-to-br from-[#C5A065] to-[#8C6D3B] p-0.5 rounded-lg shadow-lg shadow-[#C5A065]/20 rotate-3 group hover:rotate-0 transition-transform duration-500">
               <div className="w-full h-full bg-[#050A18] rounded-[6px] flex items-center justify-center">
                  <span className="font-serif font-bold text-[#C5A065] text-lg">M</span>
               </div>
            </div>
            <div className="flex flex-col">
              <span className="font-serif font-bold text-2xl tracking-wide text-white">MIKE ROSS AI</span>
              <span className="text-[10px] text-slate-400 font-medium tracking-[0.2em] uppercase">Senior Associate</span>
            </div>
          </div>
          <div className="flex items-center gap-8">
             <Link href="https://github.com/kianis4/Delta-Hacks-12" target="_blank" className="text-sm font-medium text-slate-400 hover:text-[#C5A065] transition-colors hidden md:block">
                THE FIRM
             </Link>
             <Link 
                href="/chat" 
                className="group relative px-6 py-3 bg-white text-[#050A18] rounded-none text-sm font-bold tracking-widest uppercase hover:bg-[#C5A065] transition-all duration-300 overflow-hidden"
              >
                <span className="relative z-10 group-hover:text-white transition-colors duration-300">Consult The Closer</span>
                <div className="absolute inset-0 bg-[#C5A065] transform -translate-x-full group-hover:translate-x-0 transition-transform duration-300 ease-out" />
              </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative pt-32 pb-32 border-b border-white/5">
        <div className="max-w-6xl mx-auto px-6 relative z-10">
          <div className="grid md:grid-cols-2 gap-16 items-center">
            
            {/* Text Content */}
            <div className="order-2 md:order-1">
              <div className="inline-flex items-center gap-2 px-4 py-1.5 border border-[#C5A065]/30 bg-[#C5A065]/5 text-[#C5A065] text-xs font-bold uppercase tracking-widest mb-8 animate-in fade-in slide-in-from-left-4 duration-700">
                <Award className="w-3 h-3" />
                <span>DeltaHacks 12 • Best Use of Gemini</span>
              </div>
              
              <h1 className="text-6xl md:text-8xl font-serif font-medium tracking-tight mb-8 text-white leading-[0.9] animate-in fade-in slide-in-from-bottom-8 duration-700">
                Winners <br/>
                <span className="text-[#64748B]">don't make excuses.</span>
              </h1>
              
              <p className="text-xl text-slate-400 max-w-lg mb-12 leading-relaxed font-light border-l-2 border-[#C5A065] pl-6 animate-in fade-in slide-in-from-bottom-12 duration-1000 delay-100 italic">
                "I don't play the odds, I play the man." <br/>
                <span className="text-sm text-slate-500 not-italic mt-2 block font-sans uppercase tracking-widest">
                  — The Photographic Memory Legal Engine
                </span>
              </p>
              
              <div className="flex flex-col sm:flex-row items-start gap-6 animate-in fade-in slide-in-from-bottom-16 duration-1000 delay-200">
                <Link 
                  href="/chat"
                  className="px-10 py-5 bg-[#C5A065] hover:bg-[#A3824A] text-[#050A18] font-bold tracking-widest uppercase transition-all shadow-xl shadow-[#C5A065]/20 flex items-center gap-3 group"
                >
                  Enter The Glass Office
                  <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </Link>
              </div>
            </div>

            {/* Visual Abstract */}
            <div className="order-1 md:order-2 relative h-[500px] w-full flex items-center justify-center">
                 {/* This represents the "Photographic Memory" / Nodes */}
                 <div className="absolute inset-0 bg-gradient-to-tr from-[#050A18] via-transparent to-transparent z-10" />
                 <div className="relative w-full h-full border border-white/5 bg-white/[0.02] backdrop-blur-sm rounded-none p-8 flex flex-col justify-between overflow-hidden group">
                    <div className="absolute top-0 right-0 p-4 opacity-50">
                        <Database className="w-24 h-24 text-white/5" />
                    </div>
                    
                    {/* Floating Cards simulating files */}
                    <div className="space-y-4 relative z-20">
                        <FloatingFile title="Residential Tenancies Act.pdf" type="ONTARIO STATUTE" delay="0s" />
                        <FloatingFile title="Criminal Code (C-46).xml" type="FEDERAL STATUTE" delay="1s" />
                        <FloatingFile title="Divorce Act (C-3).xml" type="FEDERAL STATUTE" delay="2s" />
                    </div>

                    <div className="mt-8 border-t border-white/10 pt-4">
                        <div className="flex justify-between items-end">
                            <div>
                                <div className="text-4xl font-bold text-white mb-1">16,170</div>
                                <div className="text-xs text-[#C5A065] font-mono uppercase tracking-widest">Pages Memorized</div>
                            </div>
                            <div className="text-right">
                                <div className="text-xs text-slate-500 uppercase tracking-widest mb-1">Retrieval Time</div>
                                <div className="text-xl font-bold text-white">0.4s</div>
                            </div>
                        </div>
                    </div>
                 </div>
            </div>

          </div>
        </div>
      </section>

      {/* The Evidence (Tech Stack) */}
      <section className="py-24 bg-[#080E20] border-b border-white/5 relative">
        <div className="max-w-7xl mx-auto px-6">
            <div className="flex flex-col md:flex-row justify-between items-end mb-16 gap-8">
                <div>
                     <span className="text-[#C5A065] font-mono text-xs uppercase tracking-widest mb-2 block">The Architecture</span>
                     <h2 className="text-4xl md:text-5xl font-serif text-white">Built Like a Iron-Clad Contract.</h2>
                </div>
                <p className="max-w-md text-slate-400 leading-relaxed text-sm text-right">
                    We didn't just wrap ChatGPT. We engineered a stateful, multi-agent system that verifies every citation against the official statutes. No hallucinations. Just facts.
                </p>
            </div>

            <div className="grid md:grid-cols-3 gap-px bg-white/10 border border-white/10">
                <TechCell 
                    icon={<Database className="w-6 h-6 text-[#C5A065]" />}
                    title="The Vault"
                    subtitle="MongoDB Atlas Vector Search"
                    desc="16,170 document chunks indexed with HNSW graphs. 768-dimensional embeddings for semantic understanding of complex legalese."
                />
                <TechCell 
                    icon={<Terminal className="w-6 h-6 text-[#C5A065]" />}
                    title="The Brain"
                    subtitle="Google Gemini 2.0 Flash"
                    desc="1M+ token context window allowing for massive retrieval-augmented generation (RAG) without losing the thread of the argument."
                />
                <TechCell 
                    icon={<Shield className="w-6 h-6 text-[#C5A065]" />}
                    title="The Logic"
                    subtitle="LangGraph State Machine"
                    desc="A deterministic state graph that routes queries (Router -> Research -> Draft) ensuring legally sound workflows, not random chat."
                />
            </div>
        </div>
      </section>

      {/* Practice Areas */}
      <section className="py-24 bg-[#050A18] relative overflow-hidden">
          <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-white/[0.02] rounded-full blur-[100px] pointer-events-none" />
          
          <div className="max-w-7xl mx-auto px-6">
             <div className="text-center mb-20">
                <h2 className="text-sm font-bold text-[#C5A065] uppercase tracking-[0.3em] mb-4">Areas of Practice</h2>
                <p className="text-3xl font-serif text-white">"We Handle The Cases You Can't."</p>
             </div>

             <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
                 <PracticeMetric number="01" title="Corporate & Tax" desc="Income Tax Act & Excise Tax Act disputes. CRA navigation." />
                 <PracticeMetric number="02" title="Criminal Defense" desc="Criminal Code of Canada (C-46). Procedure & Sentencing." />
                 <PracticeMetric number="03" title="Family Law" desc="Divorce Act (C-3). Separation agreements, assets, and custody." />
                 <PracticeMetric number="04" title="Tenancy Disputes" desc="RTA (ON, BC, AB). Evictions (N12/N5) and Landlord Tenant Board." />
             </div>
          </div>
      </section>

      {/* Team / The Name Partners */}
      <section className="py-32 bg-[#050A18] border-t border-white/5 text-center">
        <div className="max-w-4xl mx-auto px-6">
            <h2 className="text-4xl font-serif mb-16">The Name Partners</h2>
            
            <div className="flex flex-col md:flex-row justify-center gap-20">
                <PartnerCard 
                    initials="SK"
                    name="Suleyman Kiani"
                    title="Senior Partner • Engineering"
                    link="https://www.linkedin.com/in/suleymankiani/"
                />
                <div className="hidden md:block w-px bg-gradient-to-b from-transparent via-white/20 to-transparent" />
                <PartnerCard 
                    initials="KE"
                    name="Karim Elbasiouni"
                    title="Name Partner • AI Research"
                    link="https://www.linkedin.com/in/karim-elbasiouni/"
                />
            </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 bg-[#02040a] border-t border-white/5 text-center">
         <div className="max-w-7xl mx-auto px-6 flex flex-col items-center">
             <div className="w-8 h-8 bg-[#C5A065] mask-square mb-6 flex items-center justify-center font-serif font-bold text-[#050A18]">M</div>
             <p className="text-slate-500 text-sm font-light mb-8 max-w-md mx-auto">
                 "Life is this. I like this." <br/>
                 <span className="text-[#C5A065]">— Harvey Specter</span>
             </p>
             <div className="flex gap-6 text-xs text-slate-600 uppercase tracking-widest">
                 <span>© 2026 Mike Ross AI</span>
                 <span>DeltaHacks 12</span>
                 <span>Security Clearance: Top Secret</span>
             </div>
         </div>
      </footer>
    </main>
  );
}

// --- Components ---

function FloatingFile({ title, type, delay }: { title: string, type: string, delay: string }) {
    return (
        <div 
            className="p-4 bg-[#0A1025] border border-white/5 flex items-center gap-4 hover:border-[#C5A065]/50 transition-colors animate-in slide-in-from-right-8 duration-1000 fill-mode-both w-full max-w-[320px] ml-auto"
            style={{ animationDelay: delay }}
        >
            <div className="p-2 bg-[#C5A065]/10 text-[#C5A065]">
                <FileText className="w-5 h-5" />
            </div>
            <div>
                <div className="text-sm font-medium text-slate-200">{title}</div>
                <div className="text-[10px] text-slate-500 font-mono tracking-widest">{type}</div>
            </div>
        </div>
    )
}

function TechCell({ icon, title, subtitle, desc }: any) {
    return (
        <div className="bg-[#050A18] p-10 hover:bg-[#0A1025] transition-colors group">
            <div className="mb-6 opacity-50 group-hover:opacity-100 transition-opacity">{icon}</div>
            <h3 className="text-xl font-bold text-white mb-1 group-hover:text-[#C5A065] transition-colors">{title}</h3>
            <div className="text-xs font-mono text-slate-500 mb-4">{subtitle}</div>
            <p className="text-sm text-slate-400 leading-relaxed font-light">{desc}</p>
        </div>
    )
}

function PracticeMetric({ number, title, desc }: any) {
    return (
        <div className="group border-l border-white/10 pl-8 hover:border-[#C5A065] transition-colors duration-500">
            <div className="text-5xl font-serif text-white/10 font-bold mb-4 group-hover:text-[#C5A065]/20 transition-colors">{number}</div>
            <h3 className="text-lg font-bold text-white mb-2">{title}</h3>
            <p className="text-sm text-slate-400 leading-relaxed font-light">{desc}</p>
        </div>
    )
}

function PartnerCard({ initials, name, title, link }: any) {
    return (
        <a href={link} target="_blank" className="text-center group cursor-pointer">
            <div className="w-32 h-32 mx-auto bg-[#0A1025] border border-white/10 flex items-center justify-center mb-6 group-hover:border-[#C5A065] transition-all duration-500 relative overflow-hidden">
                <div className="absolute inset-0 bg-[#C5A065] transform translate-y-full group-hover:translate-y-0 transition-transform duration-500 ease-in-out opacity-10" />
                <span className="text-4xl font-serif text-slate-600 group-hover:text-white transition-colors">{initials}</span>
            </div>
            <h3 className="text-xl font-bold text-white group-hover:text-[#C5A065] transition-colors">{name}</h3>
            <p className="text-xs text-slate-500 uppercase tracking-widest mt-2">{title}</p>
        </a>
    )
}
