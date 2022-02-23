Six priorities
--------------
1. Improve Vim-Editor (currently it breaks on 'w')
        - probably everything would be more reliable if we got rid of regex
        - come up with a sane functional approach to structuring motions and operators
        - unit test these functions
2. Make the config a hardcoded config.py which the user can edit. (Skip the json!)
        - edit-config opens vim
        - will not preserve across updates. OK.
3. Make lc a simple alias for `vinca sort seen 0`
4. Print [END] at the end of a verses card.
5. Add git handles directly into vinca.
6. Statistics


Big goals
---------
- Write MIRE (see below)
        - Ask for advice on how to implement this
- Come up with a way of having orthogonal editors and reviewers which is not as hacky.
        - Perhps using abstract classes where we must inherit our methods from editor, reviewer, scheduler.


Low goals
---------
- leaches
- only reschedule a card if it was due
- show a simple table of commands (like graphics magick)
- subscript letters
- transfer my cards from ANKI
- figure out how to smooth out card due dates (maybe unncecessary)
- figure out a philosophy of handling sibling cards.
- special schedulers for quotations, languages, &c.
- intelligent review count forecast
- fire should accept slices and iterables (maybe unnecessary)
- figure out a philosophy of tagging
- record exact time of day, not just date, so as to preserve order


MIRE
----
Research on In-Memory Storage
A simple test shows that for numerical properties the sorting function on the list will be instantaneous.:
Pickling my cardlist of 1700 cards gives 650 B / card which rounded up is a conservative 1kb/card which for a collection of 100,000 cards is only 100mB. (This same estimate is corroborated by pickling individual cards which usually is around 850B per card.)

Notes
Load the module in some daemon python instance
When fire calls vinca it references this module instead of init-ing it all over.
The hard part is that they live in different python instances.
(This would provide an extension whereby I could act on the previous result by default and use col to get back to neutral. I could also write an interactive mode where the prefatory `vinca` is omitted.)
(Whenever cards are created they are added to the cardlist. This is already sort of implemented in the browser.)


Misc. Philosophy 
----------------
2 types of memory in vinca: recall ability; known to exist
Definition of waste: all learning of card order, phrasing, etc.
Defense of the compound question:
- the time to load the subject into memory is non-zero, but of zero value
- a compound question reviews two pieces of material and this loading is only done once.
principle: the questions should be unambiguous for someone who did not create them

The idea of a network of facts
The inner ones are safe (how can I forget that Constantine called the council of Nice if I know it was called in 325 and that he entered it with humilit?)
The outer ones are exposed and must form an adamantine phalanx. (Strong "surface tension"; the surface tension of knowledge)
Vinca protects the frontiers.

idea of polynomial data retrieval: 4 pieces of information are split into 5 cards; I can forget any card and the other 4 can recover it. (This is the generalization of redundancy.)

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

We want greater orthogonality:
i.e. we let a given card use ANY reviewer, or editor
e.g. the vim editor could open 'lines' if it is a verses card
     but otherwise it can open the card's directory in netrw
editors: two_lines, vim
reviewers: terminal, sxiv
schedulers need to be changed manually in metadata
