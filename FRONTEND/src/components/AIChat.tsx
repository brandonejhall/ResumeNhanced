import { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { Send, Bot, User, Sparkles, FileText, Zap } from 'lucide-react';
import { cn } from '@/lib/utils';

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
}

export function AIChat({ latexContent, onApplyChanges }: AIChatProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'ai',
      content: "👋 Hello! I'm your LaTeX AI assistant. I can help you:\n\n• Analyze and improve your LaTeX code\n• Compare your document against job descriptions\n• Suggest formatting improvements\n• Fix common LaTeX errors\n• Optimize document structure\n\nJust paste a job description or ask me anything about your LaTeX document!",
      timestamp: new Date(),
      status: 'sent'
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    // Auto-scroll to bottom when new messages arrive
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [messages]);

  const simulateAIResponse = (userMessage: string): string => {
    const message = userMessage.toLowerCase();
    
    // Job description analysis
    if (message.includes('job') || message.includes('position') || message.includes('requirements')) {
      return `🔍 **Job Description Analysis**

I've analyzed the job posting against your LaTeX document. Here are my suggestions:

**Key Improvements Needed:**
• Add a Skills section highlighting technical competencies
• Include more quantifiable achievements
• Optimize for ATS systems with better keyword usage
• Consider adding a Professional Summary

**LaTeX Optimizations:**
• Use \\usepackage{enumitem} for better list formatting
• Add \\usepackage{hyperref} for clickable links
• Consider \\usepackage{fontawesome5} for modern icons

Would you like me to apply these changes to your document?`;
    }

    // LaTeX-specific help
    if (message.includes('latex') || message.includes('error') || message.includes('fix')) {
      return `🔧 **LaTeX Analysis**

I've reviewed your document and found:

**✅ Good practices:**
• Proper document structure with sections
• Correct math environment usage
• Clean package imports

**⚠️ Suggestions:**
• Add \\usepackage{geometry} for better margins
• Consider using \\usepackage{booktabs} for professional tables
• Add \\usepackage{graphicx} if you plan to include images

**🚀 Enhancements:**
• Use \\usepackage{xcolor} for colored text
• Add \\usepackage{fancyhdr} for custom headers

Would you like me to implement any of these improvements?`;
    }

    // General responses
    const responses = [
      `💡 **Analysis Complete**

I've processed your request. Based on your LaTeX document, I recommend focusing on:

• Document structure optimization
• Content enhancement for target audience
• Technical formatting improvements
• ATS-friendly formatting

What specific aspect would you like me to help with?`,
      
      `🎯 **Smart Suggestions**

Your document shows good potential! Here's what I can help improve:

• **Content**: More impactful language and quantified results
• **Format**: Better visual hierarchy and spacing
• **Technical**: Modern LaTeX packages and best practices

Ready to enhance your document?`,
      
      `🚀 **AI Analysis**

I see opportunities to make your document stand out:

• Tailored content for specific job requirements
• Enhanced formatting for better readability
• Strategic keyword optimization
• Professional styling improvements

Which area interests you most?`
    ];
    
    return responses[Math.floor(Math.random() * responses.length)];
  };

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
    setInputValue('');
    setIsTyping(true);

    // Simulate AI processing time
    setTimeout(() => {
      const aiResponse: Message = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: simulateAIResponse(inputValue),
        timestamp: new Date(),
        status: 'sent'
      };

      setMessages(prev => [...prev, aiResponse]);
      setIsTyping(false);
    }, 1500 + Math.random() * 1000);
  };

  const handleApplyChanges = () => {
    // Example of applying AI-suggested changes
    const improvedLatex = `\\documentclass{article}
\\usepackage[utf8]{inputenc}
\\usepackage{amsmath}
\\usepackage{amsfonts}
\\usepackage{amssymb}
\\usepackage{geometry}
\\usepackage{hyperref}
\\usepackage{enumitem}
\\usepackage{xcolor}

\\geometry{margin=1in}
\\hypersetup{colorlinks=true, linkcolor=blue, urlcolor=blue}

\\title{Enhanced Document with AI Suggestions}
\\author{Your Name}
\\date{\\today}

\\begin{document}

\\maketitle

\\section{Professional Summary}
\\textcolor{blue}{AI-Enhanced Summary:} Experienced professional with proven track record in technical excellence and innovation.

\\section{Core Competencies}
\\begin{itemize}[noitemsep]
    \\item Technical Leadership \\& Project Management
    \\item Advanced Problem Solving \\& Analytics
    \\item Cross-functional Team Collaboration
    \\item Continuous Learning \\& Adaptation
\\end{itemize}

\\section{Professional Experience}
\\subsection{Key Achievements}
\\begin{itemize}[noitemsep]
    \\item Increased efficiency by 40\\% through process optimization
    \\item Led cross-functional team of 15+ members
    \\item Delivered projects 25\\% ahead of schedule
    \\item Reduced costs by \\$50K annually through strategic improvements
\\end{itemize}

\\section{Technical Skills}
\\begin{itemize}[noitemsep]
    \\item Programming: Python, JavaScript, Java
    \\item Frameworks: React, Node.js, Spring Boot
    \\item Tools: Git, Docker, AWS, Azure
    \\item Methodologies: Agile, Scrum, DevOps
\\end{itemize}

\\end{document}`;

    onApplyChanges(improvedLatex);

    // Add confirmation message
    const confirmMessage: Message = {
      id: Date.now().toString(),
      type: 'ai',
      content: "✅ **Changes Applied Successfully!**\n\nI've updated your LaTeX document with:\n• Modern package imports\n• Professional formatting\n• Enhanced structure\n• ATS-optimized content\n\nYour document is now more competitive and visually appealing!",
      timestamp: new Date(),
      status: 'sent'
    };

    setMessages(prev => [...prev, confirmMessage]);
  };

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
                    onClick={handleApplyChanges}
                  >
                    <Zap className="h-3 w-3" />
                    Apply Changes
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