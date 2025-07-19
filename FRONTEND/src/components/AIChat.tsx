import { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { Send, Bot, User, Sparkles, FileText, Zap } from 'lucide-react';
import { cn } from '@/lib/utils';
import { startSession, answerQuestion, getSessionStatus, getSuggestionsForSession } from '@/lib/api';

interface Message {
  id: string;
  type: 'user' | 'ai';
  content: string;
  timestamp: Date;
  status?: 'sending' | 'sent' | 'error';
}

interface AIChatProps {
  latexContent: string;
  onApplyChanges: (newContent: string) => void;
  onGetSuggestions?: (sessionId: string) => void;
  onSessionIdChange?: (sessionId: string | null) => void;
  showSuggestions?: boolean; // <-- add this prop
  pushMessage?: string;
  onPushMessageConsumed?: () => void;
}

export function AIChat({ latexContent, onApplyChanges, onGetSuggestions, onSessionIdChange, showSuggestions, pushMessage, onPushMessageConsumed }: AIChatProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'ai',
      content: "👋 Hello! I'm your LaTeX AI assistant. Paste a job description and I'll help you optimize your resume!",
      timestamp: new Date(),
      status: 'sent'
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [questions, setQuestions] = useState<string[]>([]);
  const [answers, setAnswers] = useState<string[]>([]);
  const [currentQuestion, setCurrentQuestion] = useState<string | null>(null);
  const [isQaComplete, setIsQaComplete] = useState(false);
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const [isLLMLoading, setIsLLMLoading] = useState(false);
  const [isOrganizingSuggestions, setIsOrganizingSuggestions] = useState(false);

  // Notify parent when session_id changes
  useEffect(() => {
    if (onSessionIdChange) {
      onSessionIdChange(sessionId);
    }
  }, [sessionId, onSessionIdChange]);

  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [messages]);

  // Handle getting suggestions after Q&A completion
  const handleGetSuggestions = async () => {
    if (!sessionId || !onGetSuggestions) return;
    setIsTyping(true);
    setIsLLMLoading(true);
    setMessages(prev => [
      ...prev,
      {
        id: Date.now().toString(),
        type: 'ai',
        content: `⏳ Loading suggestions... This may take up to a minute.`,
        timestamp: new Date(),
        status: 'sending'
      }
    ]);
    try {
      await getSuggestionsForSession(sessionId);
      onGetSuggestions(sessionId);
      setMessages(prev => [
        ...prev,
        {
          id: Date.now().toString(),
          type: 'ai',
          content: `🎯 AI suggestions generated! Review them in the modal to apply changes to your resume.`,
          timestamp: new Date(),
          status: 'sent'
        }
      ]);
    } catch (e) {
      setMessages(prev => [
        ...prev,
        {
          id: Date.now().toString(),
          type: 'ai',
          content: `❌ Failed to get suggestions: ${(e as Error).message}`,
          timestamp: new Date(),
          status: 'error'
        }
      ]);
    }
    setIsTyping(false);
    setIsLLMLoading(false);
  };

  // Start a session when user submits a job post
  const handleStartSession = async (jobPost: string) => {
    setIsTyping(true);
    try {
      const res = await startSession(latexContent, jobPost);
      setSessionId(res.session_id);
      setQuestions([res.first_question]);
      setCurrentQuestion(res.first_question);
      setAnswers([]);
      setMessages(prev => [
        ...prev,
        {
          id: Date.now().toString(),
          type: 'ai',
          content: `Q1: ${res.first_question}`,
          timestamp: new Date(),
          status: 'sent'
        }
      ]);
    } catch (e) {
      setMessages(prev => [
        ...prev,
        {
          id: Date.now().toString(),
          type: 'ai',
          content: `❌ Failed to start session: ${(e as Error).message}`,
          timestamp: new Date(),
          status: 'error'
        }
      ]);
    }
    setIsTyping(false);
  };

  // Handle answering a question
  const handleAnswerQuestion = async (answer: string) => {
    if (!sessionId) return;
    setIsTyping(true);
    try {
      const res = await answerQuestion(sessionId, answer);
      setAnswers(prev => [...prev, answer]);
      if (res.is_complete) {
        setMessages(prev => [
          ...prev,
          {
            id: Date.now().toString(),
            type: 'ai',
            content: `✅ All questions answered! Click "Get AI Suggestions" to review personalized recommendations for your resume.`,
            timestamp: new Date(),
            status: 'sent'
          }
        ]);
        setCurrentQuestion(null);
        setIsQaComplete(true);
      } else if (res.next_question) {
        setCurrentQuestion(res.next_question);
        setMessages(prev => [
          ...prev,
          {
            id: Date.now().toString(),
            type: 'ai',
            content: `Q: ${res.next_question}`,
            timestamp: new Date(),
            status: 'sent'
          }
        ]);
      }
    } catch (e) {
      setMessages(prev => [
        ...prev,
        {
          id: Date.now().toString(),
          type: 'ai',
          content: `❌ Failed to submit answer: ${(e as Error).message}`,
          timestamp: new Date(),
          status: 'error'
        }
      ]);
    }
    setIsTyping(false);
  };

  // Main send handler
  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;
    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputValue,
      timestamp: new Date(),
      status: 'sent'
    };
    setMessages(prev => [...prev, userMessage]);
    if (!sessionId) {
      // Treat first message as job post
      await handleStartSession(inputValue);
    } else if (currentQuestion) {
      // Treat as answer to current question
      await handleAnswerQuestion(inputValue);
    } else {
      setMessages(prev => [
        ...prev,
        {
      id: Date.now().toString(),
      type: 'ai',
          content: `Session complete. Start a new session by pasting a new job description!`,
      timestamp: new Date(),
      status: 'sent'
        }
      ]);
    }
    setInputValue('');
  };

  // Handler for Apply Changes button in chat
  const handleApplyChangesClick = () => {
    setIsOrganizingSuggestions(true);
    setMessages(prev => [
      ...prev,
      {
        id: Date.now().toString(),
        type: 'ai',
        content: `🗂️ Organizing suggestions... This may take up to a minute.`,
        timestamp: new Date(),
        status: 'sending'
      }
    ]);
    if (onGetSuggestions && sessionId) {
      onGetSuggestions(sessionId);
    }
  };

  // Remove the loading message when the modal opens
  useEffect(() => {
    if (isOrganizingSuggestions && showSuggestions) {
      setIsOrganizingSuggestions(false);
      setMessages(prev => prev.filter(m => !m.content.includes('Organizing suggestions')));
    }
  }, [isOrganizingSuggestions, showSuggestions]);

  useEffect(() => {
    if (pushMessage) {
      setMessages(prev => [
        ...prev,
        {
          id: Date.now().toString(),
          type: 'ai',
          content: pushMessage,
          timestamp: new Date(),
          status: 'sent'
        }
      ]);
      if (onPushMessageConsumed) onPushMessageConsumed();
    }
  }, [pushMessage, onPushMessageConsumed]);

  return (
    <div className="h-full flex flex-col bg-card">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-border">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-full bg-primary/10">
            <Bot className="h-5 w-5 text-primary" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-foreground">AI Assistant</h2>
            <p className="text-sm text-muted-foreground">LaTeX & Career Optimization</p>
          </div>
        </div>
        <Badge variant="outline" className="gap-1">
          <Sparkles className="h-3 w-3" />
          Online
        </Badge>
      </div>

      {/* Messages */}
      <ScrollArea className="flex-1 p-4" ref={scrollAreaRef}>
        <div className="space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={cn(
                "flex gap-3 max-w-[85%]",
                message.type === 'user' ? "ml-auto flex-row-reverse" : ""
              )}
            >
              <div className={cn(
                "p-2 rounded-full flex-shrink-0",
                message.type === 'user' 
                  ? "bg-chat-user/20" 
                  : "bg-chat-ai/20"
              )}>
                {message.type === 'user' ? (
                  <User className="h-4 w-4 text-chat-user" />
                ) : (
                  <Bot className="h-4 w-4 text-chat-ai" />
                )}
              </div>
              
              <div className={cn(
                "rounded-lg p-3 prose prose-sm max-w-none",
                message.type === 'user'
                  ? "bg-chat-bubble-user text-foreground ml-auto"
                  : "bg-chat-bubble-ai text-foreground"
              )}>
                <div className="whitespace-pre-wrap text-sm leading-relaxed">
                  {message.content}
                </div>
                {message.type === 'ai' && message.content.includes('apply') && (
                  <Button 
                    size="sm" 
                    className="mt-3 gap-2" 
                    onClick={handleApplyChangesClick}
                    disabled={isTyping || isOrganizingSuggestions}
                  >
                    <Zap className="h-3 w-3" />
                    Apply Changes
                  </Button>
                )}
                {message.type === 'ai' && message.content.includes('Get AI Suggestions') && (
                  <Button 
                    size="sm" 
                    className="mt-3 gap-2" 
                    onClick={handleGetSuggestions}
                    disabled={isTyping || isLLMLoading}
                  >
                    <Sparkles className="h-3 w-3" />
                    Get AI Suggestions
                  </Button>
                )}
              </div>
            </div>
          ))}
          
          {isTyping && (
            <div className="flex gap-3 max-w-[85%]">
              <div className="p-2 rounded-full bg-chat-ai/20 flex-shrink-0">
                <Bot className="h-4 w-4 text-chat-ai" />
              </div>
              <div className="bg-chat-bubble-ai text-foreground rounded-lg p-3">
                <div className="flex gap-1">
                  <div className="w-2 h-2 bg-current rounded-full animate-pulse"></div>
                  <div className="w-2 h-2 bg-current rounded-full animate-pulse delay-75"></div>
                  <div className="w-2 h-2 bg-current rounded-full animate-pulse delay-150"></div>
                </div>
              </div>
            </div>
          )}
        </div>
      </ScrollArea>

      {/* Input */}
      <div className="p-4 border-t border-border">
        <div className="flex gap-2">
          <Input
            ref={inputRef}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Paste job description or ask about your LaTeX..."
            className="flex-1"
            onKeyPress={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSendMessage();
              }
            }}
          />
          <Button 
            onClick={handleSendMessage} 
            disabled={!inputValue.trim() || isTyping}
            size="icon"
          >
            <Send className="h-4 w-4" />
          </Button>
        </div>
        <p className="text-xs text-muted-foreground mt-2">
          Tip: Paste a job description for personalized optimization suggestions
        </p>
      </div>
    </div>
  );
}