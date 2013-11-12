from latexslides import *

template=r"""
\setbeamertemplate{footline}%{miniframes theme}
{%
\begin{beamercolorbox}[ht=2.5ex,dp=1.125ex,%
  leftskip=.3cm,rightskip=.3cm plus1fil]{title in head/foot}%
  {\usebeamerfont{title in head/foot}\insertshorttitle} \hfill     \insertframenumber%
\end{beamercolorbox}%
\begin{beamercolorbox}[colsep=1.5pt]{lower separation line foot}
\end{beamercolorbox}
}
\setbeamertemplate{headline}%{miniframes theme}
{%
\begin{beamercolorbox}[colsep=1.5pt]{upper separation line foot}
\end{beamercolorbox}
\begin{beamercolorbox}[ht=2.5ex,dp=1.125ex,%
  leftskip=.3cm,rightskip=.3cm plus1fil]{author in head/foot}%
  \leavevmode{\usebeamerfont{author in head/foot}\insertauthor}%
  \hfill%
  {\usebeamerfont{institute in head/foot}\usebeamercolor[fg]{institute in head/foot}\insertshortinstitute}%
\end{beamercolorbox}%
}
"""


# Set authors
authors = [("Nick Edwards", r"University of Edinburgh\\ \medskip \textit{nedwards@cern.ch}")]

# Create slides, exchange 'Beamer' with 'Prosper' for Prosper
def NickSlides(title):
    slides = BeamerSlides(title="FATRAS Tracking Validation",
                          author_and_inst=authors,
                          short_inst="University of Edinburgh",
                          beamer_theme='Szeged',
                          beamer_colour_theme='dolphin',
                          toc_heading=None,
                          latexpackages=template
                          )
    return slides
