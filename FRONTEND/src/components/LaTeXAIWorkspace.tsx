import { useState } from 'react';
import { ResizablePanels } from './ResizablePanels';
import { LaTeXEditor } from './LaTeXEditor';
import { AIChat } from './AIChat';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { FileText, MessageSquare, Code2, Sparkles } from 'lucide-react';

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

  const handleApplyAIChanges = (newContent: string) => {
    setLatexContent(newContent);
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
          <Button variant="outline" size="sm" className="gap-2">
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