# Tests for vim_input module
# We use a simple representation of the
# VimEditor which only shows text and pos
# cursor:
## [ represents normal mode
## | represents insert mode
'''
>>> v
[The quick brown fox jumped over the lazy dog.
>>> # MOTION
>>> ## Simple Motions
>>> v.process_keys('$'); v
The quick brown fox jumped over the lazy dog.[
>>> v.process_keys('0'); v
[The quick brown fox jumped over the lazy dog.
>>> v.process_keys('w'); v
The [quick brown fox jumped over the lazy dog.
>>> v.process_keys('2w'); v
The quick brown [fox jumped over the lazy dog.
>>> v.process_keys('b'); v
The quick [brown fox jumped over the lazy dog.
>>> v.process_keys('5b'); v
[The quick brown fox jumped over the lazy dog.
>>> v.process_keys('3e'); v
The quick brow[n fox jumped over the lazy dog.
>>> v.process_keys('2h'); v
The quick br[own fox jumped over the lazy dog.
>>> v.process_keys('4l'); v
The quick brown [fox jumped over the lazy dog.
>>> ## Search Motions
>>> v.process_keys('fj'); v
The quick brown fox [jumped over the lazy dog.
>>> v.process_keys('tz'); v
The quick brown fox jumped over the l[azy dog.
>>> v.process_keys('Tv'); v
The quick brown fox jumped ov[er the lazy dog.
>>> v.process_keys('Ff'); v
The quick brown [fox jumped over the lazy dog.
>>> # ACTIONS
>>> v.process_keys('rb'); v # replace
The quick brown [box jumped over the lazy dog.
>>> v.process_keys('llsok '+ESC); v # sub
The quick brown book[  jumped over the lazy dog.
>>> v.process_keys(ESC + 'x'); v # delete char
The quick brown book[ jumped over the lazy dog.
>>> v.process_keys('5X'); v # backspace
The quick brown[ jumped over the lazy dog.
>>> v.process_keys('u'); v # backspace
The quick brown book[ jumped over the lazy dog.
>>> v.process_keys('2u'); v # backspace
The quick brown [box jumped over the lazy dog.
>>> v.process_keys('Sall new'+ESC); v # substitution
all ne[w
>>> v.process_keys('u'); v # backspace
The quick brown [box jumped over the lazy dog.
>>> v.process_keys('4wD'); v # delete (to end of line)
The quick brown box jumped over the[ 
>>> v.process_keys('2bCinto the crate'+ESC); v # change ( to end )
The quick brown box jumped into the crat[e
>>> v.process_keys('2bY'); v # yank (to end of line)
The quick brown box jumped into [the crate
>>> v.yank
'the crate'
>>> v.process_keys('$p'); v # paste
The quick brown box jumped into the crate[the crate
>>> # INSERTION ACTIONS
>>> # i I a A
>>> v.process_keys('i under'+ESC); v
The quick brown box jumped into the crate unde[rthe crate
>>> v.process_keys('a '+ESC); v
The quick brown box jumped into the crate under[ the crate
>>> v.process_keys('Iprefix '+ESC); v
prefix[ The quick brown box jumped into the crate under the crate
>>> v.process_keys('A suffix'+ESC); v
prefix The quick brown box jumped into the crate under the crate suffi[x
>>> v.line_history = ['Something came before','in line_history']
>>> v.process_keys('2k'); v
Something came befor[e
>>> v.process_keys('j'); v
in line_histor[y
>>> v.process_keys('j'); v
[
>>> v.process_keys('2k'); v
Something came befor[e
>>> # OPERATORS
>>> ## Operations without multipliers
>>> ## Doubled Operators
>>> v.process_keys('~~'); v
sOMETHING CAME BEFOR[E
>>> v.process_keys('~~'); v
Something came befor[e
>>> v.process_keys('yy'); v.yank
'Something came before'
>>> v.process_keys('ccThis is a new sentence'+ESC); v
This is a new sentenc[e
>>> v.process_keys('zz'); v
_____________________[_
>>> v.yank
'This is a new sentence'
>>> v.process_keys('dd'); v
[
>>> ## Standard Operations
>>> v.process_keys('iNew test sentence has six words.'); v
New test sentence has six words.|
>>> v.process_key(ESC)
>>> ### tests of w motion
>>> v.process_keys('0w'); v
New [test sentence has six words.
>>> v.process_keys('d'); v.mode
'motion_pending'
>>> v.process_keys('w'); v
New [sentence has six words.
>>> v.process_keys('frdw'); v
New sentence has six w[o
>>> v.process_keys('u'); v
New [sentence has six words.
>>> v.process_keys('cwinner'); v
New inner| has six words.
>>> v.process_key(ESC)
>>> ### tests of operators with miscellaneous motions
>>> v.process_keys('y0'); v.yank
'New inner'
>>> v.process_keys('~$'); v
New inne[R HAS SIX WORDS.
>>> # TAB COMPLETION
>>> v.process_keys('dd'); v
[
>>> v.completions = ['this', 'that', 'theother']
>>> v.process_keys('ieither\t'); v
either|
>>> v.process_keys(' \t'); v
either |
>>> v.process_keys('t\t'); v
either this|
>>> v.process_keys('\t\t'); v
either theother|
>>> v.process_keys('\t'); v
either t|
