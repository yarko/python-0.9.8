/***********************************************************
Copyright 1991, 1992 by Stichting Mathematisch Centrum, Amsterdam, The
Netherlands.

                        All Rights Reserved

Permission to use, copy, modify, and distribute this software and its 
documentation for any purpose and without fee is hereby granted, 
provided that the above copyright notice appear in all copies and that
both that copyright notice and this permission notice appear in 
supporting documentation, and that the names of Stichting Mathematisch
Centrum or CWI not be used in advertising or publicity pertaining to
distribution of the software without specific, written prior permission.

STICHTING MATHEMATISCH CENTRUM DISCLAIMS ALL WARRANTIES WITH REGARD TO
THIS SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS, IN NO EVENT SHALL STICHTING MATHEMATISCH CENTRUM BE LIABLE
FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT
OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

******************************************************************/

/* Dictionary object implementation; using a hash table */

/*
XXX Note -- although this may look professional, I didn't think very hard
about the problem and it is possible that obvious improvements exist.
A similar module that I saw by Chris Torek:
- uses chaining instead of hashed linear probing
- remembers the hash value with the entry to speed up table resizing
- sets the table size to a power of 2
- uses a different hash function:
	h = 0; p = str; while (*p) h = (h<<5) - h + *p++;
*/

#include "allobjects.h"
#include "modsupport.h"


/*
Table of primes suitable as keys, in ascending order.
The first line are the largest primes less than some powers of two,
the second line is the largest prime less than 6000,
and the third line is a selection from Knuth, Vol. 3, Sec. 6.1, Table 1.
The final value is a sentinel and should cause the memory allocation
of that many entries to fail (if none of the earlier values cause such
failure already).
*/
static unsigned int primes[] = {
	3, 7, 13, 31, 61, 127, 251, 509, 1021, 2017, 4093,
	5987,
	9551, 15683, 19609, 31397,
	0xffffffff /* All bits set -- truncation OK */
};

/* String used as dummy key to fill deleted entries */
static stringobject *dummy; /* Initialized by first call to newdictobject() */

/*
Invariant for entries: when in use, de_value is not NULL and de_key is
not NULL and not dummy; when not in use, de_value is NULL and de_key
is either NULL or dummy.  A dummy key value cannot be replaced by NULL,
since otherwise other keys may be lost.
*/
typedef struct {
	stringobject *de_key;
	object *de_value;
} dictentry;

/*
To ensure the lookup algorithm terminates, the table size must be a
prime number and there must be at least one NULL key in the table.
The value di_fill is the number of non-NULL keys; di_used is the number
of non-NULL, non-dummy keys.
To avoid slowing down lookups on a near-full table, we resize the table
when it is more than half filled.
*/
typedef struct {
	OB_HEAD
	int di_fill;
	int di_used;
	int di_size;
	dictentry *di_table;
} dictobject;

object *
newdictobject()
{
	register dictobject *dp;
	if (dummy == NULL) { /* Auto-initialize dummy */
		dummy = (stringobject *) newstringobject("<dummy key>");
		if (dummy == NULL)
			return NULL;
	}
	dp = NEWOBJ(dictobject, &Dicttype);
	if (dp == NULL)
		return NULL;
	dp->di_size = primes[0];
	dp->di_table = (dictentry *) calloc(sizeof(dictentry), dp->di_size);
	if (dp->di_table == NULL) {
		DEL(dp);
		return err_nomem();
	}
	dp->di_fill = 0;
	dp->di_used = 0;
	return (object *)dp;
}

/*
The basic lookup function used by all operations.
This is essentially Algorithm D from Knuth Vol. 3, Sec. 6.4.
Open addressing is preferred over chaining since the link overhead for
chaining would be substantial (100% with typical malloc overhead).

First a 32-bit hash value, 'sum', is computed from the key string.
The first character is added an extra time shifted by 8 to avoid hashing
single-character keys (often heavily used variables) too close together.
All arithmetic on sum should ignore overflow.

The initial probe index is then computed as sum mod the table size.
Subsequent probe indices are incr apart (mod table size), where incr
is also derived from sum, with the additional requirement that it is
relative prime to the table size (i.e., 1 <= incr < size, since the size
is a prime number).  My choice for incr is somewhat arbitrary.
*/
static dictentry *lookdict PROTO((dictobject *, char *));
static dictentry *
lookdict(dp, key)
	register dictobject *dp;
	char *key;
{
	register int i, incr;
	register dictentry *freeslot = NULL;
	register unsigned char *p = (unsigned char *) key;
	register unsigned long sum = *p << 7;
	while (*p != '\0')
		sum = sum + sum + *p++;
	i = sum % dp->di_size;
	do {
		sum = sum + sum + 1;
		incr = sum % dp->di_size;
	} while (incr == 0);
	for (;;) {
		register dictentry *ep = &dp->di_table[i];
		register char *s;
		if (ep->de_key == NULL) {
			if (freeslot != NULL)
				return freeslot;
			else
				return ep;
		}
		if (ep->de_key == dummy) {
			if (freeslot != NULL)
				freeslot = ep;
		}
		/* Optimized version of "if (strcmp(s, key) == 0)": */
		else if ((s = GETSTRINGVALUE(ep->de_key))[0] == key[0] &&
			(s[0] == '\0' ||
				s[1] == key[1] &&
				(s[1] == '\0' || strcmp(s+2, key+2) == 0))) {
			return ep;
		}
		i = (i + incr) % dp->di_size;
	}
}

/*
Internal routine to insert a new item into the table.
Used both by the internal resize routine and by the public insert routine.
Eats a reference to key and one to value.
*/
static void insertdict PROTO((dictobject *, stringobject *, object *));
static void
insertdict(dp, key, value)
	register dictobject *dp;
	stringobject *key;
	object *value;
{
	register dictentry *ep;
	ep = lookdict(dp, GETSTRINGVALUE(key));
	if (ep->de_value != NULL) {
		DECREF(ep->de_value);
		DECREF(key);
	}
	else {
		if (ep->de_key == NULL)
			dp->di_fill++;
		else
			DECREF(ep->de_key);
		ep->de_key = key;
		dp->di_used++;
	}
	ep->de_value = value;
}

/*
Restructure the table by allocating a new table and reinserting all
items again.  When entries have been deleted, the new table may
actually be smaller than the old one.
*/
static int dictresize PROTO((dictobject *));
static int
dictresize(dp)
	dictobject *dp;
{
	register int oldsize = dp->di_size;
	register int newsize;
	register dictentry *oldtable = dp->di_table;
	register dictentry *newtable;
	register dictentry *ep;
	register int i;
	newsize = dp->di_size;
	for (i = 0; ; i++) {
		if (primes[i] > dp->di_used*2) {
			newsize = primes[i];
			break;
		}
	}
	newtable = (dictentry *) calloc(sizeof(dictentry), newsize);
	if (newtable == NULL) {
		err_nomem();
		return -1;
	}
	dp->di_size = newsize;
	dp->di_table = newtable;
	dp->di_fill = 0;
	dp->di_used = 0;
	for (i = 0, ep = oldtable; i < oldsize; i++, ep++) {
		if (ep->de_value != NULL)
			insertdict(dp, ep->de_key, ep->de_value);
		else {
			XDECREF(ep->de_key);
		}
	}
	DEL(oldtable);
	return 0;
}

object *
dictlookup(op, key)
	object *op;
	char *key;
{
	if (!is_dictobject(op))
		fatal("dictlookup on non-dictionary");
	return lookdict((dictobject *)op, key) -> de_value;
}

object *
dict2lookup(op, key)
	register object *op;
	register object *key;
{
	register object *res;
	if (!is_dictobject(op)) {
		err_badcall();
		return NULL;
	}
	if (!is_stringobject(key)) {
		err_badarg();
		return NULL;
	}
	res = lookdict((dictobject *)op, GETSTRINGVALUE((stringobject *)key))
								-> de_value;
	if (res == NULL)
		err_setstr(KeyError, GETSTRINGVALUE((stringobject *)key));
	return res;
}

int
dict2insert(op, key, value)
	register object *op;
	object *key;
	object *value;
{
	register dictobject *dp;
	register stringobject *keyobj;
	if (!is_dictobject(op)) {
		err_badcall();
		return -1;
	}
	dp = (dictobject *)op;
	if (!is_stringobject(key)) {
		err_badarg();
		return -1;
	}
	keyobj = (stringobject *)key;
	/* if fill >= 2/3 size, resize */
	if (dp->di_fill*3 >= dp->di_size*2) {
		if (dictresize(dp) != 0) {
			if (dp->di_fill+1 > dp->di_size)
				return -1;
		}
	}
	INCREF(keyobj);
	INCREF(value);
	insertdict(dp, keyobj, value);
	return 0;
}

int
dictinsert(op, key, value)
	object *op;
	char *key;
	object *value;
{
	register object *keyobj;
	register int err;
	keyobj = newstringobject(key);
	if (keyobj == NULL)
		return -1;
	err = dict2insert(op, keyobj, value);
	DECREF(keyobj);
	return err;
}

int
dictremove(op, key)
	object *op;
	char *key;
{
	register dictobject *dp;
	register dictentry *ep;
	if (!is_dictobject(op)) {
		err_badcall();
		return -1;
	}
	dp = (dictobject *)op;
	ep = lookdict(dp, key);
	if (ep->de_value == NULL) {
		err_setstr(KeyError, key);
		return -1;
	}
	DECREF(ep->de_key);
	INCREF(dummy);
	ep->de_key = dummy;
	DECREF(ep->de_value);
	ep->de_value = NULL;
	dp->di_used--;
	return 0;
}

int
dict2remove(op, key)
	object *op;
	register object *key;
{
	if (!is_stringobject(key)) {
		err_badarg();
		return -1;
	}
	return dictremove(op, GETSTRINGVALUE((stringobject *)key));
}

int
getdictsize(op)
	register object *op;
{
	if (!is_dictobject(op)) {
		err_badcall();
		return -1;
	}
	return ((dictobject *)op) -> di_size;
}

object *
getdict2key(op, i)
	object *op;
	register int i;
{
	/* XXX This can't return errors since its callers assume
	   that NULL means there was no key at that point */
	register dictobject *dp;
	if (!is_dictobject(op)) {
		/* err_badcall(); */
		return NULL;
	}
	dp = (dictobject *)op;
	if (i < 0 || i >= dp->di_size) {
		/* err_badarg(); */
		return NULL;
	}
	if (dp->di_table[i].de_value == NULL) {
		/* Not an error! */
		return NULL;
	}
	return (object *) dp->di_table[i].de_key;
}

char *
getdictkey(op, i)
	object *op;
	int i;
{
	register object *keyobj = getdict2key(op, i);
	if (keyobj == NULL)
		return NULL;
	return GETSTRINGVALUE((stringobject *)keyobj);
}

/* Methods */

static void
dict_dealloc(dp)
	register dictobject *dp;
{
	register int i;
	register dictentry *ep;
	for (i = 0, ep = dp->di_table; i < dp->di_size; i++, ep++) {
		if (ep->de_key != NULL)
			DECREF(ep->de_key);
		if (ep->de_value != NULL)
			DECREF(ep->de_value);
	}
	if (dp->di_table != NULL)
		DEL(dp->di_table);
	DEL(dp);
}

static int
dict_print(dp, fp, flags)
	register dictobject *dp;
	register FILE *fp;
	register int flags;
{
	register int i;
	register int any;
	register dictentry *ep;
	fprintf(fp, "{");
	any = 0;
	for (i = 0, ep = dp->di_table; i < dp->di_size; i++, ep++) {
		if (ep->de_value != NULL) {
			if (any++ > 0)
				fprintf(fp, ", ");
			if (printobject((object *)ep->de_key, fp, flags) != 0)
				return -1;
			fprintf(fp, ": ");
			if (printobject(ep->de_value, fp, flags) != 0)
				return -1;
		}
	}
	fprintf(fp, "}");
	return 0;
}

static void
js(pv, w)
	object **pv;
	object *w;
{
	joinstring(pv, w);
	XDECREF(w);
}

static object *
dict_repr(dp)
	dictobject *dp;
{
	auto object *v;
	object *sepa, *colon;
	register int i;
	register int any;
	register dictentry *ep;
	v = newstringobject("{");
	sepa = newstringobject(", ");
	colon = newstringobject(": ");
	any = 0;
	for (i = 0, ep = dp->di_table; i < dp->di_size; i++, ep++) {
		if (ep->de_value != NULL) {
			if (any++)
				joinstring(&v, sepa);
			js(&v, reprobject((object *)ep->de_key));
			joinstring(&v, colon);
			js(&v, reprobject(ep->de_value));
		}
	}
	js(&v, newstringobject("}"));
	XDECREF(sepa);
	XDECREF(colon);
	return v;
}

static int
dict_length(dp)
	dictobject *dp;
{
	return dp->di_used;
}

static object *
dict_subscript(dp, key)
	dictobject *dp;
	register object *key;
{
	object *v;
	if (!is_stringobject(key)) {
		err_badarg();
		return NULL;
	}
	v = lookdict(dp, GETSTRINGVALUE((stringobject *)key)) -> de_value;
	if (v == NULL)
		err_setstr(KeyError, GETSTRINGVALUE((stringobject *)key));
	else
		INCREF(v);
	return v;
}

static int
dict_ass_sub(dp, v, w)
	dictobject *dp;
	object *v, *w;
{
	if (w == NULL)
		return dict2remove((object *)dp, v);
	else
		return dict2insert((object *)dp, v, w);
}

static mapping_methods dict_as_mapping = {
	dict_length,	/*mp_length*/
	dict_subscript,	/*mp_subscript*/
	dict_ass_sub,	/*mp_ass_subscript*/
};

static object *
dict_keys(dp, args)
	register dictobject *dp;
	object *args;
{
	register object *v;
	register int i, j;
	if (!getnoarg(args))
		return NULL;
	v = newlistobject(dp->di_used);
	if (v == NULL)
		return NULL;
	for (i = 0, j = 0; i < dp->di_size; i++) {
		if (dp->di_table[i].de_value != NULL) {
			stringobject *key = dp->di_table[i].de_key;
			INCREF(key);
			setlistitem(v, j, (object *)key);
			j++;
		}
	}
	return v;
}

object *
getdictkeys(dp)
	object *dp;
{
	if (dp == NULL || !is_dictobject(dp)) {
		err_badcall();
		return NULL;
	}
	return dict_keys((dictobject *)dp, (object *)NULL);
}

static int
dict_compare(a, b)
	dictobject *a, *b;
{
	object *akeys, *bkeys;
	int i, n, res;
	if (a == b)
		return 0;
	if (a->di_used == 0) {
		if (b->di_used != 0)
			return -1;
		else
			return 0;
	}
	else {
		if (b->di_used == 0)
			return 1;
	}
	akeys = dict_keys(a, (object *)NULL);
	bkeys = dict_keys(b, (object *)NULL);
	if (akeys == NULL || bkeys == NULL) {
		/* Oops, out of memory -- what to do? */
		/* For now, sort on address! */
		XDECREF(akeys);
		XDECREF(bkeys);
		if (a < b)
			return -1;
		else
			return 1;
	}
	sortlist(akeys);
	sortlist(bkeys);
	n = a->di_used < b->di_used ? a->di_used : b->di_used; /* smallest */
	res = 0;
	for (i = 0; i < n; i++) {
		object *akey, *bkey, *aval, *bval;
		akey = getlistitem(akeys, i);
		bkey = getlistitem(bkeys, i);
		res = cmpobject(akey, bkey);
		if (res != 0)
			break;
		aval = lookdict(a, GETSTRINGVALUE((stringobject *)akey))
								-> de_value;
		bval = lookdict(b, GETSTRINGVALUE((stringobject *)bkey))
								-> de_value;
		res = cmpobject(aval, bval);
		if (res != 0)
			break;
	}
	if (res == 0) {
		if (a->di_used < b->di_used)
			res = -1;
		else if (a->di_used > b->di_used)
			res = 1;
	}
	DECREF(akeys);
	DECREF(bkeys);
	return res;
}

static object *
dict_has_key(dp, args)
	register dictobject *dp;
	object *args;
{
	char *key;
	register long ok;
	if (!getstrarg(args, &key))
		return NULL;
	ok = lookdict(dp, key)->de_value != NULL;
	return newintobject(ok);
}

static struct methodlist dict_methods[] = {
	{"keys",	dict_keys},
	{"has_key",	dict_has_key},
	{NULL,		NULL}		/* sentinel */
};

static object *
dict_getattr(dp, name)
	dictobject *dp;
	char *name;
{
	return findmethod(dict_methods, (object *)dp, name);
}

typeobject Dicttype = {
	OB_HEAD_INIT(&Typetype)
	0,
	"dictionary",
	sizeof(dictobject),
	0,
	dict_dealloc,	/*tp_dealloc*/
	dict_print,	/*tp_print*/
	dict_getattr,	/*tp_getattr*/
	0,		/*tp_setattr*/
	dict_compare,	/*tp_compare*/
	dict_repr,	/*tp_repr*/
	0,		/*tp_as_number*/
	0,		/*tp_as_sequence*/
	&dict_as_mapping,	/*tp_as_mapping*/
};
