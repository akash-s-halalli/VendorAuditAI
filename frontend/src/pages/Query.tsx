import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Send, MessageSquare, FileText, Loader2, Bot, User } from 'lucide-react';
import { Button, Input } from '@/components/ui';
import apiClient, { getApiErrorMessage } from '@/lib/api';

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

    // Add user message
    setMessages((prev) => [
      ...prev,
      {
        role: 'user',
        content: question,
        timestamp: new Date(),
      },
    ]);

    // Send query
    queryMutation.mutate(question);
    setQuestion('');
  };

  const startNewConversation = () => {
    setMessages([]);
    setConversationId(null);
    setError(null);
  };

  return (
    <div className="flex h-full">
      {/* Main chat area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="border-b p-4 flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold">Ask a Question</h1>
            <p className="text-sm text-muted-foreground">
              Query your compliance documents using natural language
            </p>
          </div>
          {messages.length > 0 && (
            <Button variant="outline" onClick={startNewConversation}>
              New Conversation
            </Button>
          )}
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-auto p-4 space-y-4">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <MessageSquare className="h-16 w-16 text-muted-foreground mb-4" />
              <h2 className="text-xl font-medium mb-2">No messages yet</h2>
              <p className="text-muted-foreground max-w-md mb-6">
                Ask questions about your uploaded documents. For example:
              </p>
              <div className="grid gap-2 text-sm">
                <button
                  onClick={() => setQuestion("What encryption standards does this vendor use?")}
                  className="text-left px-4 py-2 rounded-lg border hover:bg-accent transition-colors"
                >
                  "What encryption standards does this vendor use?"
                </button>
                <button
                  onClick={() => setQuestion("Are there any gaps in access control?")}
                  className="text-left px-4 py-2 rounded-lg border hover:bg-accent transition-colors"
                >
                  "Are there any gaps in access control?"
                </button>
                <button
                  onClick={() => setQuestion("Summarize the incident response procedures")}
                  className="text-left px-4 py-2 rounded-lg border hover:bg-accent transition-colors"
                >
                  "Summarize the incident response procedures"
                </button>
              </div>
            </div>
          ) : (
            messages.map((message, index) => (
              <div
                key={index}
                className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {message.role === 'assistant' && (
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary">
                    <Bot className="h-4 w-4 text-primary-foreground" />
                  </div>
                )}
                <div
                  className={`max-w-[80%] rounded-lg px-4 py-3 ${
                    message.role === 'user'
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-muted'
                  }`}
                >
                  <p className="whitespace-pre-wrap">{message.content}</p>

                  {/* Citations */}
                  {message.citations && message.citations.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-border/50">
                      <p className="text-xs font-medium mb-2 opacity-70">Sources:</p>
                      <div className="space-y-2">
                        {message.citations.slice(0, 3).map((citation, i) => (
                          <div
                            key={i}
                            className="text-xs p-2 rounded bg-background/50 flex items-start gap-2"
                          >
                            <FileText className="h-3 w-3 mt-0.5 shrink-0" />
                            <div>
                              <p className="font-medium">
                                {citation.document_filename || 'Document'}
                                {citation.page_number && ` (p. ${citation.page_number})`}
                              </p>
                              <p className="opacity-70 line-clamp-2">{citation.excerpt}</p>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
                {message.role === 'user' && (
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-secondary">
                    <User className="h-4 w-4" />
                  </div>
                )}
              </div>
            ))
          )}

          {/* Loading indicator */}
          {queryMutation.isPending && (
            <div className="flex gap-3">
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary">
                <Bot className="h-4 w-4 text-primary-foreground" />
              </div>
              <div className="bg-muted rounded-lg px-4 py-3">
                <div className="flex items-center gap-2">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span className="text-sm">Searching documents and generating response...</span>
                </div>
              </div>
            </div>
          )}

          {/* Error message */}
          {error && (
            <div className="rounded-md bg-destructive/10 p-3 text-sm text-destructive">
              {error}
            </div>
          )}
        </div>

        {/* Input */}
        <div className="border-t p-4">
          <form onSubmit={handleSubmit} className="flex gap-2">
            <Input
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Ask a question about your documents..."
              className="flex-1"
              disabled={queryMutation.isPending}
            />
            <Button type="submit" disabled={!question.trim() || queryMutation.isPending}>
              <Send className="h-4 w-4" />
            </Button>
          </form>
        </div>
      </div>
    </div>
  );
}
