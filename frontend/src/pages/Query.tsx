import { useState, useRef, useEffect } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Send, MessageSquare, FileText, Loader2, Bot, User, Sparkles } from 'lucide-react';
import { Button, Input } from '@/components/ui';
import apiClient, { getApiErrorMessage } from '@/lib/api';
import { cn } from '@/lib/utils';

interface Citation {
  document_id: string;
  document_filename: string | null;
  chunk_id: string | null;
  page_number: number | null;
  section_header: string | null;
  excerpt: string;
  relevance_score: number;
}

interface Message {
  role: 'user' | 'assistant';
  content: string;
  citations?: Citation[];
  timestamp: Date;
}

interface QueryResponse {
  query_id: string;
  question: string;
  answer: string;
  confidence_score: number;
  citations: Citation[];
  limitations: string | null;
  conversation_id: string | null;
  chunks_retrieved: number;
  response_time_ms: number;
}

interface QueryPayload {
  question: string;
  max_chunks: number;
  conversation_id?: string;
}

export function Query() {
  const [question, setQuestion] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const queryMutation = useMutation({
    mutationFn: async (q: string) => {
      const payload: QueryPayload = {
        question: q,
        max_chunks: 10,
      };

      if (conversationId) {
        payload.conversation_id = conversationId;
      }

      const response = await apiClient.post<QueryResponse>('/query', payload);
      return response.data;
    },
    onSuccess: (data) => {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: data.answer,
          citations: data.citations,
          timestamp: new Date(),
        },
      ]);

      if (data.conversation_id && !conversationId) {
        setConversationId(data.conversation_id);
      }

      setError(null);
    },
    onError: (err) => {
      setError(getApiErrorMessage(err));
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim() || queryMutation.isPending) return;

    setMessages((prev) => [
      ...prev,
      {
        role: 'user',
        content: question,
        timestamp: new Date(),
      },
    ]);

    queryMutation.mutate(question);
    setQuestion('');
  };

  const startNewConversation = () => {
    setMessages([]);
    setConversationId(null);
    setError(null);
  };

  return (
    <div className="flex h-[calc(100vh-8rem)] flex-col glass-panel rounded-xl overflow-hidden border border-white/10 shadow-2xl relative">
      {/* Header */}
      <div className="border-b border-white/10 p-4 flex items-center justify-between bg-black/20 backdrop-blur-md">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-lg bg-primary/10 border border-primary/20 flex items-center justify-center shadow-[0_0_10px_rgba(0,242,255,0.2)]">
            <Sparkles className="h-5 w-5 text-primary animate-pulse" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-white neon-text">Neural Query Interface</h1>
            <p className="text-xs text-primary/80 font-mono tracking-wider">
              AI-POWERED • SECURE • CITED
            </p>
          </div>
        </div>
        {messages.length > 0 && (
          <Button
            variant="outline"
            onClick={startNewConversation}
            className="border-white/10 hover:bg-white/5 hover:text-primary hover:border-primary/50 transition-all font-mono text-xs uppercase"
          >
            Reset Link
          </Button>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-auto p-4 space-y-6 custom-scrollbar scroll-smooth" ref={scrollRef}>
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center p-8">
            <div className="h-24 w-24 rounded-full bg-primary/5 border border-primary/10 flex items-center justify-center mb-6 shadow-[0_0_30px_rgba(0,242,255,0.1)] animate-float">
              <MessageSquare className="h-10 w-10 text-primary/50" />
            </div>
            <h2 className="text-2xl font-bold mb-2 text-white">Awaiting Input</h2>
            <p className="text-muted-foreground max-w-md mb-8">
              Initialize query sequence. ask questions about your uploaded documents or compliance frameworks.
            </p>
            <div className="grid gap-3 text-sm w-full max-w-md">
              {[
                "What encryption standards does this vendor use?",
                "Are there any gaps in access control?",
                "Summarize the incident response procedures"
              ].map((q, i) => (
                <button
                  key={i}
                  onClick={() => setQuestion(q)}
                  className="text-left px-4 py-3 rounded-lg border border-white/5 bg-white/5 hover:bg-white/10 hover:border-primary/30 transition-all duration-300 group flex items-center justify-between"
                >
                  <span className="text-muted-foreground group-hover:text-white transition-colors">{q}</span>
                  <Send className="h-3 w-3 text-primary/0 group-hover:text-primary transition-all transform translate-x-3 group-hover:translate-x-0" />
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((message, index) => (
            <div
              key={index}
              className={`flex gap-4 ${message.role === 'user' ? 'justify-end' : 'justify-start'} animate-fade-in-up`}
            >
              {message.role === 'assistant' && (
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-black/40 border border-primary/30 shadow-[0_0_10px_rgba(0,242,255,0.2)] mt-1">
                  <Bot className="h-4 w-4 text-primary" />
                </div>
              )}

              <div
                className={cn(
                  "max-w-[85%] rounded-2xl p-5 shadow-lg relative overflow-hidden",
                  message.role === 'user'
                    ? "bg-primary text-primary-foreground rounded-tr-sm"
                    : "bg-white/5 border border-white/10 text-white rounded-tl-sm backdrop-blur-sm"
                )}
              >
                {/* User Message Glow */}
                {message.role === 'user' && (
                  <div className="absolute inset-0 bg-gradient-to-tr from-transparent via-white/10 to-transparent pointer-events-none" />
                )}

                <p className="whitespace-pre-wrap leading-relaxed relative z-10">{message.content}</p>

                {/* Citations */}
                {message.citations && message.citations.length > 0 && (
                  <div className="mt-4 pt-4 border-t border-white/10 relative z-10">
                    <p className="text-[10px] font-bold uppercase tracking-wider text-primary/80 mb-3 flex items-center gap-1">
                      <FileText className="h-3 w-3" />
                      Verified Sources
                    </p>
                    <div className="space-y-2">
                      {message.citations.slice(0, 3).map((citation, i) => (
                        <div
                          key={i}
                          className="text-xs p-3 rounded-lg bg-black/20 border border-white/5 flex items-start gap-3 hover:bg-black/40 hover:border-primary/20 transition-colors cursor-help"
                        >
                          <div className="h-5 w-5 rounded bg-primary/10 flex items-center justify-center shrink-0 border border-primary/20">
                            <span className="text-[10px] font-mono text-primary">{i + 1}</span>
                          </div>
                          <div>
                            <p className="font-semibold text-primary/90 mb-1">
                              {citation.document_filename || 'Unknown Document'}
                              {citation.page_number && <span className="text-white/40 font-normal ml-1">p.{citation.page_number}</span>}
                            </p>
                            <p className="text-white/60 line-clamp-2 leading-relaxed italic">"{citation.excerpt}"</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {message.role === 'user' && (
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-secondary text-white mt-1 shadow-[0_0_10px_rgba(176,38,255,0.3)]">
                  <User className="h-4 w-4" />
                </div>
              )}
            </div>
          ))
        )}

        {/* Loading indicator */}
        {queryMutation.isPending && (
          <div className="flex gap-4 animate-pulse">
            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-black/40 border border-primary/30 mt-1">
              <Bot className="h-4 w-4 text-primary" />
            </div>
            <div className="bg-white/5 border border-white/10 rounded-2xl rounded-tl-sm px-5 py-4 flex items-center gap-3">
              <Loader2 className="h-4 w-4 animate-spin text-primary" />
              <span className="text-sm text-primary font-mono tracking-wider">ANALYZING DATA STREAMS...</span>
            </div>
          </div>
        )}

        {/* Error message */}
        {error && (
          <div className="rounded-lg bg-red-500/10 border border-red-500/20 p-4 text-sm text-red-400 flex items-center gap-2 animate-in fade-in slide-in-from-bottom-2">
            <span className="font-bold">ERROR:</span> {error}
          </div>
        )}
      </div>

      {/* Input */}
      <div className="border-t border-white/10 p-4 bg-black/20 backdrop-blur-md">
        <form onSubmit={handleSubmit} className="flex gap-3 relative">
          <Input
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Input query parameters..."
            className="flex-1 bg-black/20 border-white/10 focus:border-primary/50 focus:ring-primary/20 h-12 pl-4 pr-12 font-medium placeholder:text-muted-foreground/50 transition-all"
            disabled={queryMutation.isPending}
          />
          <Button
            type="submit"
            disabled={!question.trim() || queryMutation.isPending}
            className={cn(
              "absolute right-2 top-2 h-8 w-8 p-0 rounded-lg transition-all duration-300",
              question.trim() ? "bg-primary text-black hover:bg-primary/90 shadow-[0_0_10px_rgba(0,242,255,0.4)]" : "bg-white/5 text-white/20 hover:bg-white/10"
            )}
          >
            <Send className="h-4 w-4" />
          </Button>
        </form>
        <div className="mt-2 flex justify-between items-center px-1">
          <p className="text-[10px] text-muted-foreground font-mono">
            SECURE CONNECTION ESTABLISHED
          </p>
          <div className="flex gap-1">
            <span className="h-1 w-1 rounded-full bg-primary animate-pulse py-0.5"></span>
            <span className="h-1 w-1 rounded-full bg-primary animate-pulse delay-100 py-0.5"></span>
            <span className="h-1 w-1 rounded-full bg-primary animate-pulse delay-200 py-0.5"></span>
          </div>
        </div>
      </div>
    </div>
  );
}
