import { useState } from 'react';
import { ResizablePanels } from './ResizablePanels';
import { LaTeXEditor } from './LaTeXEditor';
import { AIChat } from './AIChat';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { FileText, MessageSquare, Code2, Sparkles, Lightbulb, X } from 'lucide-react';
import { exportPdf } from '@/lib/api';
import { useRef } from 'react';
import { getSuggestions, applySuggestion, Suggestion, getSuggestionsForSession } from '@/lib/api';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog';
import { Card } from '@/components/ui/card';

const defaultLaTeXContent = `\\documentclass{article}
\\usepackage[utf8]{inputenc}
\\usepackage{amsmath}
\\usepackage{amsfonts}
\\usepackage{amssymb}

\\title{Your Document Title}
\\author{Your Name}
\\date{\\today}

\\begin{document}

\\maketitle

\\section{Introduction}
Welcome to your LaTeX document. Start writing your content here.

\\subsection{Mathematics}
Here's an example of inline math: $E = mc^2$ and display math:
\\begin{equation}
    \\int_{-\\infty}^{\\infty} e^{-x^2} dx = \\sqrt{\\pi}
\\end{equation}

\\section{Lists}
\\begin{itemize}
    \\item First item
    \\item Second item
    \\item Third item
\\end{itemize}

\\end{document}`;

export function LaTeXAIWorkspace() {
  const [latexContent, setLatexContent] = useState(defaultLaTeXContent);
  const [wordCount, setWordCount] = useState(0);
  const editorRef = useRef<any>(null);
  const [decorations, setDecorations] = useState<string[]>([]);
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isLoadingSuggestions, setIsLoadingSuggestions] = useState(false);

  const handleLatexChange = (newContent: string) => {
    setLatexContent(newContent);
    // Simple word count (excluding LaTeX commands)
    const words = newContent
      .replace(/\\[a-zA-Z]+(\[[^\]]*\])?(\{[^}]*\})?/g, '')
      .replace(/[{}\\]/g, ' ')
      .split(/\s+/)
      .filter(word => word.length > 0);
    setWordCount(words.length);
  };

  const highlightSuggestions = (content: string) => {
    if (!editorRef.current) return;
    const lines = content.split('\n');
    let inSuggestion = false;
    let startLine = 0;
    const ranges = [];
    for (let i = 0; i < lines.length; i++) {
      if (lines[i].includes('% === AI SUGGESTION START ===')) {
        inSuggestion = true;
        startLine = i + 1;
      } else if (lines[i].includes('% === AI SUGGESTION END ===') && inSuggestion) {
        inSuggestion = false;
        ranges.push({ startLineNumber: startLine, endLineNumber: i + 1 });
      }
    }
    const newDecorations = ranges.map(range => ({
      range,
      options: {
        isWholeLine: true,
        className: 'ai-suggestion-highlight',
        inlineClassName: 'ai-suggestion-inline',
      },
    }));
    setDecorations(
      editorRef.current.deltaDecorations(
        decorations,
        newDecorations.map(d => ({
          range: window['monaco'] ? new window['monaco'].Range(d.range.startLineNumber, 1, d.range.endLineNumber, 1) : undefined,
          options: d.options,
        }))
      )
    );
  };

  const handleApplyAIChanges = (snippet: string) => {
    setLatexContent((prev) => {
      const updated = prev + '\n\n' + snippet;
      setTimeout(() => highlightSuggestions(updated), 100); // highlight after update
      return updated;
    });
  };

  const handleExportPdf = async () => {
    try {
      const response = await exportPdf(latexContent);
      if (!response.ok) throw new Error('Failed to export PDF');
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'resume.pdf';
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (e) {
      alert('Failed to export PDF: ' + (e as Error).message);
    }
  };

  // --- SUGGESTION LOGIC ---
  const fetchSuggestions = async () => {
    if (!sessionId) {
      alert('Please complete the Q&A session first to get AI suggestions.');
      return;
    }
    
    setIsLoadingSuggestions(true);
    try {
      const res = await getSuggestionsForSession(sessionId);
      setSuggestions(res.suggestions);
      setShowSuggestions(true);
    } catch (e) {
      alert('Failed to fetch suggestions: ' + (e as Error).message);
    }
    setIsLoadingSuggestions(false);
  };

  const handleGetSuggestionsFromSession = async (sessionId: string) => {
    setIsLoadingSuggestions(true);
    try {
      const res = await getSuggestionsForSession(sessionId);
      setSuggestions(res.suggestions);
      setSessionId(res.session_id);
      setShowSuggestions(true);
    } catch (e) {
      alert('Failed to fetch suggestions: ' + (e as Error).message);
    }
    setIsLoadingSuggestions(false);
  };

  const handleAcceptSuggestion = async (suggestion: Suggestion) => {
    if (!sessionId) return;
    try {
      const res = await applySuggestion(sessionId, {
        suggestion_id: suggestion.id,
        resume_latex: latexContent,
      });
      setLatexContent(res.updated_resume_latex);
      setSuggestions(res.suggestions);
      setTimeout(() => highlightSuggestions(res.updated_resume_latex), 100);
      if (res.suggestions.length === 0) setShowSuggestions(false);
    } catch (e) {
      alert('Failed to apply suggestion: ' + (e as Error).message);
    }
  };

  const handleRejectSuggestion = (suggestion: Suggestion) => {
    setSuggestions((prev) => prev.filter((s) => s.id !== suggestion.id));
    if (suggestions.length === 1) setShowSuggestions(false);
  };

  return (
    <div className="h-screen bg-background flex flex-col">
      {/* Top Header */}
      <header className="h-14 border-b border-border bg-card/50 backdrop-blur-sm flex items-center justify-between px-6">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <div className="p-2 rounded-lg bg-primary/10">
              <Code2 className="h-5 w-5 text-primary" />
            </div>
            <div>
              <h1 className="text-lg font-semibold text-foreground">LaTeX AI Studio</h1>
              <p className="text-xs text-muted-foreground">Advanced LaTeX editing with AI assistance</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant="outline" className="gap-1">
              <FileText className="h-3 w-3" />
              {wordCount} words
            </Badge>
            <Badge variant="outline" className="gap-1">
              <Sparkles className="h-3 w-3" />
              AI Ready
            </Badge>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" className="gap-2" onClick={handleExportPdf}>
            <FileText className="h-4 w-4" />
            Export PDF
          </Button>
          <Button size="sm" className="gap-2" onClick={fetchSuggestions} disabled={isLoadingSuggestions || !sessionId}>
            <Lightbulb className="h-4 w-4" />
            {isLoadingSuggestions ? 'Loading...' : 'AI Suggestions'}
          </Button>
          <Button size="sm" className="gap-2">
            <MessageSquare className="h-4 w-4" />
            Share
          </Button>
        </div>
      </header>
      {/* Main Content */}
      <div className="flex-1 relative">
        <ResizablePanels 
          defaultSize={60}
          minSize={30}
          maxSize={70}
        >
          {/* LaTeX Editor Pane */}
          <LaTeXEditor 
            content={latexContent} 
            onChange={handleLatexChange}
            editorRef={editorRef}
          />
          {/* AI Chat Pane */}
          <AIChat 
            latexContent={latexContent}
            onApplyChanges={handleApplyAIChanges}
            onGetSuggestions={handleGetSuggestionsFromSession}
            onSessionIdChange={setSessionId}
          />
        </ResizablePanels>
        {/* Suggestion Review Modal */}
        <Dialog open={showSuggestions} onOpenChange={setShowSuggestions}>
          <DialogContent className="max-w-2xl w-[90vw] max-h-[80vh] flex flex-col suggestion-modal-content">
            <DialogHeader className="flex justify-between items-center">
              <div>
                <DialogTitle className="text-lg font-semibold">
                  AI Suggestions {suggestions.length > 0 && `(${suggestions.length})`}
                </DialogTitle>
                <DialogDescription>
                  Review and apply AI-generated suggestions to improve your resume
                </DialogDescription>
              </div>
              <Button variant="ghost" size="icon" onClick={() => setShowSuggestions(false)}>
                <X className="h-4 w-4" />
              </Button>
            </DialogHeader>
            
            <div className="flex-1 overflow-y-auto min-h-0 suggestion-modal-scroll">
              {isLoadingSuggestions ? (
                <div className="flex items-center justify-center py-8">
                  <div className="flex items-center gap-2 text-muted-foreground">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary"></div>
                    <span>Loading suggestions...</span>
                  </div>
                </div>
              ) : suggestions.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  No suggestions available.
                </div>
              ) : (
                <div className="space-y-4">
                  {suggestions.map((s) => (
                    <Card key={s.id} className="p-4 flex flex-col gap-3">
                      <div className="font-medium text-sm leading-relaxed">
                        {s.description}
                      </div>
                      <div className="bg-muted/50 rounded-md p-3">
                        <pre className="text-xs overflow-x-auto whitespace-pre-wrap break-words">
                          {s.suggested_latex_snippet}
                        </pre>
                      </div>
                      <div className="flex gap-2 mt-2">
                        <Button size="sm" onClick={() => handleAcceptSuggestion(s)} className="flex-1">
                          Accept
                        </Button>
                        <Button size="sm" variant="outline" onClick={() => handleRejectSuggestion(s)} className="flex-1">
                          Reject
                        </Button>
                      </div>
                    </Card>
                  ))}
                </div>
              )}
            </div>
            
            <DialogFooter className="pt-4 border-t">
              <Button variant="outline" onClick={() => setShowSuggestions(false)}>
                Close
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
      {/* Bottom Status Bar */}
      <footer className="h-8 border-t border-border bg-muted/30 flex items-center justify-between px-4 text-xs text-muted-foreground">
        <div className="flex items-center gap-4">
          <span>LaTeX AI Studio v1.0</span>
          <span>•</span>
          <span>Ready</span>
        </div>
        <div className="flex items-center gap-4">
          <span>Ln 1, Col 1</span>
          <span>•</span>
          <span>UTF-8</span>
          <span>•</span>
          <span>LaTeX</span>
        </div>
      </footer>
    </div>
  );
}