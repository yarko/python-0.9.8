(fset 'verb2tt
   "\\verb{\\tt 1}")
(re-search-forward "\\\\tt[ 	]*$")
(query-replace-regexp "^\\(\\\\\\(\\(chapter\\)\\|\\(\\(sub\\)*section\\)\\).*\\){\\\\tt " "\\1\\\\sectcode{" nil)
(query-replace "{\\tt " "\\code{" nil)
(query-replace "{\\tt " "\\var{" nil)
(fset 'item2env
   "\\\\....?item{5�descb@W�begin{\\\\\\\\....?item^[\\
]^[^\\
]q\\end{")
(fset 'fixcommas
   "\\\\begin{funcdesc}.*, n%,\\\\,!w")
(fset 'fixparens
   "\\\\begin{funcdesc}.*[()] n%\\([()]\\)\\\\\\1!w")
(query-replace-regexp "{\\\\\\(UNIX\\|ABC\\|ASCII\\|C\\|EOF\\)}" "\\\\\\1{}" nil)
