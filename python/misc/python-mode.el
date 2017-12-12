;;; Major mode for editing Python programs, version 1.06
;; by: Michael A. Guravage
;;     Guido van Rossum <guido@cwi.nl>
;;     Tim Peters <tim@ksr.com>
;;
;; Copyright (c) 1992  Tim Peters
;;
;; This software is provided as-is, without express or implied warranty.
;; Permission to use, copy, modify, distribute or sell this software,
;; without fee, for any purpose and by any individual or organization, is
;; hereby granted, provided that the above copyright notice and this
;; paragraph appear in all copies.
;;
;;
;; The following statements, placed in your .emacs file or site-init.el,
;; will cause this file to be autoloaded, and python-mode invoked, when
;; visiting .py files (assuming the file is in your load-path):
;;
;;	(autoload 'python-mode "python-mode" "" t)
;;	(setq auto-mode-alist
;;	      (cons '("\\.py$" . python-mode) auto-mode-alist))

(provide 'python-mode)

;;; Constants and variables

(defvar py-python-command "python"
  "*Shell command used to start Python interpreter.")

(defvar py-indent-offset 8		; argue with Guido <grin>
  "*Indentation increment.
Note that `\\[py-guess-indent-offset]' can usually guess a good value when you're
editing someone else's Python code.")

(defvar py-continuation-offset 2
  "*Indentation (in addition to py-indent-offset) for continued lines.
The additional indentation given to the first continuation line in a
multi-line statement.  Each subsequent continuation line in the
statement inherits its indentation from the line that precedes it, so if
you don't like the default indentation given to the first continuation
line, change it to something you do like and Python-mode will
automatically use that for the remaining continuation lines (or, until
you change the indentation again).")

(defvar py-block-comment-prefix "##"
  "*String used by py-comment-region to comment out a block of code.
This should follow the convention for non-indenting comment lines so
that the indentation commands won't get confused (i.e., the string
should be of the form `#x...' where `x' is not a blank or a tab, and
`...' is arbitrary).")

(defvar py-scroll-process-buffer t
  "*Scroll Python process buffer as output arrives.
If nil, the Python process buffer acts, with respect to scrolling, like
Shell-mode buffers normally act.  This is surprisingly complicated and
so won't be explained here; in fact, you can't get the whole story
without studying the Emacs C code.

If non-nil, the behavior is different in two respects (which are
slightly inaccurate in the interest of brevity):

  - If the buffer is in a window, and you left point at its end, the
    window will scroll as new output arrives, and point will move to the
    buffer's end, even if the window is not the selected window (that
    being the one the cursor is in).  The usual behavior for shell-mode
    windows is not to scroll, and to leave point where it was, if the
    buffer is in a window other than the selected window.

  - If the buffer is not visible in any window, and you left point at
    its end, the buffer will be popped into a window as soon as more
    output arrives.  This is handy if you have a long-running
    computation and don't want to tie up screen area waiting for the
    output.  The usual behavior for a shell-mode buffer is to stay
    invisible until you explicitly visit it.

Note the `and if you left point at its end' clauses in both of the
above:  you can `turn off' the special behaviors while output is in
progress, by visiting the Python buffer and moving point to anywhere
besides the end.  Then the buffer won't scroll, point will remain where
you leave it, and if you hide the buffer it will stay hidden until you
visit it again.  You can enable and disable the special behaviors as
often as you like, while output is in progress, by (respectively) moving
point to, or away from, the end of the buffer.

Warning:  If you expect a large amount of output, you'll probably be
happier setting this option to nil.

Obscure:  `End of buffer' above should really say `at or beyond the
process mark', but if you know what that means you didn't need to be
told <grin>.")

(defvar py-temp-directory
  (let ( (ok '(lambda (x)
		(and x
		     (setq x (expand-file-name x)) ; always true
		     (file-directory-p x)
		     (file-writable-p x)
		     x))))
    (or (funcall ok (getenv "TMPDIR"))
	(funcall ok "/usr/tmp")
	(funcall ok "/tmp")
	(funcall ok  ".")
	(error
	 "Couldn't find a usable temp directory -- set py-temp-directory")))
  "*Directory used for temp files created by a *Python* process.
By default, the first directory from this list that exists and that you
can write into:  the value (if any) of the environment variable TMPDIR,
/usr/tmp, /tmp, or the current directory.")

;; have to bind py-file-queue before installing the kill-emacs hook
(defvar py-file-queue nil
  "Queue of Python temp files awaiting execution.
Currently-active file is at the head of the list.")

;; arrange to kill temp files no matter what
;; have to trust that other people are as respectful of our hook
;; fiddling as we are of theirs
(if (boundp 'py-inherited-kill-emacs-hook)
    ;; we were loaded before -- trust others not to have screwed us
    ;; in the meantime (no choice, really)
    nil
  ;; else arrange for our hook to run theirs
  (setq py-inherited-kill-emacs-hook kill-emacs-hook)
  (setq kill-emacs-hook 'py-kill-emacs-hook))

(defvar py-beep-if-tab-change t
  "*Ring the bell if tab-width is changed.
If a comment of the form
\t# vi:set tabsize=<number>:
is found before the first code line when the file is entered, and
the current value of (the general Emacs variable) tab-width does not
equal <number>, tab-width is set to <number>, a message saying so is
displayed in the echo area, and if py-beep-if-tab-change is non-nil the
Emacs bell is also rung as a warning.")

(defvar py-mode-map nil "Keymap used in Python mode buffers.")
(if py-mode-map
    ()
  (setq py-mode-map (make-sparse-keymap))

  ;; shadow global bindings for newline-and-indent w/ the py- version
  (mapcar (function (lambda (key)
		      (define-key
			py-mode-map key 'py-newline-and-indent)))
   (where-is-internal 'newline-and-indent))

  (mapcar (function
	   (lambda (x)
	     (define-key py-mode-map (car x) (cdr x))))
	  '( ("\C-c\C-c" . py-execute-buffer)
	     ("\C-c|"	 . py-execute-region)
	     ("\C-c!"	 . py-shell)
	     ("\177"	 . py-delete-char)
	     ("\n"	 . py-newline-and-indent)
	     ("\C-c:"	 . py-guess-indent-offset)
	     ("\C-c\t"	 . py-indent-region)
	     ("\C-c<"	 . py-shift-region-left)
	     ("\C-c>"	 . py-shift-region-right)
	     ("\C-c\C-n" . py-next-statement)
	     ("\C-c\C-p" . py-previous-statement)
	     ("\C-c\C-u" . py-goto-block-up)
	     ("\C-c\C-b" . py-mark-block)
	     ("\C-c#"	 . py-comment-region)
	     ("\C-c\C-hm" . py-describe-mode)
	     ("\e\C-a"	 . beginning-of-python-def-or-class)
	     ("\e\C-e"	 . end-of-python-def-or-class)
	     ( "\e\C-h"	 . mark-python-def-or-class))))

(defvar py-mode-syntax-table nil "Python mode syntax table")
(if py-mode-syntax-table
    ()
  (setq py-mode-syntax-table (make-syntax-table))
  (mapcar (function
	   (lambda (x) (modify-syntax-entry
			(car x) (cdr x) py-mode-syntax-table)))
	  '(( ?\( . "()" ) ( ?\) . ")(" )
	    ( ?\[ . "(]" ) ( ?\] . ")[" )
	    ( ?\{ . "(}" ) ( ?\} . "){" )
	    ( ?\_ . "w" )
	    ( ?\' . "\"")	; single quote is string quote
	    ( ?\` . "$")	; backquote is open and close paren
	    ( ?\# . "<")	; hash starts comment
	    ( ?\n . ">"))))	; newline ends comment

;; a statement in Python opens a new block iff it ends with a colon;
;; while conceptually trivial, quoted strings, continuation lines, and
;; comments make this hard.  E.g., consider the statement
;; if \
;;      1 \
;;      :\
;;      \
;;      \
;;      # comment
;; here we define some regexps to help

(defconst py-stringlit-re "'\\([^'\n\\]\\|\\\\.\\)*'"
  "regexp matching a Python string literal")

;; warning!:  when [^#'\n\\] was written as [^#'\n\\]+ (i.e., with a
;; '+' suffix), this appeared to run 100x slower in some bad cases.
(defconst py-colon-line-re
  (concat
    "\\(" "[^#'\n\\]" "\\|" py-stringlit-re "\\|" "\\\\\n" "\\)*"
    ":"
    "\\(" "[ \t]\\|\\\\\n" "\\)*"
    "\\(#.*\\)?" "$")
  "regexp matching Python statements opening a new block")

;; this is tricky because a trailing backslash does not mean
;; continuation if it's in a comment
(defconst py-continued-re
  (concat
   "\\(" "[^#'\n\\]" "\\|" py-stringlit-re "\\)*"
   "\\\\$")
  "regexp matching Python lines that are continued")

(defconst py-blank-or-comment-re "[ \t]*\\($\\|#\\)"
  "regexp matching blank or comment lines")

;;; General Functions

(defun python-mode ()
  "Major mode for editing Python files.
Do `\\[py-describe-mode]' for detailed documentation.
Knows about Python indentation, tokens, comments and continuation lines.
Paragraphs are separated by blank lines only.

COMMANDS
\\{py-mode-map}
VARIABLES

py-indent-offset\tindentation increment
py-continuation-offset\textra indentation given to continuation lines
py-block-comment-prefix\tcomment string used by py-comment-region
py-python-command\tshell command to invoke Python interpreter
py-scroll-process-buffer\talways scroll Python process buffer
py-temp-directory\tdirectory used for temp files (if needed)
py-beep-if-tab-change\tring the bell if tab-width is changed"
  (interactive)
  (kill-all-local-variables)
  (setq  major-mode 'python-mode  mode-name "Python")
  (use-local-map py-mode-map)
  (set-syntax-table py-mode-syntax-table)

  (mapcar (function (lambda (x)
		      (make-local-variable (car x))
		      (set (car x) (cdr x))))
	  '( (paragraph-separate . "^[ \t]*$")
	     (paragraph-start	 . "^[ \t]*$")
	     (require-final-newline . t)
	     (comment-start .		"# ")
	     (comment-start-skip .	"# *")
	     (comment-column . 40)
	     (indent-line-function . py-indent-line)))

  ;; hack to allow overriding the tabsize in the file (see tokenizer.c)

  ;; not sure where the magic comment has to be; to save time searching
  ;; for a rarity, we give up if it's not found prior to the first
  ;; executable statement
  (let ( (case-fold-search nil)
	 (start (point))
	 new-tab-width)
    (if (re-search-forward
	 "^[ \t]*#[ \t]*vi:set[ \t]+tabsize=\\([0-9]+\\):"
	 (prog2 (py-next-statement 1) (point) (goto-char 1))
	 t)
	(progn
	  (setq new-tab-width
		(string-to-int
		 (buffer-substring (match-beginning 1) (match-end 1))))
	  (if (= tab-width new-tab-width)
	      nil
	    (setq tab-width new-tab-width)
	    (message "Caution: tab-width changed to %d" new-tab-width)
	    (if py-beep-if-tab-change (beep)))))
    (goto-char start))

  (run-hooks 'py-mode-hook))

;;; Functions that execute Python commands in a subprocess

(defun py-shell ()
  "Start an interactive Python interpreter in another window.
This is like Shell mode, except that Python is running in the window
instead of a shell.  See the `Interactive Shell' and `Shell Mode'
sections of the Emacs manual for details, especially for the key
bindings active in the `*Python*' buffer.

See the docs for variable py-scroll-buffer for info on scrolling
behavior in the process window.

Warning:  Don't use an interactive Python if you change sys.ps1 or
sys.ps2 from their default values, or if you're running code that prints
`>>> ' or `... ' at the start of a line.  Python mode can't distinguish
your output from Python's output, and assumes that `>>> ' at the start
of a line is a prompt from Python.  Similarly, the Emacs Shell mode code
assumes that both `>>> ' and `... ' at the start of a line are Python
prompts.  Bad things can happen if you fool either mode.

Warning:  If you do any editing *in* the process buffer *while* the
buffer is accepting output from Python, do NOT attempt to `undo' the
changes.  Some of the output (nowhere near the parts you changed!) may
be lost if you do.  This appears to be an Emacs bug, an unfortunate
interaction between undo and process filters; the same problem exists in
non-Python process buffers using the default (Emacs-supplied) process
filter."
  (interactive)
  (require 'shell)
  (switch-to-buffer-other-window (make-shell "Python" py-python-command))
  (make-local-variable 'shell-prompt-pattern)
  (setq shell-prompt-pattern "^>>> \\|^\\.\\.\\. ")
  (set-process-filter (get-buffer-process (current-buffer))
		      'py-process-filter)
  (set-syntax-table py-mode-syntax-table))

(defun py-execute-region (start end)
  "Send the region between START and END to a Python interpreter.
If there is a *Python* process it is used.

Hint:  If you want to execute part of a Python file several times (e.g.,
perhaps you're developing a function and want to flesh it out a bit at a
time), use `\\[narrow-to-region]' to restrict the buffer to the region of interest,
and send the code to a *Python* process via `\\[py-execute-buffer]' instead.

Following are subtleties to note when using a *Python* process:

If a *Python* process is used, the region is copied into a temp file (in
directory py-temp-directory), and an `execfile' command is sent to
Python naming that file.  If you send regions faster than Python can
execute them, Python mode will save them into distinct temp files, and
execute the next one in the queue the next time it sees a `>>> ' prompt
from Python.  Each time this happens, the process buffer is popped into
a window (if it's not already in some window) so you can see it, and a
comment of the form

\t## working on region in file <name> ...

is inserted at the end.

Caution:  No more than 26 regions can be pending at any given time.  This
limit is (indirectly) inherited from libc's mktemp(3).  Python mode does
not try to protect you from exceeding the limit.  It's extremely
unlikely that you'll get anywhere close to the limit in practice, unless
you're trying to be a jerk <grin>.

See the `\\[py-shell]' docs for additional warnings."
  (interactive "r")
  (or (< start end) (error "Region is empty"))
  (let ( (pyproc (get-process "Python"))
 	 fname)
    (if (null pyproc)
	(shell-command-on-region start end py-python-command)
      ;; else feed it thru a temp file
      (setq fname (py-make-temp-name))
      (write-region start end fname nil 'no-msg)
      (setq py-file-queue (append py-file-queue (list fname)))
      (if (cdr py-file-queue)
	  (message "File %s queued for execution" fname)
	;; else
	(py-execute-file pyproc fname)))))

(defun py-execute-file (pyproc fname)
  (py-append-to-process-buffer
   pyproc
   (format "## working on region in file %s ...\n" fname))
  (process-send-string pyproc (format "execfile('%s')\n" fname)))

(defun py-process-filter (pyproc string)
  (let ( (curbuf (current-buffer))
	 (pbuf (process-buffer pyproc))
	 (pmark (process-mark pyproc))
	 file-finished)

    ;; make sure we switch to a different buffer at least once.  if we
    ;; *don't* do this, then if the process buffer is in the selected
    ;; window, and point is before the end, and lots of output is coming
    ;; at a fast pace, then (a) simple cursor-movement commands like
    ;; C-p, C-n, C-f, C-b, C-a, C-e take an incredibly long time to have
    ;; a visible effect (the window just doesn't get updated, sometimes
    ;; for minutes(!)), and (b) it takes about 5x longer to get all the
    ;; process output (until the next python prompt).
    ;;
    ;; #b makes no sense to me at all.  #a almost makes sense:  unless we
    ;; actually change buffers, set_buffer_internal in buffer.c doesn't
    ;; set windows_or_buffers_changed to 1, & that in turn seems to make
    ;; the Emacs command loop reluctant to update the display.  Perhaps
    ;; the default process filter in process.c's read_process_output has
    ;; update_mode_lines++ for a similar reason?  beats me ...
    (if (eq curbuf pbuf)		; mysterious ugly hack
	(set-buffer (get-buffer-create "*scratch*")))

    (set-buffer pbuf)
    (let* ( (start (point))
	    (goback (< start pmark))
	    (buffer-read-only nil))
      (goto-char pmark)
      (insert string)
      (move-marker pmark (point))
      (setq file-finished
	    (and py-file-queue
		 (equal ">>> "
			(buffer-substring
			 (prog2 (beginning-of-line) (point)
				(goto-char pmark))
			 (point)))))
      (if goback (goto-char start)
	;; else
	(if py-scroll-process-buffer
	    (let* ( (pop-up-windows t)
		    (pwin (display-buffer pbuf)))
	      (set-window-point pwin (point))))))
    (set-buffer curbuf)
    (if file-finished
	(progn
	  (py-delete-file-silently (car py-file-queue))
	  (setq py-file-queue (cdr py-file-queue))
	  (if py-file-queue
		(py-execute-file pyproc (car py-file-queue)))))))

(defun py-execute-buffer ()
  "Send the contents of the buffer to a Python interpreter.
If there is a *Python* process buffer it is used.  If a clipping
restriction is in effect, only the accessible portion of the buffer is
sent.  A trailing newline will be supplied if needed.

See the `\\[py-execute-region]' docs for an account of some subtleties."
  (interactive)
  (py-execute-region (point-min) (point-max)))


;;; Functions for Python style indentation

(defun py-delete-char ()
  "Reduce indentation or delete character.
If point is at the leftmost column, deletes the preceding newline.

Else if point is at the leftmost non-blank character of a line that is
neither a continuation line nor a non-indenting comment line, or if
point is at the end of a blank line, reduces the indentation to match
that of the line that opened the current block of code.  The line that
opened the block is displayed in the echo area to help you keep track of
where you are.

Else the preceding character is deleted, converting a tab to spaces if
needed so that only a single column position is deleted."
  (interactive "*")
  (if (or (/= (current-indentation) (current-column))
	  (bolp)
	  (py-continuation-line-p)
	  (looking-at "#[^ \t\n]"))	; non-indenting #
      (backward-delete-char-untabify 1)
    ;; else indent the same as the colon line that opened the block

    ;; force non-blank so py-goto-block-up doesn't ignore it
    (insert-char ?* 1)
    (backward-char)
    (let ( (base-indent 0)		; indentation of base line
	   (base-text "")		; and text of base line
	   (base-found-p nil))
      (condition-case nil		; in case no enclosing block
	  (save-excursion
	    (py-goto-block-up 'no-mark)
	    (setq base-indent (current-indentation)
		  base-text   (py-suck-up-leading-text)
		  base-found-p t))
	(error nil))
      (delete-char 1)			; toss the dummy character
      (delete-horizontal-space)
      (indent-to base-indent)
      (if base-found-p
	  (message "Closes block: %s" base-text)))))

(defun py-indent-line ()
  "Fix the indentation of the current line according to Python rules."
  (interactive)
  (let* ( (ci (current-indentation))
	  (move-to-indentation-p (<= (current-column) ci))
	  (need (py-compute-indentation)) )
    (if (/= ci need)
	(save-excursion
	  (beginning-of-line)
	  (delete-horizontal-space)
	  (indent-to need)))
    (if move-to-indentation-p (back-to-indentation))))

(defun py-newline-and-indent ()
  "Strives to act like the Emacs newline-and-indent.
This is just `strives to' because correct indentation can't be computed
from scratch for Python code.  In general, deletes the whitespace before
point, inserts a newline, and takes an educated guess as to how you want
the new line indented."
  (interactive)
  (let ( (ci (current-indentation)) )
    (if (or (< ci (current-column))	; if point is beyond indentation
	    (looking-at "[ \t]*$"))	; or line is empty
	(newline-and-indent)
      ;; else try to act like newline-and-indent "normally" acts
      (beginning-of-line)
      (insert-char ?\n 1)
      (move-to-column ci))))

(defun py-compute-indentation ()
  (save-excursion
    (beginning-of-line)
    (cond
     ;; are we on a continuation line?
     ( (py-continuation-line-p)
       (forward-line -1)
       (if (py-continuation-line-p) ; on at least 3rd line in block
	   (current-indentation)    ; so just continue the pattern
	 ;; else on 2nd line in block, so indent more
	 (+ (current-indentation) py-indent-offset
	    py-continuation-offset)))
     ;; not on a continuation line

     ;; if at start of restriction, or on a non-indenting comment line,
     ;; assume they intended whatever's there
     ( (or (bobp) (looking-at "[ \t]*#[^ \t\n]"))
       (current-indentation) )

     ;; else indentation based on that of the statement that precedes
     ;; us; use the first line of that statement to establish the base,
     ;; in case the user forced a non-std indentation for the
     ;; continuation lines (if any)
     ( t
       ;; skip back over blank & non-indenting comment lines
       ;; note:  will skip a blank or non-indenting comment line that
       ;; happens to be a continuation line too
       (re-search-backward "^[ \t]*\\([^ \t\n#]\\|#[ \t\n]\\)"
			   nil 'move)
       (py-goto-initial-line)
       (if (looking-at py-colon-line-re)
	   (+ (current-indentation) py-indent-offset)
	 (current-indentation))))))

(defun py-guess-indent-offset (&optional global)
  "Guess a good value for, and change, py-indent-offset.
By default (without a prefix arg), makes a buffer-local copy of
py-indent-offset with the new value.  This will not affect any other
Python buffers.  With a prefix arg, changes the global value of
py-indent-offset.  This affects all Python buffers (that don't have
their own buffer-local copy), both those currently existing and those
created later in the Emacs session.

Some people use a different value for py-indent-offset than you use.
There's no excuse for such foolishness, but sometimes you have to deal
with their ugly code anyway.  This function examines the file and sets
py-indent-offset to what it thinks it was when they created the mess.

Specifically, it searches forward from the statement containing point,
looking for a line that opens a block of code.  py-indent-offset is set
to the difference in indentation between that line and the Python
statement following it.  If the search doesn't succeed going forward,
it's tried again going backward."
  (interactive "P")			; raw prefix arg
  (let ( new-value
	 (start (point))
	 restart
	 (found nil)
	 colon-indent)
    (py-goto-initial-line)
    (while (not (or found (eobp)))
      (if (re-search-forward ":[ \t]*\\($\\|[#\\]\\)" nil 'move)
	  (progn
	    (setq restart (point))
	    (py-goto-initial-line)
	    (if (looking-at py-colon-line-re)
		(setq found t)
	      (goto-char restart)))))
    (if found
	()
      (goto-char start)
      (py-goto-initial-line)
      (while (not (or found (bobp)))
	(setq found
	      (and
	       (re-search-backward ":[ \t]*\\($\\|[#\\]\\)" nil 'move)
	       (or (py-goto-initial-line) t) ; always true -- side effect
	       (looking-at py-colon-line-re)))))
    (setq colon-indent (current-indentation)
	  found (and found (zerop (py-next-statement 1)))
	  new-value (- (current-indentation) colon-indent))
    (goto-char start)
    (if found
	(progn
	  (funcall (if global 'kill-local-variable 'make-local-variable)
		   'py-indent-offset)
	  (setq py-indent-offset new-value)
	  (message "%s value of py-indent-offset set to %d"
		   (if global "Global" "Local")
		   py-indent-offset))
      (error "Sorry, couldn't guess a value for py-indent-offset"))))

(defun py-shift-region (start end count)
  (save-excursion
    (goto-char end)   (beginning-of-line) (setq end (point))
    (goto-char start) (beginning-of-line) (setq start (point))
    (indent-rigidly start end count)))

(defun py-shift-region-left (start end &optional count)
  "Shift region of Python code to the left.
The lines from the line containing the start of the current region up
to (but not including) the line containing the end of the region are
shifted to the left, by py-indent-offset columns.

If a prefix argument is given, the region is instead shifted by that
many columns."
  (interactive "*r\nP")   ; region; raw prefix arg
  (py-shift-region start end
		   (- (prefix-numeric-value
		       (or count py-indent-offset)))))

(defun py-shift-region-right (start end &optional count)
  "Shift region of Python code to the right.
The lines from the line containing the start of the current region up
to (but not including) the line containing the end of the region are
shifted to the right, by py-indent-offset columns.

If a prefix argument is given, the region is instead shifted by that
many columns."
  (interactive "*r\nP")   ; region; raw prefix arg
  (py-shift-region start end (prefix-numeric-value
			      (or count py-indent-offset))))

(defun py-indent-region (start end &optional indent-offset)
  "Reindent a region of Python code.
The lines from the line containing the start of the current region up
to (but not including) the line containing the end of the region are
reindented.  If the first line of the region has a non-whitespace
character in the first column, the first line is left alone and the rest
of the region is reindented with respect to it.  Else the entire region
is reindented with respect to the (closest code or indenting-comment)
statement immediately preceding the region.

This is useful when code blocks are moved or yanked, when enclosing
control structures are introduced or removed, or to reformat code using
a new value for the indentation offset.

If a numeric prefix argument is given, it will be used as the value of
the indentation offset.  Else the value of py-indent-offset will be
used.

Warning:  The region must be consistently indented before this function
is called!  This function does not compute proper indentation from
scratch (that's impossible in Python), it merely adjusts the existing
indentation to be correct in context.

Warning:  This function really has no idea what to do with non-indenting
comment lines, and shifts them as if they were indenting comment lines.
Fixing this appears to require telepathy.

Special cases:  whitespace is deleted from blank lines; continuation
lines are shifted by the same amount their initial line was shifted, in
order to preserve their relative indentation with respect to their
initial line; and comment lines beginning in column 1 are ignored."

  (interactive "*r\nP") ; region; raw prefix arg
  (save-excursion
    (goto-char end)   (beginning-of-line) (setq end (point-marker))
    (goto-char start) (beginning-of-line)
    (let ( (py-indent-offset (prefix-numeric-value
			      (or indent-offset py-indent-offset)))
	   (indents '(-1))	; stack of active indent levels
	   (target-column 0)	; column to which to indent
	   (base-shifted-by 0)	; amount last base line was shifted
	   (indent-base (if (looking-at "[ \t\n]")
			    (py-compute-indentation)
			  0))
	   ci)
      (while (< (point) end)
	(setq ci (current-indentation))
	;; figure out appropriate target column
	(cond
	 ( (or (eq (following-char) ?#)	; comment in column 1
	       (looking-at "[ \t]*$"))	; entirely blank
	   (setq target-column 0))
	 ( (py-continuation-line-p)	; shift relative to base line
	   (setq target-column (+ ci base-shifted-by)))
	 (t				; new base line
	  (if (> ci (car indents))	; going deeper; push it
	      (setq indents (cons ci indents))
	    ;; else we should have seen this indent before
	    (setq indents (memq ci indents)) ; pop deeper indents
	    (if (null indents)
		(error "Bad indentation in region, at line %d"
		       (save-restriction
			 (widen)
			 (1+ (count-lines 1 (point)))))))
	  (setq target-column (+ indent-base
				 (* py-indent-offset
				    (- (length indents) 2))))
	  (setq base-shifted-by (- target-column ci))))
	;; shift as needed
	(if (/= ci target-column)
	    (progn
	      (delete-horizontal-space)
	      (indent-to target-column)))
	(forward-line 1))))
  (set-marker end nil))

;;; Functions for moving point

(defun py-previous-statement (count)
  "Go to the start of previous Python statement.
If the statement at point is the i'th Python statement, goes to the
start of statement i-COUNT.  If there is no such statement, goes to the
first statement.  Returns count of statements left to move.
`Statements' do not include blank, comment, or continuation lines."
  (interactive "p") ; numeric prefix arg
  (if (< count 0) (py-next-statement (- count))
    (py-goto-initial-line)
    (let ( start )
      (while (and
	      (setq start (point)) ; always true -- side effect
	      (> count 0)
	      (zerop (forward-line -1))
	      (py-goto-statement-at-or-above))
	(setq count (1- count)))
      (if (> count 0) (goto-char start)))
    count))

(defun py-next-statement (count)
  "Go to the start of next Python statement.
If the statement at point is the i'th Python statement, goes to the
start of statement i+COUNT.  If there is no such statement, goes to the
last statement.  Returns count of statements left to move.  `Statements'
do not include blank, comment, or continuation lines."
  (interactive "p") ; numeric prefix arg
  (if (< count 0) (py-previous-statement (- count))
    (beginning-of-line)
    (let ( start )
      (while (and
	      (setq start (point)) ; always true -- side effect
	      (> count 0)
	      (py-goto-statement-below))
	(setq count (1- count)))
      (if (> count 0) (goto-char start)))
    count))

(defun py-goto-block-up (&optional nomark)
  "Move up to start of current block.
Go to the statement that starts the smallest enclosing block; roughly
speaking, this will be the closest preceding statement that ends with a
colon and is indented less than the statement you started on.  If
successful, also sets the mark to the starting point.

`\\[py-mark-block]' can be used afterward to mark the whole code block, if desired.

If called from a program, the mark will not be set if optional argument
NOMARK is not nil."
  (interactive)
  (let ( (start (point))
	 (found nil)
	 initial-indent)
    (py-goto-initial-line)
    ;; if on blank or non-indenting comment line, use the preceding stmt
    (if (looking-at "[ \t]*\\($\\|#[^ \t\n]\\)")
	(progn
	  (py-goto-statement-at-or-above)
	  (setq found (looking-at py-colon-line-re))))
    ;; search back for colon line indented less
    (setq initial-indent (current-indentation))
    (if (zerop initial-indent)
	;; force fast exit
	(goto-char (point-min)))
    (while (not (or found (bobp)))
      (setq found
	    (and
	     (re-search-backward ":[ \t]*\\($\\|[#\\]\\)" nil 'move)
	     (or (py-goto-initial-line) t) ; always true -- side effect
	     (< (current-indentation) initial-indent)
	     (looking-at py-colon-line-re))))
    (if found
	(progn
	  (or nomark (push-mark start))
	  (back-to-indentation))
      (goto-char start)
      (error "Enclosing block not found"))))

(defun beginning-of-python-def-or-class (&optional class)
  "Move point to start of def (or class, with prefix arg).

By default, looks for an appropriate `def'.  If you supply a prefix arg,
looks for a `class' instead.  The docs assume the `def' case; just
substitute `class' for `def' for the other case:

If point is on a blank or non-indenting comment line, moves back to
start of closest preceding code statement or indenting comment line.

If this is a `def' statement, leaves point at the start of it and
returns t.

Else searches for the smallest enclosing `def' block, leaves point at
the start of it and returns t (note that since class & def statements
can nest to arbitrary depths in Python, `smallest enclosing' doesn't
necessarily mean `closest preceding that's indented less'; this point is
subtle, and this remark is just to let you know that `smallest
enclosing' means what it says ...).

If no `def' statement can be found by those rules, leaves point at its
original location and signals an error.

If you just want to mark the def/class, see `\\[mark-python-def-or-class]'."
  (interactive "P")			; raw prefix arg
  (let ( (start (point))
	 (which (if class "class" "def")))
    (if (py-go-up-tree-to-keyword which)
	t
      (goto-char start)
      (error "Enclosing %s not found" which))))

(defun end-of-python-def-or-class (&optional class)
  "Move point beyond end of def (or class, with prefix arg) body.
See `\\[beginning-of-python-def-or-class]' docs for how the def (or class) is found.

Once the beginning statement is found, this function leaves point
immediately after the end of the body of this def (or class).  If it's a
one-liner (like `def onemore(n): return n+1'), point will move to the
start of the line immediately following the def or class statement.
Else point will move beyond the end of the body as defined in the docs
for `\\[py-mark-block]'.

If you just want to mark the def/class, see `\\[mark-python-def-or-class]'.

Returns the position of the start of the def or class."
  (interactive "P")			; raw prefix arg
  (beginning-of-python-def-or-class class)
  (prog1 (point) (py-goto-beyond-block)))

;;; Functions for marking regions

(defun py-mark-block (&optional extend just-move)
  "Mark following block of lines.  With prefix arg, mark structure.
Easier to use than explain.  It sets the region to an `interesting'
block of succeeding lines.  If point is on a blank line, it goes down to
the next non-blank line.  That will be the start of the region.  The end
of the region depends on the kind of line at the start:

 - If a comment, the region will include all succeeding comment lines up
   to (but not including) the next non-comment line (if any).

 - Else if a prefix arg is given, and the line begins one of these
   structures:
\tif elif else try except finally for while def class
   the region will be set to the body of the structure, including
   following blocks that `belong' to it, but excluding trailing blank
   and comment lines.  E.g., if on a `try' statement, the `try' block
   and all (if any) of the following `except' and `finally' blocks that
   belong to the `try' structure will be in the region.  Ditto for
   if/elif/else, for/else and while/else structures, and (a bit
   degenerate, since they're always one-block structures) def and class
   blocks.

 - Else if no prefix argument is given, and the line begins a Python
   block (see list above), and the block is not a `one-liner' (i.e., the
   statement ends with a colon, not with code), the region will include
   all succeeding lines up to (but not including) the next code
   statement (if any) that's indented no more than the starting line,
   except that trailing blank and comment lines are excluded.  E.g., if
   the starting line begins a multi-statement `def' structure, the
   region will be set to the full function definition, but without any
   trailing `noise' lines.

 - Else the region will include all succeeding lines up to (but not
   including) the next blank line, or code or indenting-comment line
   indented strictly less than the starting line.  Trailing indenting
   comment lines are included in this case, but not trailing blank
   lines.

A msg identifying the location of the mark is displayed in the echo
area; or do `\\[exchange-point-and-mark]' to flip down to the end.

If called from a program, optional argument EXTEND plays the role of the
prefix arg, and if optional argument JUST-MOVE is not nil, just moves to
the end of the block (& does not set mark or display a msg)."

  (interactive "P")			; raw prefix arg
  (py-goto-initial-line)
  ;; skip over blank lines
  (while (and
	  (looking-at "[ \t]*$")	; while blank line
	  (not (eobp)))			; & somewhere to go
    (forward-line 1))
  (if (eobp)
      (error "Hit end of buffer without finding a non-blank stmt"))
  (let ( (initial-pos (point))
	 (initial-indent (current-indentation))
	 last-pos			; position of last stmt in region
	 (followers
	  '( (if elif else) (elif elif else) (else)
	     (try except finally) (except except finally) (finally)
	     (for else) (while else)
	     (def) (class) ) )
	 first-symbol next-symbol)

    (cond
     ;; if comment line, suck up the following comment lines
     ((looking-at "[ \t]*#")
      (re-search-forward "^[ \t]*[^ \t#]" nil 'move) ; look for non-comment
      (re-search-backward "^[ \t]*#")	; and back to last comment in block
      (setq last-pos (point)))

     ;; else if line is a block line and EXTEND given, suck up
     ;; the whole structure
     ((and extend
	   (setq first-symbol (py-suck-up-first-keyword) )
	   (assq first-symbol followers))
      (while (and
	      (or (py-goto-beyond-block) t) ; side effect
	      (forward-line -1)		; side effect
	      (setq last-pos (point))	; side effect
	      (py-goto-statement-below)
	      (= (current-indentation) initial-indent)
	      (setq next-symbol (py-suck-up-first-keyword))
	      (memq next-symbol (cdr (assq first-symbol followers))))
	(setq first-symbol next-symbol)))

     ;; else if line *opens* a block, search for next stmt indented <=
     ((looking-at py-colon-line-re)
      (while (and
	      (setq last-pos (point))	; always true -- side effect
	      (py-goto-statement-below)
	      (> (current-indentation) initial-indent))
	nil))

     ;; else plain code line; stop at next blank line, or stmt or
     ;; indenting comment line indented <
     (t
      (while (and
	      (setq last-pos (point))	; always true -- side effect
	      (or (py-goto-beyond-final-line) t)
	      (not (looking-at "[ \t]*$")) ; stop at blank line
	      (or
	       (>= (current-indentation) initial-indent)
	       (looking-at "[ \t]*#[^ \t\n]"))) ; ignore non-indenting #
	nil)))

    ;; skip to end of last stmt
    (goto-char last-pos)
    (py-goto-beyond-final-line)

    ;; set mark & display
    (if just-move
	()				; just return
      (push-mark (point) 'no-msg)
      (forward-line -1)
      (message "Mark set after: %s" (py-suck-up-leading-text))
      (goto-char initial-pos))))

(defun mark-python-def-or-class (&optional class)
  "Set region to body of def (or class, with prefix arg) enclosing point.
Pushes the current mark, then point, on the mark ring (all language
modes do this, but although it's handy it's never documented ...).

See `\\[beginning-of-python-def-or-class]' docs for how the start of the def (or class, with
prefix arg) is found.  This command leaves point in the same place,
except that if the preceding line is blank, point is instead left at its
start (mostly for compatibility with other language modes; it's handy if
you get into the habit of leaving an empty line before def and class
stmts).  The mark is set immediately after the end of the def (or class,
with prefix arg), at the same place `\\[end-of-python-def-or-class]' leaves point."

  (interactive "P")			; raw prefix arg
  (push-mark (point))
  (let ( (start (end-of-python-def-or-class class)) )
    (push-mark (point))
    (goto-char (1- start))		; end of preceding line or bobp
    (if (= (current-indentation) (current-column))
	(beginning-of-line)
      ;; note that (forward-char 1) wouldn't work if def was at
      ;; start of restriction
      (goto-char start))))

(defun py-comment-region (start end &optional uncomment-p)
  "Comment out region of code; with prefix arg, uncomment region.
The lines from the line containing the start of the current region up
to (but not including) the line containing the end of the region are
commented out, by inserting the string py-block-comment-prefix at the
start of each line.  With a prefix arg, removes py-block-comment-prefix
from the start of each line instead."
  (interactive "*r\nP")   ; region; raw prefix arg
  (goto-char end)   (beginning-of-line) (setq end (point))
  (goto-char start) (beginning-of-line) (setq start (point))
  (let ( (prefix-len (length py-block-comment-prefix)) )
    (save-excursion
      (save-restriction
	(narrow-to-region start end)
	(while (not (eobp))
	  (if uncomment-p
	      (and (string= py-block-comment-prefix
			    (buffer-substring
			     (point) (+ (point) prefix-len)))
		   (delete-char prefix-len))
	    (insert py-block-comment-prefix))
	  (forward-line 1))))))

;;; Documentation functions

;; dump the long form of the mode blurb; does the usual doc escapes,
;; plus lines of the form ^[vc]:name$ to suck variable & command
;; docs out of the right places, along with the keys they're on &
;; current values
(defun py-dump-help-string (str)
  (with-output-to-temp-buffer "*Help*"
    (let ( (locals (buffer-local-variables))
	   funckind funcname func funcdoc
	   (start 0) mstart end
	   keys )
      (while (string-match "^%\\([vc]\\):\\(.+\\)\n" str start)
	(setq mstart (match-beginning 0)  end (match-end 0)
	      funckind (substring str (match-beginning 1) (match-end 1))
	      funcname (substring str (match-beginning 2) (match-end 2))
	      func (intern funcname))
	(princ (substitute-command-keys (substring str start mstart)))
	(cond
	 ( (equal funckind "c")		; command
	   (setq funcdoc (documentation func)
		 keys (concat
		       "Key(s): "
		       (mapconcat 'key-description
				  (where-is-internal func py-mode-map)
				  ", "))))
	 ( (equal funckind "v")		; variable
	   (setq funcdoc (substitute-command-keys
			  (get func 'variable-documentation))
		 keys (if (assq func locals)
			  (concat
			   "Local/Global values: "
			   (prin1-to-string (symbol-value func))
			   " / "
			   (prin1-to-string (default-value func)))
			(concat
			 "Value: "
			 (prin1-to-string (symbol-value func))))))
	 ( t				; unexpected
	   (error "Error in py-dump-help-string, tag `%s'" funckind)))
	(princ (format "\n-> %s:\t%s\t%s\n\n"
		       (if (equal funckind "c") "Command" "Variable")
		       funcname keys))
	(princ funcdoc)
	(terpri)
	(setq start end))
      (princ (substitute-command-keys (substring str start))))
    (print-help-return-message)))

(defun py-describe-mode ()
  "Dump long form of Python-mode docs."
  (interactive)
  (py-dump-help-string "Major mode for editing Python files.
Knows about Python indentation, tokens, comments and continuation lines.
Paragraphs are separated by blank lines only.

Major sections below begin with the string `@'; specific function and
variable docs begin with `->'.

@EXECUTING PYTHON CODE

\\[py-execute-buffer]\tsends the entire buffer to the Python interpreter
\\[py-execute-region]\tsends the current region
\\[py-shell]\tstarts a Python interpreter window; this will be used by
\tsubsequent \\[py-execute-buffer] or \\[py-execute-region] commands
%c:py-execute-buffer
%c:py-execute-region
%c:py-shell

@VARIABLES

py-indent-offset\tindentation increment
py-continuation-offset\textra indentation given to continuation lines
py-block-comment-prefix\tcomment string used by py-comment-region

py-python-command\tshell command to invoke Python interpreter
py-scroll-process-buffer\talways scroll Python process buffer
py-temp-directory\tdirectory used for temp files (if needed)

py-beep-if-tab-change\tring the bell if tab-width is changed
%v:py-indent-offset
%v:py-continuation-offset
%v:py-block-comment-prefix
%v:py-python-command
%v:py-scroll-process-buffer
%v:py-temp-directory
%v:py-beep-if-tab-change

@KINDS OF LINES

Each physical line in the file is either a `continuation line' (the
preceding line ends with a backslash that's not part of a comment) or an
`initial line' (everything else).

An initial line is in turn a `blank line' (contains nothing except
possibly blanks or tabs), a `comment line' (leftmost non-blank character
is `#'), or a `code line' (everything else).

Comment Lines

Although all comment lines are treated alike by Python, Python mode
recognizes two kinds that act differently with respect to indentation.

An `indenting comment line' is a comment line with a blank, tab or
nothing after the initial `#'.  The indentation commands (see below)
treat these exactly as if they were code lines:  a line following an
indenting comment line will be indented like the comment line.  All
other comment lines (those with a non-whitespace character immediately
following the initial `#') are `non-indenting comment lines', and their
indentation is ignored by the indentation commands.

Indenting comment lines are by far the usual case, and should be used
whenever possible.  Non-indenting comment lines are useful in cases like
these:

\ta = b   # a very wordy single-line comment that ends up being
\t        #... continued onto another line

\tif a == b:
##\t\tprint 'panic!' # old code we've `commented out'
\t\treturn a

Since the `#...' and `##' comment lines have a non-whitespace character
following the initial `#', Python mode ignores them when computing the
proper indentation for the next line.

Continuation Lines and Statements

The Python-mode commands generally work on statements instead of on
individual lines, where a `statement' is a comment or blank line, or a
code line and all of its following continuation lines (if any)
considered as a single logical unit.  The commands in this mode
generally (when it makes sense) automatically move to the start of the
statement containing point, even if point happens to be in the middle of
some continuation line.

A Bad Idea

Always put something on the initial line of a multi-line statement
besides the backslash!  E.g., don't do this:

\t\\
\ta = b # what's the indentation of this stmt?

While that's legal Python, it's silly & would be very expensive for
Python mode to handle correctly.

@INDENTATION

Primarily for entering new code:
\t\\[indent-for-tab-command]\t indent line appropriately
\t\\[py-newline-and-indent]\t insert newline, then indent
\t\\[py-delete-char]\t reduce indentation, or delete single character

Primarily for reindenting existing code:
\t\\[py-guess-indent-offset]\t guess py-indent-offset from file content; change locally
\t\\[universal-argument] \\[py-guess-indent-offset]\t ditto, but change globally

\t\\[py-indent-region]\t reindent region to match its context
\t\\[py-shift-region-left]\t shift region left by py-indent-offset
\t\\[py-shift-region-right]\t shift region right by py-indent-offset

Unlike most programming languages, Python uses indentation, and only
indentation, to specify block structure.  Hence the indentation supplied
automatically by Python-mode is just an educated guess:  only you know
the block structure you intend, so only you can supply correct
indentation.

The \\[indent-for-tab-command] and \\[py-newline-and-indent] keys try to suggest plausible indentation, based on
the indentation of preceding statements.  E.g., assuming
py-indent-offset is 4, after you enter
\tif a > 0: \\[py-newline-and-indent]
the cursor will be moved to the position of the `_' (_ is not a
character in the file, it's just used here to indicate the location of
the cursor):
\tif a > 0:
\t    _
If you then enter `c = d' \\[py-newline-and-indent], the cursor will move
to
\tif a > 0:
\t    c = d
\t    _
Python-mode cannot know whether that's what you intended, or whether
\tif a > 0:
\t    c = d
\t_
was your intent.  In general, Python-mode either reproduces the
indentation of the (closest code or indenting-comment) preceding
statement, or adds an extra py-indent-offset blanks if the preceding
statement has `:' as its last significant (non-whitespace and non-
comment) character.  If the suggested indentation is too much, use
\\[py-delete-char] to reduce it.

Warning:  indent-region should not normally be used!  It calls \\[indent-for-tab-command]
repeatedly, and as explained above, \\[indent-for-tab-command] can't guess the block
structure you intend.
%c:indent-for-tab-command
%c:py-newline-and-indent
%c:py-delete-char


The next function may be handy when editing code you didn't write:
%c:py-guess-indent-offset


The remaining `indent' functions apply to a region of Python code.  They
assume the block structure (equals indentation, in Python) of the region
is correct, and alter the indentation in various ways while preserving
the block structure:
%c:py-indent-region
%c:py-shift-region-left
%c:py-shift-region-right

@MARKING & MANIPULATING REGIONS OF CODE

\\[py-mark-block]\t mark block of lines
\\[mark-python-def-or-class]\t mark smallest enclosing def
\\[universal-argument] \\[mark-python-def-or-class]\t mark smallest enclosing class
\\[py-comment-region]\t comment out region of code
\\[universal-argument] \\[py-comment-region]\t uncomment region of code
%c:py-mark-block
%c:mark-python-def-or-class
%c:py-comment-region

@MOVING POINT

\\[py-previous-statement]\t move to statement preceding point
\\[py-next-statement]\t move to statement following point
\\[py-goto-block-up]\t move up to start of current block
\\[beginning-of-python-def-or-class]\t move to start of def
\\[universal-argument] \\[beginning-of-python-def-or-class]\t move to start of class
\\[end-of-python-def-or-class]\t move to end of def
\\[universal-argument] \\[end-of-python-def-or-class]\t move to end of class

The first two move to one statement beyond the statement that contains
point.  A numeric prefix argument tells them to move that many
statements instead.  Blank lines, comment lines, and continuation lines
do not count as `statements' for these commands.  So, e.g., you can go
to the first code statement in a file by entering
\t\\[beginning-of-buffer]\t to move to the top of the file
\t\\[py-next-statement]\t to skip over initial comments and blank lines
Or do `\\[py-previous-statement]' with a huge prefix argument.
%c:py-previous-statement
%c:py-next-statement
%c:py-goto-block-up
%c:beginning-of-python-def-or-class
%c:end-of-python-def-or-class

@LITTLE-KNOWN EMACS COMMANDS PARTICULARLY USEFUL IN PYTHON MODE

`\\[indent-new-comment-line]' is handy for entering a multi-line comment.

`\\[set-selective-display]' with a `small' prefix arg is ideally suited for viewing the
overall class and def structure of a module.

`\\[back-to-indentation]' moves point to a line's first non-blank character.

`\\[indent-relative]' is handy for creating odd indentation.

@OTHER EMACS HINTS

If you don't like the default value of a variable, change its value to
whatever you do like by putting a `setq' line in your .emacs file.
E.g., to set the indentation increment to 4, put this line in your
.emacs:
\t(setq  py-indent-offset  4)
To see the value of a variable, do `\\[describe-variable]' and enter the variable
name at the prompt.

When entering a key sequence like `C-c C-n', it is not necessary to
release the CONTROL key after doing the `C-c' part -- it suffices to
press the CONTROL key, press and release `c' (while still holding down
CONTROL), press and release `n' (while still holding down CONTROL), &
then release CONTROL.

Entering Python mode calls with no arguments the value of the variable
`py-mode-hook', if that value exists and is not nil; see the `Hooks'
section of the Elisp manual for details.

Obscure:  When python-mode is first loaded, it looks for all bindings
to newline-and-indent in the global keymap, and shadows them with
local bindings to py-newline-and-indent."))

;;; Helper functions

;; go to initial line of current statement; usually this is the
;; line we're on, but if we're on the 2nd or following lines of a
;; continuation block, we need to go up to the first line of the block
(defun py-goto-initial-line ()
  (while (py-continuation-line-p)
    (forward-line -1))
  (beginning-of-line))

;; go to point right beyond final line of current statement; usually
;; this is the start of the next line, but if this is a multi-line
;; statement we need to skip over the continuation lines
(defun py-goto-beyond-final-line ()
  (forward-line 1)
  (while (and (py-continuation-line-p)
	      (not (eobp)))
    (forward-line 1)))

;; go to point right beyond final line of block begun by the current
;; line.  This is the same as where py-goto-beyond-final-line goes
;; unless we're on colon line, in which case we go to the end of the
;; block.
;; assumes point is at bolp
(defun py-goto-beyond-block ()
  (if (looking-at py-colon-line-re)
      (py-mark-block nil 'just-move)
    (py-goto-beyond-final-line)))

;; t iff on continuation line == preceding line ends with backslash
;; that's not in a comment
(defun py-continuation-line-p ()
  (save-excursion
    (beginning-of-line)
    (and
     ;; use a cheap test first to avoid the regexp if possible
     ;; use 'eq' because char-after may return nil
     (eq (char-after (- (point) 2)) ?\\ )
     ;; make sure; since eq test passed, there is a preceding line
     (forward-line -1) ; always true -- side effect
     (looking-at py-continued-re))))

;; go to start of first statement (not blank or comment or continuation
;; line) at or preceding point
;; returns t if there is one, else nil
(defun py-goto-statement-at-or-above ()
  (py-goto-initial-line)
  (if (looking-at py-blank-or-comment-re)
	;; skip back over blank & comment lines
	;; note:  will skip a blank or comment line that happens to be
	;; a continuation line too
	(if (re-search-backward "^[ \t]*[^ \t#\n]" nil t)
	    (progn (py-goto-initial-line) t)
	  nil)
    t))

;; go to start of first statement (not blank or comment or continuation
;; line) following the statement containing point
;; returns t if there is one, else nil
(defun py-goto-statement-below ()
  (beginning-of-line)
  (let ( (start (point)) )
    (py-goto-beyond-final-line)
    (while (and
	    (looking-at py-blank-or-comment-re)
	    (not (eobp)))
      (forward-line 1))
    (if (eobp)
	(progn (goto-char start) nil)
      t)))

;; go to start of statement, at or preceding point, starting with keyword
;; KEY.  Skips blank lines and non-indenting comments upward first.  If
;; that statement starts with KEY, done, else go back to first enclosing
;; block starting with KEY.
;; If successful, leaves point at the start of the KEY line & returns t.
;; Else leaves point at an undefined place & returns nil.
(defun py-go-up-tree-to-keyword (key)
  ;; skip blanks and non-indenting #
  (py-goto-initial-line)
  (while (and
	  (looking-at "[ \t]*\\($\\|#[^ \t\n]\\)")
	  (zerop (forward-line -1)))	; go back
    nil)
  (py-goto-initial-line)
  (let* ( (re (concat "[ \t]*" key "\\b"))
	  (case-fold-search nil)	; let* so looking-at sees this
	  (found (looking-at re))
	  (dead nil))
    (while (not (or found dead))
      (condition-case nil		; in case no enclosing block
	  (py-goto-block-up 'no-mark)
	(error (setq dead t)))
      (or dead (setq found (looking-at re))))
    (beginning-of-line)
    found))

;; return string in buffer from start of indentation to end of line;
;; prefix "..." if leading whitespace was skipped
(defun py-suck-up-leading-text ()
  (save-excursion
    (back-to-indentation)
    (concat
     (if (bolp) "" "...")
     (buffer-substring (point) (progn (end-of-line) (point))))))

;; assuming point at bolp, return first keyword ([a-z]+) on the line,
;; as a Lisp symbol; return nil if none
(defun py-suck-up-first-keyword ()
  (let ( (case-fold-search nil) )
    (if (looking-at "[ \t]*\\([a-z]+\\)\\b")
	(intern (buffer-substring (match-beginning 1) (match-end 1)))
      nil)))

(defun py-make-temp-name ()
  (make-temp-name
   (concat (file-name-as-directory py-temp-directory) "python")))

(defun py-delete-file-silently (fname)
  (condition-case nil
      (delete-file fname)
    (error nil)))

(defun py-kill-emacs-hook ()
  ;; delete our temp files
  (while py-file-queue
    (py-delete-file-silently (car py-file-queue))
    (setq py-file-queue (cdr py-file-queue)))
  ;; run the hook we inherited, if any
  (and py-inherited-kill-emacs-hook
       (funcall py-inherited-kill-emacs-hook)))

;; make PROCESS's buffer visible, append STRING to it, and force display;
;; also make shell-mode believe the user typed this string, so that
;; kill-output-from-shell and show-output-from-shell work "right"
(defun py-append-to-process-buffer (process string)
  (let ( (cbuf (current-buffer))
	 (pbuf (process-buffer process))
	 (py-scroll-process-buffer t))
    (set-buffer pbuf)
    (goto-char (point-max))
    (move-marker (process-mark process) (point))
    (move-marker last-input-start (point)) ; muck w/ shell-mode
    (funcall (process-filter process) process string)
    (move-marker last-input-end (point)) ; muck w/ shell-mode
    (set-buffer cbuf))
  (sit-for 0))

;; To do:
;; - support for ptags
