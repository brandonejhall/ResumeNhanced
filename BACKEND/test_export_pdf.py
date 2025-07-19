import subprocess
import tempfile
import os
import shutil

# Your original LaTeX code
latex_resume = r"""
\documentclass[letterpaper,11pt]{article}

\usepackage{latexsym}
\usepackage[empty]{fullpage}
\usepackage{titlesec}
\usepackage{marvosym}
\usepackage[usenames,dvipsnames]{color}
\usepackage{verbatim}
\usepackage{enumitem}
\usepackage[hidelinks]{hyperref}
\usepackage{fancyhdr}
\usepackage[english]{babel}
\usepackage{tabularx}

\pagestyle{fancy}
\fancyhf{}
\fancyfoot{}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}

\addtolength{\oddsidemargin}{-0.5in}
\addtolength{\evensidemargin}{-0.5in}
\addtolength{\textwidth}{1in}
\addtolength{\topmargin}{-.5in}
\addtolength{\textheight}{1.0in}

\urlstyle{same}

\raggedbottom
\raggedright
\setlength{\tabcolsep}{0in}

\titleformat{\section}{
  \vspace{-4pt}\scshape\raggedright\large
}{}{0em}{}[\color{black}\titlerule \vspace{-5pt}]

\newcommand{\resumeItem}[1]{
  \item\small{
    {#1 \vspace{-2pt}}
  }
}

\newcommand{\resumeSubheading}[4]{
  \vspace{-2pt}\item
    \begin{tabular*}{0.97\textwidth}[t]{l@{\extracolsep{\fill}}r}
      \textbf{#1} & #2 \\
      \textit{\small#3} & \textit{\small #4} \\
    \end{tabular*}\vspace{-7pt}
}

\newcommand{\resumeSubItem}[1]{\resumeItem{#1}\vspace{-4pt}}

\renewcommand\labelitemii{$\vcenter{\hbox{\tiny$\bullet$}}$}

\newcommand{\resumeSubHeadingListStart}{\begin{itemize}[leftmargin=0.15in, label={}]}
\newcommand{\resumeSubHeadingListEnd}{\end{itemize}}
\newcommand{\resumeItemListStart}{\begin{itemize}}
\newcommand{\resumeItemListEnd}{\end{itemize}\vspace{-5pt}}

\begin{document}

\begin{center}
    \textbf{\Huge \scshape John Doe} \\ \vspace{1pt}
    \small 555-123-4567 $|$ \href{mailto:john.doe@email.com}{\underline{john.doe@email.com}} $|$ 
    \href{https://linkedin.com/in/johndoe}{\underline{linkedin.com/in/johndoe}} $|$
    \href{https://github.com/johndoe}{\underline{github.com/johndoe}}
\end{center}

\section{Experience}
  \resumeSubHeadingListStart

    \resumeSubheading
      {Software Developer}{Jan 2022 -- Present}
      {TechCorp Solutions}{San Francisco, CA}
      \resumeItemListStart
        \resumeItem{Developed and maintained web applications using React and Node.js}
        \resumeItem{Collaborated with design team to implement responsive user interfaces}
        \resumeItem{Participated in code reviews and maintained code quality standards}
        \resumeItem{Fixed bugs and implemented feature requests from product management}
      \resumeItemListEnd

    \resumeSubheading
      {Junior Developer}{Jun 2020 -- Dec 2021}
      {StartupXYZ}{Remote}
      \resumeItemListStart
        \resumeItem{Built REST APIs using Express.js and MongoDB}
        \resumeItem{Implemented user authentication and session management}
        \resumeItem{Worked on small team to deliver MVP features quickly}
        \resumeItem{Wrote unit tests using Jest framework}
      \resumeItemListEnd

    \resumeSubheading
      {Programming Intern}{May 2019 -- Aug 2019}
      {Local Software Company}{Austin, TX}
      \resumeItemListStart
        \resumeItem{Assisted senior developers with debugging and testing}
        \resumeItem{Created simple scripts for data processing tasks}
        \resumeItem{Learned version control with Git and team collaboration}
      \resumeItemListEnd

  \resumeSubHeadingListEnd

\section{Education}
  \resumeSubHeadingListStart
    \resumeSubheading
      {Bachelor of Science in Computer Science}{Sep 2016 -- May 2020}
      {University of Texas at Austin}{Austin, TX}
      \resumeItemListStart
        \resumeItem{Relevant Coursework: Data Structures, Algorithms, Database Systems, Software Engineering}
        \resumeItem{GPA: 3.4/4.0}
      \resumeItemListEnd
  \resumeSubHeadingListEnd

\section{Technical Skills}
 \begin{itemize}[leftmargin=0.15in, label={}]
    \small{\item{
     \textbf{Languages}{: JavaScript, Python, Java, HTML/CSS, SQL} \\
     \textbf{Frameworks}{: React, Node.js, Express.js, Bootstrap} \\
     \textbf{Tools}{: Git, MongoDB, MySQL, VS Code, Postman} \\
     \textbf{Other}{: REST APIs, Agile development, Unit testing}
    }}
 \end{itemize}

\section{Projects}
    \resumeSubHeadingListStart
      \resumeSubheading
        {Personal Portfolio Website}{2021}
        {\href{https://johndoe.dev}{\underline{johndoe.dev}}}{}
        \resumeItemListStart
          \resumeItem{Built responsive portfolio site using React and deployed on Netlify}
          \resumeItem{Implemented contact form with email integration}
        \resumeItemListEnd
        
      \resumeSubheading
        {Task Management App}{2020}
        {\href{https://github.com/johndoe/taskapp}{\underline{github.com/johndoe/taskapp}}}{}
        \resumeItemListStart
          \resumeItem{Created full-stack web application for personal task management}
          \resumeItem{Used React frontend with Node.js backend and MongoDB database}
        \resumeItemListEnd
    \resumeSubHeadingListEnd

\end{document}
"""

def test_latex_compilation_locally():
    """Test LaTeX compilation locally with detailed error output"""
    print("🔍 Testing LaTeX compilation locally...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        tex_file = os.path.join(temp_dir, "resume.tex")
        
        # Write LaTeX code to file
        with open(tex_file, 'w', encoding='utf-8') as f:
            f.write(latex_resume)
        print(f"✅ LaTeX file written to: {tex_file}")
        
        # Try compiling with pdflatex
        try:
            print("🚀 Running pdflatex compilation...")
            result = subprocess.run(
                ['pdflatex', '-interaction=nonstopmode', '-output-directory', temp_dir, tex_file],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=temp_dir
            )
            
            print(f"📊 Exit code: {result.returncode}")
            
            if result.returncode == 0:
                print("✅ LaTeX compilation successful!")
                pdf_path = os.path.join(temp_dir, "resume.pdf")
                if os.path.exists(pdf_path):
                    # Copy PDF to current directory
                    shutil.copy2(pdf_path, "debug_resume.pdf")
                    print("💾 PDF copied to debug_resume.pdf")
                    print(f"📦 PDF size: {os.path.getsize('debug_resume.pdf')} bytes")
                else:
                    print("⚠️ PDF not found despite successful compilation")
            else:
                print("❌ LaTeX compilation failed!")
                print("\n--- STDOUT ---")
                print(result.stdout)
                print("\n--- STDERR ---") 
                print(result.stderr)
                
                # Check for .log file with more details
                log_file = os.path.join(temp_dir, "resume.log")
                if os.path.exists(log_file):
                    print("\n--- LOG FILE CONTENT (last 50 lines) ---")
                    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        for line in lines[-50:]:
                            print(line.rstrip())
                
        except subprocess.TimeoutExpired:
            print("❌ LaTeX compilation timed out (>60s)")
        except Exception as e:
            print(f"❌ Error running pdflatex: {e}")

def check_latex_packages():
    """Check if required LaTeX packages are installed"""
    print("\n🔍 Checking LaTeX package availability...")
    
    packages = [
        'latexsym', 'fullpage', 'titlesec', 'marvosym', 'color',
        'verbatim', 'enumitem', 'hyperref', 'fancyhdr', 'babel', 'tabularx'
    ]
    
    for package in packages:
        try:
            result = subprocess.run(
                ['kpsewhich', f'{package}.sty'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0 and result.stdout.strip():
                print(f"✅ {package}: {result.stdout.strip()}")
            else:
                print(f"❌ {package}: NOT FOUND")
        except Exception as e:
            print(f"⚠️ {package}: Error checking - {e}")

if __name__ == "__main__":
    check_latex_packages()
    test_latex_compilation_locally()