import { useState, useRef, useEffect } from 'react';
import { Editor } from '@monaco-editor/react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { AlertCircle, CheckCircle, FileText, Save } from 'lucide-react';
import { cn } from '@/lib/utils';

interface LaTeXError {
  line: number;
  column: number;
  message: string;
  severity: 'error' | 'warning' | 'info';
}

interface LaTeXEditorProps {
  content: string;
  onChange: (content: string) => void;
}

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

export function LaTeXEditor({ content, onChange }: LaTeXEditorProps) {
  const [errors, setErrors] = useState<LaTeXError[]>([]);
  const [isCompiling, setIsCompiling] = useState(false);
  const editorRef = useRef(null);

  // Simple LaTeX validation function
  const validateLaTeX = (code: string): LaTeXError[] => {
    const errors: LaTeXError[] = [];
    const lines = code.split('\n');

    lines.forEach((line, index) => {
      // Check for unmatched braces
      const openBraces = (line.match(/\{/g) || []).length;
      const closeBraces = (line.match(/\}/g) || []).length;
      
      if (openBraces !== closeBraces) {
        errors.push({
          line: index + 1,
          column: 1,
          message: 'Unmatched braces detected',
          severity: 'warning'
        });
      }

      // Check for common LaTeX errors
      if (line.includes('\\begin{') && !lines.slice(index + 1).some(l => l.includes('\\end{'))) {
        const envMatch = line.match(/\\begin\{([^}]+)\}/);
        if (envMatch) {
          errors.push({
            line: index + 1,
            column: 1,
            message: `Missing \\end{${envMatch[1]}}`,
            severity: 'error'
          });
        }
      }

      // Check for undefined commands (basic check)
      const commandMatches = line.match(/\\[a-zA-Z]+/g);
      if (commandMatches) {
        const knownCommands = [
          '\\documentclass', '\\usepackage', '\\begin', '\\end', '\\title', '\\author', 
          '\\date', '\\maketitle', '\\section', '\\subsection', '\\item', '\\textbf', 
          '\\textit', '\\emph', '\\cite', '\\ref', '\\label', '\\today', '\\newline',
          '\\int', '\\sum', '\\frac', '\\sqrt', '\\alpha', '\\beta', '\\gamma', '\\delta'
        ];
        
        commandMatches.forEach(cmd => {
          if (!knownCommands.includes(cmd) && !cmd.match(/^\\[a-z]$/)) {
            errors.push({
              line: index + 1,
              column: line.indexOf(cmd) + 1,
              message: `Possibly undefined command: ${cmd}`,
              severity: 'info'
            });
          }
        });
      }
    });

    return errors;
  };

  useEffect(() => {
    const timeoutId = setTimeout(() => {
      setIsCompiling(true);
      const newErrors = validateLaTeX(content);
      setErrors(newErrors);
      setIsCompiling(false);
    }, 500);

    return () => clearTimeout(timeoutId);
  }, [content]);

  const getStatusBadge = () => {
    const errorCount = errors.filter(e => e.severity === 'error').length;
    const warningCount = errors.filter(e => e.severity === 'warning').length;

    if (isCompiling) {
      return <Badge variant="secondary" className="gap-1"><FileText className="h-3 w-3" />Compiling...</Badge>;
    }

    if (errorCount > 0) {
      return <Badge variant="destructive" className="gap-1"><AlertCircle className="h-3 w-3" />{errorCount} Error{errorCount > 1 ? 's' : ''}</Badge>;
    }

    if (warningCount > 0) {
      return <Badge className="gap-1 bg-warning text-warning-foreground"><AlertCircle className="h-3 w-3" />{warningCount} Warning{warningCount > 1 ? 's' : ''}</Badge>;
    }

    return <Badge className="gap-1 bg-success text-success-foreground"><CheckCircle className="h-3 w-3" />No Issues</Badge>;
  };

  return (
    <div className="h-full flex flex-col bg-card border-r border-border">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-border">
        <div className="flex items-center gap-3">
          <h2 className="text-lg font-semibold text-foreground">LaTeX Editor</h2>
          {getStatusBadge()}
        </div>
        <Button variant="outline" size="sm" className="gap-2">
          <Save className="h-4 w-4" />
          Save
        </Button>
      </div>

      {/* Editor */}
      <div className="flex-1 relative">
        <Editor
          height="100%"
          defaultLanguage="latex"
          value={content}
          onChange={(value) => onChange(value || '')}
          theme="vs-dark"
          options={{
            minimap: { enabled: false },
            fontSize: 14,
            fontFamily: 'JetBrains Mono, Consolas, Monaco, monospace',
            lineNumbers: 'on',
            wordWrap: 'on',
            automaticLayout: true,
            scrollBeyondLastLine: false,
            renderWhitespace: 'boundary',
            cursorBlinking: 'smooth',
            cursorSmoothCaretAnimation: 'on',
            smoothScrolling: true,
            padding: { top: 16, bottom: 16 }
          }}
          onMount={(editor) => {
            editorRef.current = editor;
          }}
        />
      </div>

      {/* Error Panel */}
      {errors.length > 0 && (
        <div className="border-t border-border bg-muted/30 max-h-40 overflow-y-auto">
          <div className="p-3">
            <h3 className="text-sm font-medium text-foreground mb-2">Issues</h3>
            <div className="space-y-1">
              {errors.map((error, index) => (
                <div
                  key={index}
                  className={cn(
                    "text-xs p-2 rounded flex items-start gap-2 cursor-pointer hover:bg-muted/50",
                    error.severity === 'error' && "text-destructive",
                    error.severity === 'warning' && "text-warning",
                    error.severity === 'info' && "text-muted-foreground"
                  )}
                  onClick={() => {
                    // Focus editor and go to line
                    if (editorRef.current) {
                      (editorRef.current as any).focus();
                      (editorRef.current as any).setPosition({ lineNumber: error.line, column: error.column });
                    }
                  }}
                >
                  <AlertCircle className="h-3 w-3 mt-0.5 flex-shrink-0" />
                  <div>
                    <div className="font-medium">Line {error.line}:{error.column}</div>
                    <div>{error.message}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}