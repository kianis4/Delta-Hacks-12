'use client';

import { useState, useRef, useEffect } from 'react';
import { Send, AlertTriangle, Scale, FileText } from 'lucide-react';
import { cn } from '@/lib/utils';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface Message {
  role: 'user' | 'assistant';
  content: str;
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([
    { role: 'assistant', content: 'Hello! I am Juris. I can help you understand your rights under the Residential Tenancies Act. What situation are you facing?' }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [disclaimerAccepted, setDisclaimerAccepted] = useState(false);
  const [threadId, setThreadId] = useState('');

  useEffect(() => {
    // Generate a random thread ID on mount
    setThreadId(crypto.randomUUID());
  }, []);

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMsg = { role: 'user', content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    try {
      // Connect to backend with persistent thread_id
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          message: input,
          thread_id: threadId 
        })
      });
      const data = await response.json();
      
      setMessages(prev => [...prev, { role: 'assistant', content: data.response }]);
    } catch (error) {
      console.error(error);
      setMessages(prev => [...prev, { role: 'assistant', content: "I'm sorry, I'm having trouble connecting to my legal brain right now. Please make sure the backend server is running." }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen flex-col bg-slate-50">
      {/* Disclaimer Modal */}
      {!disclaimerAccepted && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-white max-w-lg w-full rounded-xl shadow-2xl overflow-hidden border border-red-200">
            <div className="bg-red-50 p-6 border-b border-red-100 flex items-center gap-3">
              <div className="p-3 bg-red-100 rounded-full">
                <AlertTriangle className="w-6 h-6 text-red-600" />
              </div>
              <h2 className="text-xl font-bold text-red-900">Legal Disclaimer</h2>
            </div>
            <div className="p-6 space-y-4">
              <p className="text-slate-700 leading-relaxed">
                <strong>Juris is an AI research tool, NOT a lawyer.</strong>
              </p>
              <p className="text-slate-600 text-sm">
                This system produces drafts and information for educational purposes only. It may hallucinate or provide incorrect legal citations.
              </p>
              <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-100 text-sm text-yellow-800">
                You must verify all information with a qualified legal professional before taking any action (e.g., filing forms, withholding rent).
              </div>
            </div>
            <div className="p-6 bg-slate-50 border-t border-slate-100 flex justify-end">
              <button 
                onClick={() => setDisclaimerAccepted(true)}
                className="bg-red-600 hover:bg-red-700 text-white px-6 py-2.5 rounded-lg font-medium transition-colors shadow-sm"
              >
                I Understand & Accept Liability
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Header */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="bg-indigo-600 p-2 rounded-lg">
              <Scale className="w-5 h-5 text-white" />
            </div>
            <span className="font-bold text-xl text-slate-900">Juris</span>
            <span className="px-2 py-0.5 bg-indigo-50 text-indigo-700 text-xs font-medium rounded-full border border-indigo-100">Beta</span>
          </div>
          <div className="text-sm text-slate-500 hidden sm:block">
            Powered by <strong>Voyage AI</strong> & <strong>Gemini</strong>
          </div>
        </div>
      </header>

      {/* Chat Area */}
      <div className="flex-1 max-w-4xl w-full mx-auto p-4 space-y-6 pb-32">
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
                <div className="prose prose-sm prose-slate max-w-none prose-headings:font-bold prose-headings:text-slate-900 prose-p:text-slate-700 prose-li:text-slate-700 prose-strong:text-slate-900">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {msg.content}
                  </ReactMarkdown>
                </div>
              )}
              {msg.role === 'assistant' && (
                <div className="mt-3 pt-3 border-t border-slate-100 flex gap-4 text-xs text-slate-400">
                  <span className="flex items-center gap-1"><FileText className="w-3 h-3" /> citing RTA 2006</span>
                </div>
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
            className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-4 pr-14 resize-none focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all max-h-48"
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
      </div>
    </main>
  );
}
