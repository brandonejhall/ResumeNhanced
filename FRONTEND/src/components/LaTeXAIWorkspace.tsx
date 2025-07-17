import { useState } from 'react';
import { ResizablePanels } from './ResizablePanels';
import { LaTeXEditor } from './LaTeXEditor';
import { AIChat } from './AIChat';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { FileText, MessageSquare, Code2, Sparkles } from 'lucide-react';
import { exportPdf } from '@/lib/api';
import { useRef } from 'react';

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
          />
        </ResizablePanels>
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