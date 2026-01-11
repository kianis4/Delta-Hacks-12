'use client';

import { useState, useRef, useEffect } from 'react';
import { Send, AlertTriangle, Scale, FileText, Download, Gavel, UserCheck, Briefcase } from 'lucide-react';
import { cn } from '@/lib/utils';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

  interface Message {
    role: 'user' | 'assistant';
    content: string;
    debug_info?: any[];
  }

  export default function Home() {
    const [messages, setMessages] = useState<Message[]>([
      { role: 'assistant', content: 'Mike Ross here. I’ve memorized every law book in the database. What aspect of the law can I help you exploit... I mean, understand, today?' }
    ]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [disclaimerAccepted, setDisclaimerAccepted] = useState(false);
    const [threadId, setThreadId] = useState('');
    const [saulMode, setSaulMode] = useState(false);
    const [showToast, setShowToast] = useState(false);

    useEffect(() => {
      setThreadId(crypto.randomUUID());
    }, []);

    const handleSaulToggle = () => {
        // The law has no room for shenanigans ;)
        setSaulMode(true); // Visually toggle it maybe? No, let's keep it off or just flash it.
        // Actually user said: "when they toggle it on nothing actually happens" 
        // implies the visual toggle might move but the effect is the quote.
        // Let's toggle the state but reset it or just show the toast.
        setShowToast(true);
        setTimeout(() => setShowToast(false), 4000);
        setTimeout(() => setSaulMode(false), 300); // Reset toggle back to off for effect
    };

    /* ... sendMessage and renderMessageContent ... */
    /* (Insert standard logic here if rewriting whole file, but we are chunking) */
    
    // ... sendMessage function ...
    const sendMessage = async () => {
        if (!input.trim() || isLoading) return;
    
        const userMsg: Message = { role: 'user', content: input };
        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setIsLoading(true);
    
        try {
          // Connect to backend with persistent thread_id
          const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
          const response = await fetch(`${apiUrl}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
              message: input,
              thread_id: threadId 
            })
          });
          const data = await response.json();
          
          setMessages(prev => [...prev, { 
              role: 'assistant', 
              content: data.response,
              debug_info: data.debug_info 
          }]);
        } catch (error) {
          console.error(error);
          setMessages(prev => [...prev, { role: 'assistant', content: "I'm sorry, I'm having trouble connecting to my legal brain right now. Please make sure the backend server is running." }]);
        } finally {
          setIsLoading(false);
        }
      };

    /* ... Structured Response Interfaces ... */
    interface StructuredResponse {
        explanation: string;
        citations?: (string | { text: string; url?: string })[];
        options?: { label: string; action: string; description: string }[];
        draft?: string;
    }

    /* ... renderMessageContent ... */
    const renderMessageContent = (content: string) => {
        let parsed: StructuredResponse | null = null;
        try {
          parsed = JSON.parse(content);
        } catch (e) {
          // Not JSON
        }
    
        if (!parsed) {
          return (
            <div className="prose prose-sm prose-slate max-w-none prose-headings:font-bold prose-headings:text-slate-900 prose-p:text-slate-700 prose-li:text-slate-700 prose-strong:text-slate-900">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {content}
              </ReactMarkdown>
            </div>
          );
        }
    
        const handleDownloadPdf = async (text: string) => {
             /* ... existing pdf logic ... */
              try {
                const response = await fetch('http://localhost:8000/generate-pdf', {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({ text })
                });
                
                if (!response.ok) throw new Error('PDF Generation Failed');
                
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = "Juris_Legal_Draft.pdf";
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
              } catch (e) {
                console.error(e);
                alert("Failed to generate PDF. Please try again.");
              }
        };
    
        return (
          <div className="space-y-4">
            {/* Explanation */}
            <div className="prose prose-sm prose-slate max-w-none">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {parsed.explanation}
              </ReactMarkdown>
            </div>
    

    
            {/* Citations Section */}
        {parsed.citations && parsed.citations.length > 0 && (
          <div className="mt-4 pt-4 border-t border-slate-100 bg-slate-50/50 rounded-lg p-3">
            <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2 flex items-center gap-1">
              <Scale className="w-3 h-3" />
              Sources Cited
            </h4>
            <ul className="space-y-3">
              {parsed.citations.map((cit: any, i: number) => (
                  <li key={i} className="text-sm border-l-2 border-indigo-400 pl-3">
                    <div className="font-semibold text-slate-900">
                      {cit.source_title}
                    </div>
                    <div className="text-slate-600 italic mt-1 text-xs">
                      "{cit.quote}"
                    </div>
                    {cit.url && (
                      <a 
                        href={cit.url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1 text-indigo-600 hover:text-indigo-800 text-xs mt-1 font-medium hover:underline"
                      >
                        <Download className="w-3 h-3" />
                        View Official Source
                      </a>
                    )}
                  </li>
              ))}
            </ul>
          </div>
        )}

        {/* Action Options */}
            {parsed.options && parsed.options.length > 0 && (
              <div className="grid gap-2 mt-4">
                {parsed.options.map((opt, i) => (
                  <button
                    key={i}
                    onClick={() => {
                       if (opt.action.startsWith('http')) {
                           window.open(opt.action, '_blank');
                       } else {
                           setInput(`I select: ${opt.label}`);
                           sendMessage(); // Clean follow up
                       }
                    }}
                    className="text-left group p-3 rounded-xl border border-indigo-100 bg-white hover:border-indigo-300 hover:shadow-md transition-all flex items-start gap-3"
                  >
                    <div className="mt-1 p-1.5 bg-indigo-50 text-indigo-600 rounded-lg group-hover:bg-indigo-600 group-hover:text-white transition-colors">
                      <Send className="w-3 h-3" />
                    </div>
                    <div>
                      <div className="font-semibold text-slate-900 text-sm">{opt.label}</div>
                      <div className="text-xs text-slate-500 line-clamp-1">{opt.description}</div>
                    </div>
                  </button>
                ))}
              </div>
            )}
    
            {/* Magic Draft Button */}
            {parsed.draft && (
              <div className="mt-6 pt-4 border-t border-slate-100 animate-in fade-in slide-in-from-bottom-4 duration-500">
                 <button
                    onClick={() => handleDownloadPdf(parsed.draft!)}
                    className="w-full flex items-center justify-center gap-2 bg-slate-900 hover:bg-slate-800 text-white p-4 rounded-xl shadow-lg hover:shadow-xl transition-all group"
                 >
                    <div className="p-2 bg-white/10 rounded-lg group-hover:scale-110 transition-transform">
                      <Download className="w-5 h-5" />
                    </div>
                    <div className="text-left">
                      <div className="font-bold text-sm">Download Official Notice</div>
                      <div className="text-xs text-slate-400">PDF Format • Ready to Print</div>
                    </div>
                 </button>
              </div>
            )}
          </div>
        );
      };

    return (
    <main className="flex min-h-screen flex-col bg-slate-50 relative">
      {/* Toast Notification */}
      {showToast && (
          <div className="fixed top-20 right-4 z-[60] animate-in fade-in slide-in-from-right-10 duration-300">
             <div className="bg-slate-900 text-white px-6 py-4 rounded-lg shadow-2xl flex items-center gap-4 border border-slate-700 max-w-sm">
                 <div className="text-2xl">⚖️</div>
                 <div>
                     <p className="font-bold text-sm text-yellow-500">Access Denied</p>
                     <p className="text-xs text-slate-300 italic">"The law is a particular endeavour and has no room for shenanigans ;)"</p>
                 </div>
             </div>
          </div>
      )}

      {/* Disclaimer Modal */}
      {!disclaimerAccepted && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-white max-w-lg w-full rounded-xl shadow-2xl overflow-hidden border border-slate-200">
            <div className="bg-slate-900 p-6 border-b border-slate-800 flex items-center gap-3">
              <div className="p-3 bg-slate-800 rounded-full">
                <Briefcase className="w-6 h-6 text-white" />
              </div>
              <h2 className="text-xl font-bold text-white">Mike Ross Juris</h2>
            </div>
            <div className="p-6 space-y-4">
              <p className="text-slate-700 leading-relaxed font-medium">
                "I don't play the odds, I play the man."
              </p>
              <p className="text-slate-600 text-sm">
                ...But in this case, I'm an AI. I have read every law in the database, but I am not a real lawyer. Do not rely on me for life-or-death advice without verifying it first. Oh Yea... and if anyone asks... I want to Harvard...
              </p>
              <div className="bg-blue-50 p-4 rounded-lg border border-blue-100 text-sm text-blue-800">
                Verify all information with a qualified legal professional.
              </div>
            </div>
            <div className="p-6 bg-slate-50 border-t border-slate-100 flex justify-end">
              <button 
                onClick={() => setDisclaimerAccepted(true)}
                className="bg-slate-900 hover:bg-slate-800 text-white px-6 py-2.5 rounded-lg font-medium transition-colors shadow-sm"
              >
                I Understand
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Header */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-10 shadow-sm">
        <div className="max-w-5xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="bg-slate-900 p-2 rounded-lg shadow-lg">
              <Briefcase className="w-5 h-5 text-white" />
            </div>
            <div className="flex flex-col">
                <span className="font-bold text-lg text-slate-900 leading-tight">Mike Ross Juris</span>
                <span className="text-[10px] text-slate-500 font-medium">Pearson Specter Litt AI Division</span>
            </div>
          </div>
          
          <div className="flex items-center gap-6">
              {/* Saul Goodman Toggle */}
              <div className="hidden sm:flex items-center gap-2 cursor-pointer group" onClick={handleSaulToggle}>
                  <span className={cn("text-xs font-bold transition-colors", saulMode ? "text-yellow-600" : "text-slate-400 group-hover:text-slate-600")}>SAUL GOODMAN MODE</span>
                  <div className={cn("w-10 h-5 rounded-full relative transition-colors duration-300", saulMode ? "bg-yellow-400" : "bg-slate-200")}>
                      <div className={cn("absolute top-0.5 w-4 h-4 bg-white rounded-full shadow-sm transition-transform duration-300", saulMode ? "left-5.5" : "left-0.5")} />
                  </div>
              </div>
          </div>
        </div>
      </header>

      {/* Chat Area */}
      <div className="flex-1 max-w-4xl w-full mx-auto p-4 space-y-6 pb-48">
        {messages.map((msg, idx) => (
          <div key={idx} className={cn("flex gap-4", msg.role === 'user' ? "justify-end" : "justify-start")}>
            <div className={cn(
              "max-w-[85%] rounded-2xl p-4 shadow-sm",
              msg.role === 'user' 
                ? "bg-indigo-600 text-white rounded-br-none" 
                : "bg-white border border-slate-200 text-slate-800 rounded-bl-none"
            )}>
              {msg.role === 'user' ? (
                <p className="leading-relaxed whitespace-pre-wrap">{msg.content}</p>
              ) : (
                renderMessageContent(msg.content)
              )}
            </div>
          </div>
        ))}
        {isLoading && (
           <div className="flex gap-4 justify-start">
             <div className="bg-white border border-slate-200 rounded-2xl rounded-bl-none p-4 shadow-sm">
               <div className="flex gap-1">
                 <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" />
                 <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce [animation-delay:0.2s]" />
                 <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce [animation-delay:0.4s]" />
               </div>
               <span className="text-xs text-slate-400 mt-2 block">Researching case law...</span>
             </div>
           </div>
        )}
        {/* Scope / Capabilities Cards - Only show on start */}
        {messages.length === 1 && !isLoading && (
          <div className="max-w-4xl mx-auto px-1 grid grid-cols-1 md:grid-cols-3 gap-4 mt-8">
            <button 
              onClick={() => setInput("My tenant is damaging the rental unit. I need to evict them. Get me the N5 form.")}
              className="text-left bg-white p-6 rounded-xl border border-slate-200 shadow-sm hover:border-slate-300 hover:shadow-lg transition-all group hover:-translate-y-1"
            >
              <h3 className="font-semibold text-slate-900 mb-2 flex items-center gap-2">
                <div className="p-2 bg-slate-100 text-slate-700 rounded-lg group-hover:bg-slate-900 group-hover:text-white transition-colors">
                    <FileText className="w-5 h-5" />
                </div>
                Smart Form Finder
              </h3>
              <p className="text-sm text-slate-500">
                "Get me the N12 form." <br/>
                "I need the divorce application form."
              </p>
            </button>
            
            <button 
              onClick={() => setInput("My wife cheated on me and I need a divorce. Can I keep the house?")}
              className="text-left bg-white p-6 rounded-xl border border-slate-200 shadow-sm hover:border-slate-300 hover:shadow-lg transition-all group hover:-translate-y-1"
            >
              <h3 className="font-semibold text-slate-900 mb-2 flex items-center gap-2">
                <div className="p-2 bg-slate-100 text-slate-700 rounded-lg group-hover:bg-slate-900 group-hover:text-white transition-colors">
                    <Gavel className="w-5 h-5" />
                </div>
                Complex Legal Drafts
              </h3>
              <p className="text-sm text-slate-500">
                "Draft me a demand letter for unpaid wages." <br/>
                "My wife cheated on me, I need a divorce."
              </p>
            </button>

            <button 
              onClick={() => setInput("Find a criminal lawyer in Toronto.")}
              className="text-left bg-white p-6 rounded-xl border border-slate-200 shadow-sm hover:border-slate-300 hover:shadow-lg transition-all group hover:-translate-y-1"
            >
              <h3 className="font-semibold text-slate-900 mb-2 flex items-center gap-2">
                <div className="p-2 bg-slate-100 text-slate-700 rounded-lg group-hover:bg-slate-900 group-hover:text-white transition-colors">
                    <UserCheck className="w-5 h-5" />
                </div>
                Find Representation
              </h3>
              <p className="text-sm text-slate-500">
                "Find a top rated criminal lawyer in Toronto." <br/>
                "I need Legal Aid in Ottawa."
              </p>
            </button>
          </div>
        )}
      </div>



      {/* Input Area */}
      <div className="fixed bottom-0 left-0 right-0 bg-white/80 backdrop-blur-md border-t border-slate-200 p-4">
        <div className="max-w-4xl mx-auto relative">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
              }
            }}
            placeholder="Describe your situation (e.g., 'My landlord sent me an N12 eviction notice...')"
            className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-4 pr-14 resize-none focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all max-h-48 text-slate-900 placeholder:text-slate-400"
            rows={1}
            disabled={!disclaimerAccepted}
          />
          <button 
            onClick={sendMessage}
            disabled={!input.trim() || isLoading || !disclaimerAccepted}
            className="absolute right-3 top-3 p-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:hover:bg-indigo-600 transition-colors"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
        <p className="text-center text-xs text-slate-400 mt-2">
          Juris can make mistakes. Check important info.
        </p>
        
        {/* Debug Panel Toggle */}
        <details className="max-w-4xl mx-auto mt-4 text-xs text-slate-400 cursor-pointer">
            <summary>Debug Console (Raw Backend Logic)</summary>
            <div className="mt-2 p-4 bg-slate-900 text-green-400 rounded-xl border border-slate-700 overflow-auto max-h-96 font-mono shadow-2xl">
                {messages.map((m, i) => (
                    <div key={i} className="mb-4 border-b border-slate-800 pb-2">
                        <div className="text-white font-bold mb-1">[{m.role.toUpperCase()}]</div>
                        <div className="opacity-80 break-words">{m.content}</div>
                        {(m as any).debug_info && (
                             <div className="mt-2 pl-4 border-l-2 border-yellow-500">
                                <div className="text-yellow-500 font-bold mb-1">⚡ Node Execution Trace:</div>
                                {((m as any).debug_info).map((log: any, j: number) => (
                                    <div key={j} className="mb-2">
                                        <div className="text-blue-400">Step: {log.node} ({log.step || 'output'})</div>
                                        {log.raw_output && (
                                            <details>
                                                <summary className="cursor-pointer text-slate-500 hover:text-slate-300">Raw Source Output</summary>
                                                <div className="p-2 bg-black rounded mt-1 whitespace-pre-wrap">{log.raw_output}</div>
                                            </details>
                                        )}
                                        {log.error && <div className="text-red-500 font-bold">ERROR: {log.error}</div>}
                                    </div>
                                ))}
                             </div>
                        )}
                    </div>
                ))}
            </div>
        </details>
      </div>
    </main>
  );
}
