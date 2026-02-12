# NASA Technical Memorandum Starter Package

This package provides everything needed to create a NASA Technical Memorandum (TM) style LaTeX document from markdown source files.

## Package Contents

```
nasa-tm-starter/
├── README.md              # This file (instructions for Claude)
├── main-template.tex      # LaTeX template with NASA TM formatting
├── references.bib         # Bibliography template
├── NASA_logo.svg.png      # NASA grayscale logo
└── figures/               # Create this for your figures
```

## Quick Start for Claude

When asked to convert markdown files to a NASA TM format:

1. **Copy this package** to your project's `paper/latex/` directory
2. **Rename** `main-template.tex` to `main.tex`
3. **Update metadata** in the `DOCUMENT METADATA` section
4. **Create sections/** directory and convert each markdown file to a `.tex` file
5. **Update `main.tex`** to `\input{sections/filename}` for each section
6. **Compile** with `pdflatex` + `biber` + `pdflatex` (×2)

## Converting Markdown to LaTeX

### Section Files

For each markdown file, create a corresponding `.tex` file in `sections/`:

| Markdown | LaTeX |
|----------|-------|
| `01-introduction.md` | `sections/introduction.tex` |
| `02-method.md` | `sections/method.tex` |
| `03-results.md` | `sections/results.tex` |
| `04-discussion.md` | `sections/discussion.tex` |

### Conversion Rules

**Headers:**
```markdown
## Section Title        →  Already handled by main.tex \section{}
### Subsection          →  \subsection{Subsection}
#### Subsubsection      →  \subsubsection{Subsubsection}
```

**Text formatting:**
```markdown
**bold**                →  \textbf{bold}
*italic*                →  \textit{italic}
`code`                  →  \texttt{code}
```

**Lists:**
```markdown
- Item 1                →  \begin{itemize}
- Item 2                       \item Item 1
                               \item Item 2
                           \end{itemize}

1. First                →  \begin{enumerate}
2. Second                      \item First
                               \item Second
                           \end{enumerate}
```

**Figures:**
```markdown
![Caption](figures/fig.png)

→

\begin{figure}[htbp]
    \centering
    \includegraphics[width=0.8\textwidth]{figures/fig.png}
    \caption[Short caption]{Full caption text.}
    \label{fig:descriptive-label}
\end{figure}
```

**Tables:**
```markdown
| Col1 | Col2 |
|------|------|
| A    | B    |

→

\begin{table}[htbp]
    \centering
    \caption[Short caption]{Full caption text.}
    \label{tab:descriptive-label}
    \begin{tabular}{ll}
        \toprule
        \textbf{Col1} & \textbf{Col2} \\
        \midrule
        A & B \\
        \bottomrule
    \end{tabular}
\end{table}
```

**Equations:**
```markdown
Inline: $E = mc^2$      →  $E = mc^2$

Display:
$$
F = ma
$$
→
\begin{equation}
    F = ma
    \label{eq:newton}
\end{equation}
```

**Cross-references:**
```markdown
See Figure 1            →  See \cref{fig:label}
As shown in Table 2     →  As shown in \cref{tab:label}
From Equation 3         →  From \cref{eq:label}
```

**Citations:**
```markdown
[1]                     →  \cite{bibtex_key}
(Smith et al., 2024)    →  \cite{smith2024}
```

### Short Captions

**Important:** Always use short captions for List of Figures/Tables:

```latex
\caption[Short version]{Long detailed caption that appears under the figure.}
```

The short version appears in the LoF/LoT as "Figure X: Short version"

## Custom Commands

Define frequently-used terms as commands in the preamble:

```latex
% Acronyms (use \newcommand for text that should appear exactly)
\newcommand{\isru}{ISRU}
\newcommand{\nasa}{NASA}

% Units
\newcommand{\tyr}{t/yr}
\newcommand{\kgperkgh}{kg/(kg$_{\text{H}_2}$/month)}

% Chemical formulas
\newcommand{\lox}{LO\textsubscript{2}}
\newcommand{\lh}{LH\textsubscript{2}}
\newcommand{\htwo}{H\textsubscript{2}}
\newcommand{\htwoo}{H\textsubscript{2}O}
\newcommand{\otwo}{O\textsubscript{2}}

% Commonly formatted terms
\newcommand{\ddte}{DDT\&E}
\newcommand{\dv}{$\Delta V$}
```

## Metadata to Update

In `main.tex`, customize these fields:

```latex
\newcommand{\doctitle}{Your Document Title Here}
\newcommand{\docsubtitle}{Optional Subtitle}
\newcommand{\docmonth}{February}
\newcommand{\docyear}{2026}
\newcommand{\docnumber}{NASA/TM---2026-XXXXXX}
\newcommand{\doccenter}{Langley Research Center}
\newcommand{\doclocation}{Hampton, Virginia}
\newcommand{\docauthorA}{Author Name}
\newcommand{\docaffiliationA}{Affiliation, Location}
```

For multiple authors, add more:
```latex
\newcommand{\docauthorB}{Second Author}
\newcommand{\docaffiliationB}{Their Affiliation}
```

And in the title page section, add:
```latex
\noindent
{\large \docauthorA}\\[3pt]
{\itshape \docaffiliationA}

\vspace{0.25in}

\noindent
{\large \docauthorB}\\[3pt]
{\itshape \docaffiliationB}
```

## List of Acronyms

Update the acronyms section with all abbreviations used:

```latex
\section*{List of Acronyms}

\begin{tabular}{@{}ll@{}}
CCR & Cumulative Cost Ratio \\
DDT\&E & Design, Development, Test, and Evaluation \\
ISRU & In-Situ Resource Utilization \\
NASA & National Aeronautics and Space Administration \\
TM & Technical Memorandum \\
\end{tabular}
```

## Compilation

```bash
# From the latex/ directory:
pdflatex main.tex
biber main
pdflatex main.tex
pdflatex main.tex   # Run twice for cross-references

# Or if latexmk is available:
latexmk -pdf main.tex
```

## Common Issues

### Hyperref warnings about math in PDF strings
Use `\texorpdfstring` for math in section titles:
```latex
\subsection{Section with \texorpdfstring{$\times$}{x} symbol}
```

### Duplicate page.1 destination warning
This is normal due to page number reset between front matter and body. Can be ignored.

### Missing figures
Ensure `\graphicspath{{figures/}}` is set and figures are in that directory.

### Bibliography not appearing
Run `biber main` after first `pdflatex`, then `pdflatex` again.

## File Structure for Larger Documents

For documents with many sections:

```
paper/
├── latex/
│   ├── main.tex
│   ├── references.bib
│   ├── NASA_logo.svg.png
│   ├── figures/
│   │   ├── fig01_overview.png
│   │   ├── fig02_method.png
│   │   └── ...
│   └── sections/
│       ├── abstract.tex
│       ├── introduction.tex
│       ├── method.tex
│       ├── results.tex
│       └── discussion.tex
└── markdown/           # Source markdown files
    ├── 01-introduction.md
    ├── 02-method.md
    └── ...
```

## Style Notes

- Use 10pt Times-like font (mathptmx package)
- 1" side margins, 0.75" top/bottom
- Left-justified title page (not centered)
- Figures: `[htbp]` placement, `\centering`, width typically 0.8-0.85\textwidth
- Tables: caption above, `\toprule`/`\midrule`/`\bottomrule` from booktabs
- References: numeric style, citation order
