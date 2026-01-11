'use client';

import Link from 'next/link';
import { ArrowRight, Scale, Shield, Zap, Database, Terminal, Users } from 'lucide-react';
import { Analytics } from "@vercel/analytics/react";
import { SpeedInsights } from "@vercel/speed-insights/next";

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-slate-950 text-white selection:bg-indigo-500 selection:text-white">
      {/* Navbar */}
      <nav className="border-b border-white/10 bg-slate-950/50 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="bg-indigo-600 p-2 rounded-lg">
              <Scale className="w-5 h-5 text-white" />
            </div>
            <span className="font-bold text-xl tracking-tight">Mike Ross AI</span>
          </div>
          <Link 
            href="/chat" 
            className="text-sm font-medium text-slate-300 hover:text-white transition-colors"
          >
            Launch App
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative pt-32 pb-20 overflow-hidden">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1000px] h-[600px] bg-indigo-600/20 blur-[120px] rounded-full pointer-events-none" />
        
        <div className="max-w-4xl mx-auto px-6 text-center relative z-10">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-xs font-medium mb-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <Zap className="w-3 h-3" />
            <span>Powered by Gemini 2.0 & MongoDB Atlas</span>
          </div>
          
          <h1 className="text-5xl md:text-7xl font-bold tracking-tight mb-8 bg-gradient-to-b from-white to-slate-400 bg-clip-text text-transparent animate-in fade-in slide-in-from-bottom-8 duration-700">
            The AI Legal Assistant <br/> for Canadians.
          </h1>
          
          <p className="text-lg md:text-xl text-slate-400 max-w-2xl mx-auto mb-10 leading-relaxed animate-in fade-in slide-in-from-bottom-12 duration-1000 delay-100">
            Navigate complex legal landscapes with confidence. From tenancy disputes to specialized document drafting, Mike Ross AI turns legal jargon into clear, actionable advice.
          </p>
          
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 animate-in fade-in slide-in-from-bottom-16 duration-1000 delay-200">
            <Link 
              href="/chat"
              className="px-8 py-4 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl font-semibold transition-all hover:scale-105 shadow-xl shadow-indigo-900/20 flex items-center gap-2"
            >
              Enter the Brain
              <ArrowRight className="w-4 h-4" />
            </Link>
            <a 
              href="https://github.com/kianis4/Delta-Hacks-12" 
              target="_blank"
              rel="noopener noreferrer"
              className="px-8 py-4 bg-white/5 hover:bg-white/10 text-white rounded-xl font-semibold border border-white/10 transition-all hover:border-white/20"
            >
              View Source
            </a>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="py-24 bg-slate-900/50 border-y border-white/5">
        <div className="max-w-7xl mx-auto px-6 grid md:grid-cols-3 gap-8">
            <FeatureCard 
                icon={<Database className="w-6 h-6 text-indigo-400" />}
                title="Massive Legal Knowledge"
                desc="Ingested over 8,000 legal documents including the Criminal Code, Divorce Act, and Tenancy Acts across ON, BC, and AB."
            />
            <FeatureCard 
                icon={<Shield className="w-6 h-6 text-emerald-400" />}
                title="Privacy First RAG"
                desc="Built with LangGraph architecture to ensure your data stays secure while retrieving precise, cited legal references."
            />
             <FeatureCard 
                icon={<Terminal className="w-6 h-6 text-amber-400" />}
                title="Agentic Workflows"
                desc="Not just a chatbot. Mike Ross can research, reason, draft documents, and find specific forms autonomously."
            />
        </div>
      </section>

      {/* Team Section */}
      <section className="py-20 text-center">
        <div className="max-w-7xl mx-auto px-6">
            <h2 className="text-2xl font-bold mb-12">Built for DeltaHacks 12</h2>
            <div className="flex justify-center gap-12">
                <div className="flex flex-col items-center gap-3">
                    <div className="w-16 h-16 bg-slate-800 rounded-full flex items-center justify-center border border-slate-700">
                        <Users className="w-8 h-8 text-slate-400" />
                    </div>
                    <div>
                        <div className="font-semibold">Suleyman Kiani</div>
                        <div className="text-sm text-slate-500">Full Stack Engineer</div>
                    </div>
                </div>
                <div className="flex flex-col items-center gap-3">
                    <div className="w-16 h-16 bg-slate-800 rounded-full flex items-center justify-center border border-slate-700">
                        <Users className="w-8 h-8 text-slate-400" />
                    </div>
                    <div>
                        <div className="font-semibold">Karim Elbasiouni</div>
                        <div className="text-sm text-slate-500">AI Engineer</div>
                    </div>
                </div>
            </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 text-center text-slate-600 text-sm border-t border-white/5">
        <p>© 2026 Mike Ross AI. Not a substitute for professional legal advice.</p>
      </footer>
    </main>
  );
}

function FeatureCard({ icon, title, desc }: { icon: React.ReactNode, title: string, desc: string }) {
    return (
        <div className="p-8 rounded-2xl bg-white/5 border border-white/5 hover:border-indigo-500/30 transition-colors">
            <div className="mb-4">{icon}</div>
            <h3 className="text-xl font-bold mb-3">{title}</h3>
            <p className="text-slate-400 leading-relaxed">{desc}</p>
        </div>
    )
}
