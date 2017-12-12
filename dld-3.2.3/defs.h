/* defs.h -- global definitions. */

/* This file is part of DLD, a dynamic link/unlink editor for C.
   
   Copyright (C) 1990 by W. Wilson Ho.

   The author can be reached electronically by how@ivy.ucdavis.edu or
   through physical mail at:

   W. Wilson Ho
   Division of Computer Science
   University of California at Davis
   Davis, CA 95616
 */

/* This program is free software; you can redistribute it and/or modify it
   under the terms of the GNU General Public License as published by the
   Free Software Foundation; either version 1, or (at your option) any
   later version. */


#include <a.out.h>
#include <ar.h>
#include <stdio.h>
#include <sys/types.h>
#include <strings.h>
#include <sys/stat.h>
#include <sys/file.h>
#include <sys/param.h>
#include <setjmp.h>
#include "dld.h"

/* Each input file, and each library member ("subfile") being loaded,
   has a `file_entry' structure for it.

   For files specified by command args, these are contained in the vector
   which `file_table' points to.

   For library members, they are dynamically allocated,
   and chained through the `chain' field.
   The chain is found in the `subfiles' field of the `file_entry'.
   The `file_entry' objects for the members have `superfile' fields pointing
   to the one for the library.  */

struct file_entry {
    /* Name of this file.  */
    char *filename;
    /* Name to use for the symbol giving address of text start */
    /* Usually the same as filename, but for a file spec'd with -l
       this is the -l switch itself rather than the filename.  */
    char *local_sym_name;

    /* For library member, points to next entry for next member.
       For object or library *file*, points to previously loaded entry */
    struct file_entry *chain;

    /* number of undefined symbols referenced by this module */
    int undefined_symbol_count;
  
    /* chain of file_entry that defines symbols this file references */
    struct file_chain *refs;

    /* chain of file_entry that references symbols defined in this file */
    struct file_chain *refs_by;
  
    /* reference count -- number of entries referenceing myself */
    int ref_count;
    
    /* Describe the layout of the contents of the file */

    /* The file's a.out header.  */
    struct exec header;

    /* Describe data from the file loaded into core */

    /* Symbol table of the file.  */
    struct nlist *symbols;
    /* Size in bytes of string table.  */
    int string_size;
    /* Pointer to the string table.
       The string table is not kept in core all the time,
       but when it is in core, its address is here.  */
    char *strings;

    /* Relocation information of the file. */

    /* Start of this file's text relocation information. */
    struct dld_reloc_info *text_reloc;
    /* Start of this file's data relocation information. */
    struct dld_reloc_info *data_reloc;
    
    /* Relation of this file's segments to the output buffer */

    /* Start of this file's text seg in the output file core image.  */
    int text_start_address;
    /* Start of this file's data seg in the output file core image.  */
    int data_start_address;
    /* Start of this file's bss seg in the output file core image.  */
    int bss_start_address;

    /* For library members only */

    /* For a library, points to chain of entries for the library members.  */
    struct file_entry *subfiles;
    /* For a library member, offset of the member within the archive.
       Zero for files that are not library members.  */
    int starting_offset;
    /* Size of contents of this file, if library member.  */
    int total_size;
    /* For library member, points to the library's own entry.  */
    struct file_entry *superfile;

    /* 1 if file is a library. */
    char library_flag;

    /* 1 if file's header has been read into this structure.  */
    char header_read_flag;

    /* 1 if this module has all external references resolved */
    char all_symbols_resolved_flag;
  
    /* 1 if functions in this module can be safely executed. */
    char executable_flag;

    /* 1 if this module has already been (soft) unlinked. */
    char already_unlink;
    /* 1 means search a set of directories for this file.  */
    /* char search_dirs_flag; */
};


/* format of file_entry chain */
struct file_chain {
    struct file_chain *next;
    struct file_entry *entry;
};

/* Symbol table */

/* Global symbol data is recorded in these structures,
   one for each global symbol.
   They are found via hashing in 'symtab', which points to a vector of buckets.
   Each bucket is a chain of these structures through the link field.  */

typedef
  struct glosym
    {
      /* Pointer to next symbol in this symbol's hash bucket.  */
      struct glosym *link;
      /* Name of this symbol.  */
      char *name;
      /* Value of this symbol as a global symbol.  */
      long value;
      /* Points to the file_entry that defines this symbol */
      struct file_entry *defined_by;
      /* chain of file_entry that contains reference to this symbol */
      struct file_chain *referenced_by;
      /* Nonzero means a definition of this global symbol is known to exist.
	 Library members should not be loaded on its account.  */
      char defined;
      /* Nonzero means a reference to this global symbol has been seen
	 in a file that is surely being loaded. */
      char referenced;
    }
  symbol;

/* Number of buckets in symbol hash table */
#define	TABSIZE	1009

/* this is commonly used in removing single linked-list elements. */
#define del_link_list_elt(head, prev, current, next) { \
    if (prev == 0) { \
	head = current->next; \
	free (current); \
	current = head; \
    } else { \
	prev->next = current->next; \
	free (current); \
	current = prev->next; \
    } }

/* The symbol hash table: a vector of TABSIZE pointers to struct glosym. */
extern symbol *_dld_symtab[TABSIZE];

/* variable for saving the environment */
extern jmp_buf _dld_env;

/* pointer to the lastest (newest) file entry */
extern struct file_entry *_dld_latest_entry;

/* dummy file_entry to hold all "dangling" symbols. */
extern struct file_entry *_dld_dummy_entry;

/* true if the executable flags are up-to-date */
extern char _dld_exec_flags_valid;

extern int _dld_malloc ();
extern symbol *_dld_getsym ();
extern symbol *_dld_getsym_soft ();
extern void _dld_enter_global_ref ();
extern void _dld_unlink_entry ();
extern void _dld_create_dummy_entry ();
extern void _dld_patch_all_files ();

