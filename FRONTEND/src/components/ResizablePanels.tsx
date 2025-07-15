import { useState, useRef, useCallback, useEffect } from 'react';
import { cn } from '@/lib/utils';

interface ResizablePanelsProps {
  children: [React.ReactNode, React.ReactNode];
  defaultSize?: number; // percentage (0-100)
  minSize?: number; // percentage
  maxSize?: number; // percentage
  className?: string;
}

export function ResizablePanels({
  children,
  defaultSize = 50,
  minSize = 20,
  maxSize = 80,
  className
}: ResizablePanelsProps) {
  const [leftWidth, setLeftWidth] = useState(defaultSize);
  const [isDragging, setIsDragging] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleMouseMove = useCallback((e: MouseEvent) => {
    if (!isDragging || !containerRef.current) return;

    const containerRect = containerRef.current.getBoundingClientRect();
    const newLeftWidth = ((e.clientX - containerRect.left) / containerRect.width) * 100;
    
    // Apply constraints
    const constrainedWidth = Math.max(minSize, Math.min(maxSize, newLeftWidth));
    setLeftWidth(constrainedWidth);
  }, [isDragging, minSize, maxSize]);

  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
  }, []);

  useEffect(() => {
    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = 'col-resize';
      document.body.style.userSelect = 'none';

      return () => {
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
        document.body.style.cursor = '';
        document.body.style.userSelect = '';
      };
    }
  }, [isDragging, handleMouseMove, handleMouseUp]);

  return (
    <div 
      ref={containerRef}
      className={cn("flex h-full w-full", className)}
    >
      {/* Left Panel */}
      <div 
        style={{ width: `${leftWidth}%` }}
        className="flex-shrink-0 overflow-hidden"
      >
        {children[0]}
      </div>

      {/* Resizer */}
      <div
        className={cn(
          "w-2 bg-border hover:bg-primary/50 cursor-col-resize flex-shrink-0 transition-colors duration-200 relative group",
          isDragging && "bg-primary"
        )}
        onMouseDown={handleMouseDown}
      >
        {/* Visual indicator */}
        <div className="absolute inset-y-0 left-1/2 transform -translate-x-1/2 w-0.5 bg-muted-foreground/20 group-hover:bg-primary/70 transition-colors duration-200" />
      </div>

      {/* Right Panel */}
      <div 
        style={{ width: `${100 - leftWidth}%` }}
        className="flex-1 overflow-hidden"
      >
        {children[1]}
      </div>
    </div>
  );
}