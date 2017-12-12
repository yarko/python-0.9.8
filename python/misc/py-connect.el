(require 'comint)
;;; python-connect.el
;;;
;;; Author
;;; Terrence M. Brannon
;;;
;;; Project
;;; Allow the creation of multiple emacs objects which can be queried
;;; and commanded. Primary reason is to use ange-ftp from python since
;;; it is a big headache to re-code all of ange-ftp in python - plus
;;; why re-invent the wheel.
;;; 
;;; Technique
;;; Basically we spawn a python interpreter as an inferior process of
;;; emacs and then filter its output . If we get a string delimited
;;; by the start and end markers then we evaluate it.
;;;
;;; Requirements
;;; comint.el available from:
;;; "/anonymous@archive.cis.ohio-state.edu:pub/gnu/emacs/elisp-archive/as-is"
;;; python 0.9.7, available from:
;;; "/anonymous@ftp.cwi.nl:pub"
;;;
;;; Usage
;;; C-x C-f py-connect.el
;;; M-x eval-current-buffer
;;; M-x py-connect
;;; At the python prompt (>>>) type import emacs.
;;; Now at the python prompt you may call any of the defined modules.
;;; ex: emacs.dired('.')
;;; You may also type elisp strings delimited by + and ~ and they will
;;; be evaluated in emacs after you hit return.
;;; ex: +(copy-file "/anonymous@princeton.edu:yoga" "my-yoga" t)~
;;;
;;; SCOPES FOR IMPROVEMENT
;;; an extremely robust interface would allow one to do completion by
;;; sending an obarray/assoc list and complete-file-name command to
;;; emacs . then get back the results
;;;
;;; Another project
;;; Another possibility is to make it so you can run python without it being
;;; on your local machine - just telnet to the Python interpreter port and
;;; tell it whether you are using x-windows or whatnot.
;;; - games
;;; - demos . see where they are calling from . ange-ftp a file to their
;;;   home directory
;;; - portmapper
;;;
;;; Another project
;;; NOTE: remote emacs-code becomes executable if it shows up in a buffer
;;; because emacs has a built in interpreter . if we have
;;; self-intelligent interpreters, they can show up on your remote
;;; machine and do their work, remember the results, and leave. just
;;; tell the objects what to do and they head over to the correct
;;; machine and do it

(setq start-mkr ?+)
(setq start-mkr-string (char-to-string ?+))
(setq end-mkr-string (char-to-string ?~))

(setq accum-string "")

(defun py-connect ()
  (interactive)
  (cond ((not (comint-check-proc "*py-connect*"))
	 (let* ((prog "python")
		(name (file-name-nondirectory prog)))
	   (set-buffer (apply 'make-comint "py-connect" (list prog)))
	   (comint-mode))))
  (switch-to-buffer "*py-connect*")
  (setq comint-prompt-regexp ">>>")
  (setq P (get-buffer-process (current-buffer)))
  (set-process-filter P 'elisp-filter))

(defun elisp-filter (process string)
  "Make sure that the window continues to show the most recently output
text."

  (let ((old-buffer (current-buffer)))
    (unwind-protect
	(let (moving)
	  (set-buffer (process-buffer process))
	  (setq moving (= (point) (process-mark process)))
	  (save-excursion
	    (goto-char (process-mark process))
	    (insert string)
	    (set-marker (process-mark process) (point)))
	  (if moving (goto-char (process-mark process))))
      (set-buffer old-buffer)))

  (while (not (string-equal string ""))
    (let ((s (string-match start-mkr-string string))
	  (e (string-match end-mkr-string string)))
      (if (string-equal accum-string "")
	  (progn
	    (setq expecting 'start-marker)
	    (if s
		(progn
		  (setq expecting 'end-marker)
		  (if e 
		      (progn
			(interp-elisp (substring string (1+ s) e))
			(setq string (substring string (1+ e))))
		    (progn
		      (setq accum-string (substring string (1+ s)))
		      (setq string ""))))
	      (setq string "")))
	(if e
	    (progn
	      (interp-elisp (concat accum-string (substring string 0 (1- e))))
	      (setq string (substring string (1+ e))))
	  (setq accum-string (concat accum-string string))
	  (setq string ""))))))
    
  
(defun interp-elisp (string)
  (eval (read string)))
	      
;;; hacking from here on out -- ignore (or enjoy)


(defun filter-accum-command (string)
  "This function is only called to reset the systems idea of the
currently accumulated output from the process if output is already in
accum-string and possibly evaluate this output if end-mkr is seen.
What it does is check for the first start-mkr and end-mkr in the
string. If neither exists, <return> the concatenation of string onto
accum-string and <exit>. If start-mkr is first, then the accumulated
string is reset to STRING from start-mkr+1 onward and we recursively
call this function. If end-mkr is first, then we evaluate (concat
accum-string STRING up-to-end-mkr), search for the next start-mkr. If
no start-mkr, <return> empty quotes and <exit>. If a start-mkr,
<return> from start-mkr to end of STRING and <exit>"
  (debug)
  (let* ((s (string-match start-mkr-string string))
	 (e (string-match   end-mkr-string string)))
    (cond 
     ((and (not s) (not e)) 
      (concat accum-string string))
     ((or (< s e) (and s (not e)))
      (filter-accum-command (substring (1+ s) string)))
     ((or (< e s) (and e (not s)))
      (progn
	(interpret-elisp (concat accum-string (substring 0 (1- e)
							 string)))
	(setq string (substring (1+ e) string))
	(let ((st (string-match start-mkr-string string)))
	  (if st
	      (substring string (1+ st))
	    ""))
	)
      )
     )
    )
  )

(defun interpret-elisp (str)
  (message str)
  (eval (car (read-from-string str))))



(defun old-elisp-filter (proc string)
  (interactive)
  ;;; Cases -
  ;;;
  ;;; (0) if accum-string == "", (0.5) expect a start marker. 
  ;;; (1.0) accum-string will equal start-marker to finish-marker or
  ;;; start-marker to end of string. if accum-string went to end of
  ;;; string, exit. (1.5) else eval the region, chop the region from the
  ;;; string, set  
  ;;; accum-string to "" and retry (0)
  ;;; (2) if accum-string != "", expect a finish marker. if we get a
  ;;; finish marker, (2.5) concat accum string and string up to finish
  ;;; marker, evaluate then pass the remainder of the stream to (0).
  ;;; (3.0) if we get a start-marker, set accum-string to "" , prepend
  ;;; start-marker to string and goto (0). (3.5) if we get neither, append
  ;;; all of string to accum-string, set accum-string to "", then exit

  (if (string-equal accum-string "")
      (case-0 string)
    (case-2 string)))

(defun case-0 (string)
  (let ((count 0)
	(lth (length string)))
    (while (not (equal (elt string count) start-mkr))
		(setq count (1+ count)))
    (if (equal count lth)
	()
      (progn
	(setq accum-string (do-1-0))
	(if eos
	    ()
	  (progn
	    (do-1-5)
	    (setq accum-string "")
	    (case-0 string)))))))

(defun case-2 (string)
  (let ((count 0)
	(lth (length string)))
    (while (not (or (equal (elt string count) start-mkr)
		    (equal (elt string count) end-mkr)))
      (setq count (1+ count)))
    (if (equal count lth)
	(do-3-5))
    (if (equal (elt string count) end-mkr)
	(progn
	  (setq string (do-2-5 string))
	  (setq accum-string "")
	  (case-0 string))
      (progn
	(setq accum-string "")
	(setq newstr (concat start-mkr string))
	(case-0 newstr)))))
  

;(comint-proc-query P "\na = [2 , 3, 4] \n")

(defun t ()
  (interactive)
  (pop-to-buffer "*py-connect*")
  (setq comint-eol-on-send 't)
  (visi-input "a = [ 4 ,5 ,6 ] ")
  (visi-input "a"))

(defun visi-input (string)
  (message string)
  (sit-for 1)
  (goto-char (point-max))
  (let* ((end (point))
	 (start (progn
		  (beginning-of-line 1)
		  (point)))
	 (line (buffer-substring start end)))
    (while (not (string-match "[ ]*" line))

      (setq end (point))
      (setq start (progn
		    (beginning-of-line 1)
		    (point)))
      (setq line (buffer-substring start end)))
    (goto-char (point-max))
    (insert string)
    (comint-send-input)
    (goto-char (point-max))))
