Leaches
- is_leach is a function of the scheduler and the card history

only add to history and reschedule the card if it was due !!
2 types of memory in vinca: recall ability; known to exist
Definition of waste: all learning of card order, phrasing, etc.
undo grade
A new scheduler: never (helpful for making notes)
A new generator: note (just a text file, with the never scheduler and no reviewer because it is never reviewed; or less)
Why make this part of vinca at all? I can search; sort by date; tag; associate
Another scheduler: see it enough to remember it exists (i.e. reminder) (lower mental load)
decks are either saved commands ( I have  to interfere with fire )
or they are just a tag nothing more
I do not yet see why I will need tags but I will leave them in place for now.
cardlist should be a subclass of list
• I can get the documentation purer in manpage and tabcompletions
fire should accept slices for iterables
Defense of the compound question:
- the time to load the subject into memory is non-zero, but of zero value
- a compound question reviews two pieces of material and this loading is only done once.
think about inheritance and making the editor and reviewer abstract classes
principle: the questions should be unambiguous for someone who did not create them
manually transfer cards from anki to vinca
Another tagging idea: allow for hidden words in {} so that tags can be added at the end but left invisible.
card-creation-time statistics
rethink what you want to see and look at usage stats for your commands
 cacheing strategy: use symlinks to the directories themselves
set the card difficulty ( a way to warn that the answer is long )
set the card timer with custom pace for each card in metadata or generated from history
grade without seeing all lines on a verses card


No matter the approach: SQL, json, anything else, 1M cards is too many. Yes, I can use the default "soon" collection which makes use of symlinks, but this is less convenient when I want to find a reference card. It requires caching, which is some amount of code.
My preferred way is to launch a single vinca instance.
E.g. the instance reads from a fifo. Running a vinca command on the command line attaches the vinca instance to the terminal and writes the command and arguments to the fifo. When the vinca instance is done it automatically detaches itself from the terminal.
-- To do this I would need to write my own equivalent of python fire (I do not think this would be that hard.)
-- This would make it easy to implement a vinca 'mode' in which many commands are run consecutively.
-- small: this would make it easy to preserve line_history and yank_history of the custom vim editor.


How to read 1M cards from json in 25s:
Current speed is 10c / 1ms ⇒ 10000c / s
⇒ 100s to read 1M cards
This can be easily multiprocessed. So x4.
Since reading the json files into python objects is the most time consuming part,
I could possibly write a C script which is a "fragile json reader"
making use of the idea that I know exactly where the data I need is ; (what specific bytes)
In fact, I might add create-date and time to metadata and move the history into a separate file.
-- → (This obeys the unix principle of flat, tabular data, the json is then all one line and the history is a tsv).


make filter commands on the cardlist toplevel? (i.e. get rid of filter command)

The idea of a network of facts
The inner ones are safe (how can I forget that Constantine called the council of Nice if I know it was called in 325 and that he entered it with humilit?)
The outer ones are exposed and must form an adamantine phalanx. (Strong "surface tension"; the surface tension of knowledge)
Vinca protects the frontiers.
.

Marks as good and continue; (i.e. alias for hitting the space bar twice)
LARGE
-----
MULTICOLOR STATISTICS
-> like anki, colored squares
-> previous review density
-> cards created over time
-> cards learned over time
3/4 screen is the past 1/4 screen is the future
--I go downward not across
--numbers are given on the right.
--or I do go across and right my numbers downards
solve overgrading issues
---- why? less dead space
time today: 1h
date		creation	review		forecast
<unicode block left side> [number]
...
...
cards / day:  	56		123		150
time / day:
total:
total time:

red and blue should be used in displaying the card itself not just for the cardlist. (this is done by going into the string method of the card and checking if the output is a tty. If it is we wrap the thing in colors.)
A regulate command which would operate on a cardlist and distribute the due dates more evenly with a +-2 day allowance. (Optimized for a minimum of rescheduling.)
Integrate with git enough to allow
- a save command (commit with message 'review cards')
- an upload command (will require authentication password in config probably)
- a switch command (switch to a different deck) (should have tab completion eventually)
- - a switch commadn would require autocomitting first
Do I need to spread sibling cards apart or put them all on the same day?
a generator for code cards with syntax highlightingwith syntax highlighting
different schedulers for different card types e.g. language, medical, software
these previous two and the succeeding are different form anki
a review count prediction which is a little more intelligent
the main thing is its permanence
set a locked hour for card creation and review e.g. 9a - 10a
lists:
5 = 3 + 2
frankly, 2 = 1 + 1
idea of polynomial data retrieval: 4 pieces of information are split into 5 cards; I can forget any card and the other 4 can recover it. (This is the generalization of redundancy.)

Two Ideas (one practical & one not):
practical:
my own fork of fire: "mire"
`mire vinca` launches a background process running python that loads the vinca module
this background process then reads from a fifo and parses these commands exactly as python-fire would
subsequent invocations of `mire vinca filter new count total` etc. simply write to the fifo
and the background process which has already loaded vinca simply reads the commands and processed them like python-fire would


impractical:
intelligence is not in fact but relation
vinca is not for trivia, but hierarchy
therefore extensively label the relations between cards.
Not just tags, but atomic single and double bonds between pairs of cards
superior & inferior cards. in short, a whole web
Perhaps special cards would be 'relation cards' which ask about the connect of a pair of pieces of knowledge.
An interactive traversal program would then allow me to move from card to card and navigate the web interactively.
It would visualize concentric circles of knowledge.
And when you have made 100,000 such cards, traversing this web would be very similar to traversing your own brain.
(it would be useful for any writing too. cards could be rated for many things like their importance, or in this
case for their literary potential.)


Homemade text compression (shorthand). (Perhaps I could develop five easy deterministic rules which I would test against a corpus.)
e.g. a dot might represent the and the initial of a last term could be used to designate that term.

If I keep the independent folder system, some indexing could be done by helper daemons which watch files and then reindex.
Or I could use a function decorator to keep things simple.
Or the card could notify the index when it writes to metadata.
A good rule for deletion: is the card difficult to review.


We want greater orthogonality:
i.e. we let a given card use ANY reviewer, or editor
e.g. the vim editor could open 'lines' if it is a verses card
     but otherwise it can open the card's directory in netrw
editors: two_lines, vim
reviewers: terminal, sxiv
schedulers need to be changed manually in metadata
Go back to oldstyle help screen:
If I run -h or help I am shown a list of the
commands and their descriptions in a simple table.

I will record the exact time of review, not just the day.
This will allow me to dispense with last_card caching
- I can use most recent review time as a stopgap
- Later "mire" will simply cache the last card as a global variable
As for the cards-folder I have a few choices
- vinca reads from a locals cards folder which is actually a symlink
- that we can set.
- or 2: vinca always reads from ~/cards.
- The user can symlink that if they like.

We need subscript letters.

Perhaps it would be convenient to also have a 
n available ref to the most recently created 
card.

Instead of a config (json) file we can do the following:
- obviate need for a "last card"
- Make other variables environment variables:
-- VINCA_CARDS_PATH
-- TERMINAL_BG (perhaps consistent with some other standard.)
- This has the advantage of simplifying the source code
- And allowing for easy extensibility w/o communication of the modules
- It does not allow for setting environment variables however.

The "vinput" module is somewhat fragile and can be improved by tests and perhaps by taking a more functional approach.
I.e.
every motion is a function and can be unit tested.
every operator is a function which takes a motion as a parameter and can be unit tested.
I use a dictionary to connect the key_characters to their associated function. (So d,c,~,y will all have special handling if they want to override the default behaviour of the motion.)
