
def DocumentHeadings():

    texstr = "\\documentclass[a4paper,11pt]{article}\n" 
    #texstr = "\\documentclass[a4paper,11pt,landscape]{article}\n" 
    texstr += "\\usepackage{graphicx}\n" 
    texstr += "\\usepackage{longtable}\n" 
    texstr += "\\usepackage{hyperref} \n" 
    texstr += "\\usepackage{multirow} \n" 
    texstr += "\\setcounter{tocdepth}{3}\n" 
    texstr += "\\usepackage[a4paper,top=2cm,bottom=2cm,left=2cm,right=2cm]{geometry}\n" 
    texstr += "\\begin{document}\n" 
    texstr += "\\def\\ZZ{ZZ}"
    texstr += "\\def\\ZZs{ZZ*}"

    return texstr

def ListToTable(list, titles, caption = "", small=False):

    texstr = "\\begin{table}[htbp]\n"
    if small:
        texstr += "\\small\n"
    texstr += "\\centering\n"
    texstr += "\\begin{tabular}{l"+"|c"*(len(list[0])-1)+"}\n"
    texstr += "\\hline\\hline\n"
    if type(titles) == type([]):
        texstr += " & ".join(titles) +" \\\\\n"
    else:
        texstr += titles
    texstr += "\\hline\n"

    # Loop once to get max lengths
    column_max_lengths = [0,] * len(list[0])
    for row in list :
        #for cell, formatstr in zip(row , formatstr_list)
        for iCell in range(len(row)):
            if len(row[iCell]) > column_max_lengths[iCell]:
                column_max_lengths[iCell] = len(row[iCell])

    #import pdb
    #pdb.set_trace()

    for row in list :
        #for cell, formatstr in zip(row , formatstr_list)
        for cell,col_length in zip(row,column_max_lengths) :
            formatstr = "%%%is" % (col_length)
            texstr += formatstr % (cell) + " &  "
            #texstr += cell + " &  "
        texstr = texstr[:-3] + "\\\\\n"

    texstr += ""
    texstr += "\\hline\\hline\n"
    texstr += "\\end{tabular}\n"
    if caption:
        texstr += "\\caption{"+caption+"}\n"
    texstr += "\\end{table}\n"

    return texstr

def DocumentFooters():

    texstr = "\\end{document}\n"
    return texstr

def clean_tex(str):

    str = str.replace("_", "\\_")
    return str

def Image(filenames, caption="", width=None):

    caption = clean_tex(caption)

    textstr = "\\begin{figure}[h]\n"
    for filename in filenames:
        if width:
            textstr += "\\includegraphics[width=%s]{%s}\n" % (str(width), filename)
        else:
            textstr += "\\includegraphics[]{{%s}}\n" % (filename)

    textstr += "\\caption{%s}\n" % (caption,)
    textstr += "\\end{figure}\n\n"
    return textstr

def ClearPage():
    textstr = "\\clearpage\n\n"
    return textstr

def TableOfContents():
    texstr = "\\tableofcontents\n\n" 
    texstr += ClearPage()
    return texstr

def Section(name):
    name = clean_tex(name)
    textstr = "\\section{%s}\n\n" % (name,)
    return textstr

