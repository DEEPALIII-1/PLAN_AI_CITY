import React, { useState } from 'react';
import { 
  Bot, User, Send, Sparkles, ShieldCheck, ChevronDown, 
  ChevronUp, CheckCircle, FileText, ExternalLink, Lightbulb
} from 'lucide-react';
import { City, AgentStep, RAGCitation } from '../types';
import { api } from '../services/api';

interface Message {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  intent?: string;
  agentsInvolved?: string[];
  agentSteps?: AgentStep[];
  citations?: RAGCitation[];
  suggestedActions?: string[];
  timestamp: string;
}

interface AIChatAssistantViewProps {
  currentCity: City | null;
  initialPrompt?: string;
}

export const AIChatAssistantView: React.FC<AIChatAssistantViewProps> = ({
  currentCity,
  initialPrompt,
}) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      sender: 'assistant',
      text: `Hello! I am your **Plan AI City Assistant** for **${currentCity?.name || 'Shimla'}**.\n\nI combine Retrieval-Augmented Generation (RAG) and specialized multi-agents to help you plan trips, discover places, and answer factual questions using verified municipal and tourism documents.\n\nTry asking me:\n- *"What can I do in Shimla in one day under ₹1500?"*\n- *"Is Viceregal Lodge suitable for a family with children?"*\n- *"Recommend cozy rooftop cafés with mountain views."*`,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      suggestedActions: [
        `Plan 1 day in ${currentCity?.name || 'Shimla'} under ₹1500`,
        `Is Viceregal Lodge child friendly?`,
        `Top rated cafés on Mall Road`,
      ]
    }
  ]);

  const [input, setInput] = useState(initialPrompt || '');
  const [loading, setLoading] = useState(false);
  const [expandedSteps, setExpandedSteps] = useState<Record<string, boolean>>({});

  const toggleSteps = (msgId: string) => {
    setExpandedSteps(prev => ({ ...prev, [msgId]: !prev[msgId] }));
  };

  const handleSend = async (messageText?: string) => {
    const textToSend = messageText || input;
    if (!textToSend.trim() || loading) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      sender: 'user',
      text: textToSend,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const response = await api.chatWithAgents(textToSend, currentCity?.id);
      
      const assistantMsg: Message = {
        id: (Date.now() + 1).toString(),
        sender: 'assistant',
        text: response.reply,
        intent: response.intent_detected,
        agentsInvolved: response.agents_involved,
        agentSteps: response.agent_steps,
        citations: response.citations,
        suggestedActions: response.suggested_actions,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };

      setMessages(prev => [...prev, assistantMsg]);
    } catch (err) {
      console.error(err);
      const errorMsg: Message = {
        id: (Date.now() + 1).toString(),
        sender: 'assistant',
        text: "I encountered an issue processing your query. Please make sure the backend server is running and try again.",
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      {/* Header */}
      <div className="flex items-center justify-between pb-4 mb-4 border-b border-slate-800">
        <div>
          <h2 className="text-xl sm:text-2xl font-extrabold text-white flex items-center gap-2">
            <Bot className="w-6 h-6 text-emerald-400" />
            <span>AI City Assistant</span>
            <span className="text-xs bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 px-2.5 py-0.5 rounded-full font-bold">
              Multi-Agent + RAG
            </span>
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Active city: <strong className="text-white">{currentCity?.name}</strong> • Answers verified against municipal records
          </p>
        </div>
      </div>

      {/* Messages Scroll Area */}
      <div className="space-y-6 mb-6 min-h-[460px] max-h-[600px] overflow-y-auto pr-2">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex flex-col ${msg.sender === 'user' ? 'items-end' : 'items-start'}`}
          >
            <div className="flex items-start gap-3 max-w-3xl">
              {msg.sender === 'assistant' && (
                <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-indigo-600 to-emerald-400 flex items-center justify-center text-white shrink-0 shadow-md">
                  <Bot className="w-4 h-4" />
                </div>
              )}

              <div
                className={`rounded-2xl p-4 sm:p-5 text-sm leading-relaxed ${
                  msg.sender === 'user'
                    ? 'bg-indigo-600 text-white rounded-tr-none shadow-md shadow-indigo-600/20'
                    : 'bg-slate-900 border border-slate-800 text-slate-200 rounded-tl-none shadow-lg'
                }`}
              >
                {/* Agent & Intent Badges for Assistant */}
                {msg.sender === 'assistant' && msg.agentsInvolved && (
                  <div className="flex flex-wrap items-center gap-1.5 mb-3 pb-2.5 border-b border-slate-800 text-[11px]">
                    <span className="font-semibold text-slate-400">Agents:</span>
                    {msg.agentsInvolved.map((agent, i) => (
                      <span key={i} className="bg-slate-800 text-indigo-300 px-2 py-0.5 rounded-md font-medium">
                        {agent}
                      </span>
                    ))}
                    {msg.intent && (
                      <span className="ml-auto text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded-md font-bold">
                        {msg.intent}
                      </span>
                    )}
                  </div>
                )}

                {/* Message Body */}
                <div className="whitespace-pre-line space-y-2">
                  {msg.text}
                </div>

                {/* Multi-Agent Transparent Steps Accordion */}
                {msg.agentSteps && msg.agentSteps.length > 0 && (
                  <div className="mt-4 pt-3 border-t border-slate-800">
                    <button
                      onClick={() => toggleSteps(msg.id)}
                      className="flex items-center justify-between w-full text-xs font-semibold text-slate-400 hover:text-indigo-300 py-1"
                    >
                      <span className="flex items-center gap-1.5">
                        <Sparkles className="w-3.5 h-3.5 text-amber-400" />
                        Multi-Agent Execution Log ({msg.agentSteps.length} steps)
                      </span>
                      {expandedSteps[msg.id] ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                    </button>

                    {expandedSteps[msg.id] && (
                      <div className="mt-2 space-y-2 bg-slate-950/60 p-3 rounded-xl border border-slate-800/80 text-xs">
                        {msg.agentSteps.map((step, sIdx) => (
                          <div key={sIdx} className="flex items-start gap-2">
                            <CheckCircle className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
                            <div>
                              <strong className="text-white">{step.agent_name}:</strong>{' '}
                              <span className="text-slate-300">{step.action_taken}</span>
                              <div className="text-[10px] text-slate-500">
                                Confidence: {(step.confidence * 100).toFixed(0)}%
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                {/* Verified Citations Drawer */}
                {msg.citations && msg.citations.length > 0 && (
                  <div className="mt-4 pt-3 border-t border-slate-800">
                    <div className="text-xs font-bold text-slate-300 mb-2 flex items-center gap-1.5">
                      <ShieldCheck className="w-4 h-4 text-emerald-400" />
                      <span>Verified Sources Cited ({msg.citations.length}):</span>
                    </div>

                    <div className="grid grid-cols-1 gap-2">
                      {msg.citations.map((cit, cIdx) => (
                        <div key={cIdx} className="bg-slate-950/80 border border-slate-800 p-2.5 rounded-xl text-xs">
                          <div className="flex items-center justify-between mb-1">
                            <span className="font-bold text-white flex items-center gap-1">
                              <FileText className="w-3.5 h-3.5 text-indigo-400" />
                              {cit.title}
                            </span>
                            <span className="text-[10px] font-semibold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full">
                              Score: {cit.relevance_score}
                            </span>
                          </div>
                          <p className="text-[11px] text-slate-400 italic line-clamp-2">
                            "{cit.snippet}"
                          </p>
                          {cit.source_url && (
                            <a 
                              href={cit.source_url} 
                              target="_blank" 
                              rel="noreferrer"
                              className="inline-flex items-center gap-1 text-[10px] text-indigo-400 hover:underline mt-1"
                            >
                              <span>Official Document Source</span>
                              <ExternalLink className="w-3 h-3" />
                            </a>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <div className="mt-2 text-[10px] text-slate-500 text-right">
                  {msg.timestamp}
                </div>
              </div>

              {msg.sender === 'user' && (
                <div className="w-8 h-8 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-300 shrink-0">
                  <User className="w-4 h-4" />
                </div>
              )}
            </div>

            {/* Suggested Follow-up Actions */}
            {msg.suggestedActions && msg.suggestedActions.length > 0 && (
              <div className="flex flex-wrap gap-2 mt-2 ml-11">
                {msg.suggestedActions.map((action, aIdx) => (
                  <button
                    key={aIdx}
                    onClick={() => handleSend(action)}
                    className="text-xs bg-slate-900 hover:bg-slate-800 text-indigo-300 hover:text-white border border-slate-800 hover:border-indigo-500/50 px-3 py-1 rounded-full transition-all"
                  >
                    ↳ {action}
                  </button>
                ))}
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-indigo-600 to-emerald-400 flex items-center justify-center text-white shrink-0 animate-pulse">
              <Bot className="w-4 h-4" />
            </div>
            <div className="bg-slate-900 border border-slate-800 rounded-2xl rounded-tl-none p-4 text-xs text-slate-400 flex items-center gap-3">
              <div className="w-4 h-4 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
              <span>Orchestrating agents and retrieving verified documents...</span>
            </div>
          </div>
        )}
      </div>

      {/* Input Box */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-2 shadow-2xl">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="flex items-center gap-2"
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={`Ask anything about ${currentCity?.name || 'the city'} (e.g. "What can I do in Shimla under ₹1500?")...`}
            className="flex-1 bg-transparent px-4 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none"
          />
          <button
            type="submit"
            disabled={!input.trim() || loading}
            className="bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white p-3 rounded-xl transition-all shadow-md shadow-indigo-600/20"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
};
