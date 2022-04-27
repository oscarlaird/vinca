'''
contains the VimEditor class and instantiates a single instance of it.
by using the same instance we can preserve yank and line_history for
the duration of the vinca_session.

'''
import re
import string
from math import ceil

from vinca._lib import ansi
from vinca._lib import terminal
from vinca._lib.readkey import readkey, keys
from vinca._lib.vinput.digraphs import digraphs

# TODO dff cft &c. 
# TODO dot repeat
# TODO dot repeat insertions like cwnewtext
class VimEditor:
        # mutable variables like line_history and yank_history
        # will be shared across all instances of the class
        line_history = []
        yank_history = ['']

        green, red = ansi.codes['green'], ansi.codes['red']
        reset = ansi.codes['reset']
        mode_prompt_dict = {
        'normal':                     f'{red}[N]{reset} ',
        'insert':                     f'{green}[I]{reset} '}
        prompt_length = 4
        MODES = ('normal','insert')
        INSERT_SUBMODES = ('none', 'replace', 'tab_completing', 'digraph_pending')
        NORMAL_SUBMODES = ('none', 'motion_pending', 'search_char_pending', 'replace_char_pending')
        SUBMODES = INSERT_SUBMODES + NORMAL_SUBMODES

        OPERATORS = 'dcy~'
        MOTIONS = 'webftFT;,hl()0$_^'
        ACTIONS = 'sSru.xXDCpPYaiAIjk'
        DIGITS = '123456789'

        BOW = re.compile(       # BEGINNING OF WORD
                '((?<=\s)|^)'   # pattern is preceded by whitespace or BOL
                '\w')           # beginning of word is any alphanumeric.
        EOW = re.compile(       # END OF WORD
                '\w'            # any alphanumeric character
                '(\s|$)')       # succeeded by whitespace or EOL
        EOS = re.compile('[.!?]')  # EDGE OF SENTENCE

        @property
        def yank(self):
                return self.yank_history[-1]


        def __init__(self, text='', mode='default', prompt = '', completions = None):
                self.text = text if text is not None else ''
                self.mode = mode
                self.submode = 'none'
                if mode=='default':
                        if self.text:
                                self.mode = 'normal'
                        elif not self.text:
                                self.mode = 'insert'
                self.prompt = prompt
                self.completions = completions if completions else []

                self.pos = 0
                self.completing = False

                self.multiplier = 1
                self.undo_stack = []
                self.redo_stack = []
                self.operator = None
                # store previous keypresses to redo actions with .
                self.current_insertion = ''
                self.prev_multiplier = 1
                self.prev_insertion = ''
                self.prev_action = None
                self.prev_operator = None
                self.prev_motion = None
                self.thing_to_repeat = 'none'
                # use up and down arrows to scroll through previous entries
                self.line_history_idx = 0  
                # character jumping (using f and t)
                self.search_char = ''
                self.char_jumper = None
                # delimit the range of motion for an operation
                self.start = None  
                self.end = None
                # misc.
                self.digraph = ''

        def process_key(self, key):
                assert self.mode in self.MODES and self.submode in self.SUBMODES, f'bad mode {self.mode} and sub {self.submode}'
                if self.mode == 'insert':
                        self.do_insert(key)
                elif self.mode == 'normal':
                        if self.submode == 'none':
                                self.process_key_normal_mode(key)
                        elif self.submode == 'motion_pending':
                                self.process_key_motion_pending_mode(key)
                        elif self.submode == 'search_char_pending':
                                self.process_key_search_char_pending_mode(key)
                        elif self.submode == 'replace_char_pending':
                                self.process_key_replace_char_pending_mode(key)

        def process_keys(self, keys, debug_id = 0):
                self.debug_id = debug_id
                for key in keys:
                        self.process_key(key)

        def process_key_search_char_pending_mode(self, key):
                assert self.char_jumper in ('f','F','t','T')
                sc = self.search_char = key
		# if the search character is a regex symbol itself
		# se need to escape it
                if sc in '()[].?':
                        sc = '\\' + sc
                self.pos = {'f': self.idx(sc),
                            'F': self.idx(sc, back = True),
                            't': self.idx(f'.(?={sc})'),
                            'T': self.idx(f'(?<={sc}).', back = True),
                           }[self.char_jumper]
                self.submode = 'none'

        def process_key_replace_char_pending_mode(self, key):
                before = self.text[:self.pos]
                after  = self.text[self.pos+1:]
                self.text = before + key + after
                self.submode = 'none'
                self.save_state()

        def process_key_motion_pending_mode(self, key):
                assert self.submode == 'motion_pending'
                assert self.operator
                # multiplier
                if key in self.DIGITS:
                        self.multiplier = int(key)
                        return
                # determine [start:end] range for the multiplier
                if key == self.operator:
                        # allow for a doubled operator to act on the line
                        # e.g. dd or yy is shorthand for
                        # 0d$ and 0y$
                        self.start = 0
                        self.end = len(self.text) - 1
                elif key in self.MOTIONS:
                        self.start = self.pos
                        for _ in range(self.multiplier):
                                self.do_motion(key)
                        self.reset_multiplier()
                        self.end = self.pos
                        self.pos = self.start
                else:
                        return  # invalid motion
                self.do_operation()
                self.thing_to_repeat = 'operation'
                if self.submode == 'motion_pending':
                        self.submode = 'none'
                if self.mode != 'insert':
                        # save state after performing an operation
                        # except if in insert mode,
                        # because we will save the state after
                        # performing the insertion.
                        self.save_state()

        def process_key_normal_mode(self, key):
                assert self.mode == 'normal'
                if key in self.DIGITS:
                        self.multiplier = int(key)
                elif key in self.ACTIONS:
                        for _ in range(self.multiplier):
                                self.do_action(key)
                        self.reset_multiplier()
                        self.thing_to_repeat = 'action'
                        if self.mode != 'insert' and key != 'u':
                                # save state after performing an action
                                # except if in insert mode,
                                # because we will save the state after
                                # performing the insertion.
                                self.save_state()
                elif key in self.OPERATORS:
                        self.submode = 'motion_pending'
                        self.operator = key
                elif key in self.MOTIONS:
                        for _ in range(self.multiplier):
                                self.do_motion(key)
                        self.reset_multiplier()

        def reset_multiplier(self):
                self.prev_multiplier = self.multiplier
                self.multiplier = 1

        def idx(self, pattern, back = False):
                '''Return the index of the next match of the pattern in the text.
                If we find no match we return the current pos.'''
                # list of matching indicies
                indices = [m.start() for m in re.finditer(pattern, self.text)] 
                if not back:
                        return min([i for i in indices if i > self.pos],
                                default = self.pos)
                if back:
                        return max([i for i in indices if i < self.pos],
                                default = self.pos)

        def save_state(self):
                self.undo_stack.append({'text':self.text,'pos':self.pos})

        @property
        def current_char(self):
                if not self.text:
                        return None
                if self.mode == 'normal':
                        return self.text[self.pos]
                elif self.mode == 'insert':
                        return self.text[self.pos - 1]

        @property
        def prev_char(self):
                if self.pos == 0:
                        return None
                return self.text[self.pos - 1]

        def do_tab_complete(self):
                # we want to tab through various completions
                # get the starting index of the selected word
                if self.current_char not in string.ascii_letters:
                        return
                if self.prev_char and self.prev_char not in string.ascii_letters:
                        BOW_idx = self.pos
                else:
                        BOW_idx = self.idx(self.BOW, back=True)
                        
                # if we are pressing tab for the first time
                # we need to determine the completion stem
                # and make a list of possible completions
                if not self.completing:
                        stem = self.text[BOW_idx:self.pos+1]
                        cc = [stem]
                        cc += [c for c in self.completions if c.startswith(stem)] 
                        self.current_completions = cc
                        self.completing = True
                        self.complete_idx = 0
                # now we do the tab completions
                # go to next match
                self.complete_idx += 1
                # allow for scrolling through from the last match to the first match
                self.complete_idx = self.complete_idx % len(self.current_completions)
                
                before = self.text[:BOW_idx]
                after = self.text[self.pos+1:]
                completion = self.current_completions[self.complete_idx]
                self.text = before + completion + after
                self.pos = BOW_idx + len(completion)

        def do_insert(self, key):
                if self.submode == 'replace':
                        raise NotImplementedError
                if self.submode == 'digraph_pending':
                        self.digraph += key
                        if len(self.digraph) == 2:
                                unicode_digraph = digraphs.get(self.digraph, '?')
                                self.text = self.text[:self.pos] + unicode_digraph + self.text[self.pos:]
                                self.current_insertion += unicode_digraph
                                self.pos += 1
                                # clean-up
                                self.submode = 'none'
                                self.digraph = ''
                        return

                if key == keys.CTRL_K:
                        self.submode = 'digraph_pending'
                        return

                if key == keys.ESC:
                        self.prev_insertion = self.current_insertion
                        self.save_state()
                        self.current_insertion = ''
                        self.mode = 'normal'
                        self.pos -= 1
                        self.bring_position_into_text()
                        return
                if key == '\t' and self.completions:
                        self.do_tab_complete()
                        return
                else:
                        self.completing = False
                if key == '\x1b\t':
                        key = '\t'
                if key == '\x1b\r':
                        key = '\n'
                if key in (keys.LEFT, keys.RIGHT):
                        if key == keys.LEFT:
                                self.pos -= 1
                        elif key == keys.RIGHT:
                                self.pos += 1
                        self.bring_position_into_text()
                        self.current_insertion = ''
                elif key == keys.BACK and self.pos > 0:
                        self.text = self.text[:self.pos - 1] + self.text[self.pos:]
                        self.pos -= 1
                        self.current_insertion = ''
                elif key in string.printable:
                        self.text = self.text[:self.pos] + key + self.text[self.pos:]
                        self.current_insertion += key
                        self.pos += 1

        def bring_position_into_text(self):
                min_pos = 0
                max_pos = len(self.text) - 1 if self.text else 0
                if self.pos < min_pos:
                        self.pos = min_pos
                elif self.pos > max_pos:
                        self.pos = max_pos

        def do_operation(self):
                self.start, self.end = min(self.start, self.end), max(self.start, self.end)
                key = self.operator
                if key == 'd':
                        self.text = self.text[:self.start] + self.text[self.end+1:]
                        self.bring_position_into_text()
                if key == 'c':
                        self.text = self.text[:self.start] + self.text[self.end+1:]
                        self.mode = 'insert' ; self.submode = 'none'
                if key == 'y':
                        self.yank_history.append(self.text[self.start:self.end+1])
                if key == '~':
                        self.text = self.text[:self.start] + \
                                self.text[self.start:self.end+1].swapcase() + \
                                self.text[self.end+1:]
                self.prev_operator = key

        def w_motion(self):
                assert self.mode == 'normal'
                if self.submode == 'none':
                        return self.idx(self.BOW)
                elif self.submode == 'motion_pending':
                        if self.operator in 'c~y':
                                return self.idx(self.EOW)
                        elif self.operator == 'd':
                                # dw should delete up through the
                                # beginning of the next word ( \w)
                                # or all the way thru to the end of the line
                                pat = re.compile('(( \w)|$)')
                                return self.idx(pat)

        def do_motion(self, key):
                # jump to character
                if key in ('f','F','t','T'):
                        self.char_jumper = key
                        self.submode = 'search_char_pending'
                        return
                # other motions
                self.pos = {
                        # jump by word
                        'w': self.w_motion,
                        'e': lambda: self.idx(self.EOW),
                        'b': lambda: self.idx(self.BOW, back = True),
                        # repeat character jumps
                        ';': lambda: self.idx(self.search_char),
                        ',': lambda: self.idx(self.search_char, back = True),
                        # left / right navigation
                        'h':       lambda: max(0, self.pos-1),
                        'l': lambda: min(len(self.text)-1, self.pos+1),
                        # sentence jumping
                        ')': lambda: self.idx(self.EOS),
                        '(': lambda: self.idx(self.EOS, back = True),
                        # jump to beginning or end of line
                        '0': lambda: 0,
                        '^': lambda: 0,
                        '_': lambda: 0,
                        '$': lambda: len(self.text)
                        }[key]()
                self.prev_motion = key

        def do_action(self, key): 
                k = key
                # substitution
                if k == 'C':
                        self.process_keys('c$')
                if k in ('s','S'):
                        self.mode = 'insert'; self.submode = 'none'
                        if key == 'S':
                                self.text = ''
                        if key == 's':
                                self.text = self.text[:self.pos] + self.text[self.pos+1:]
                if k == 'r':
                        self.submode = 'replace_char_pending'
                # reversion and redoing
                if k == 'u' and self.undo_stack:
                        # save current state
                        current_state = self.undo_stack.pop()
                        self.redo_stack.append(current_state)
                        # retrieve previous state
                        prev_state = self.undo_stack[-1]
                        self.text, self.pos = prev_state['text'], prev_state['pos']
                if k == keys.CTRL_R and self.redo_stack:
                        self.undo_stack.append({'text': self.text, 'pos': self.pos})
                        new_state = self.redo_stack.pop()
                        self.text, self.pos = new_state['text'], new_state['pos']
                if k == '.':
                        self.repeat()
                # deletion
                if k == 'D':
                        self.process_keys('d$')
                if k in ('x','X'):
                        self.text = {
                                'x': self.text[:self.pos] + self.text[self.pos+1:],
                                'X': self.text[:self.pos-1] + self.text[self.pos:]}[k]
                        self.pos -= (k == 'X')
                # copy and paste
                if k == 'Y':
                        self.process_keys('y$')
                if k == 'p':
                        self.text = self.text[:self.pos+1] + \
                                    self.yank + self.text[self.pos+1:]
                if k == 'P':
                        self.text = self.text[:self.pos] + \
                                    self.yank + self.text[self.pos:]
                        self.pos += len(self.yank)
                # enter insert mode
                if k in ('i','I','a','A'):
                        self.mode = 'insert' ; self.submode = 'none'
                        self.pos =  {'i': self.pos,
                                'I': 0,
                                'a': self.pos + 1,
                                'A': len(self.text)}[k]
                                
                # history scrolling
                if k in ('j','k',keys.DOWN, keys.UP):
                        max_lhi = 0
                        min_lhi = - len(self.line_history)
                        if k in ('j', keys.DOWN):
                                if self.line_history_idx < max_lhi:
                                        self.line_history_idx += 1
                        if k in ('k', keys.UP):
                                if self.line_history_idx > min_lhi:
                                        self.line_history_idx -= 1
                        lhi = self.line_history_idx
                        if lhi == 0:
                                self.text = ''
                        elif lhi <= -len(self.text):
                                self.text = self.line_history[0]
                        else:
                                self.text = self.line_history[lhi]
                        self.pos = len(self.text) - 1

                self.prev_action = key if key != '.' else self.prev_action

        def repeat(self):
                if self.thing_to_repeat == 'none':
                        return
                if self.thing_to_repeat == 'action':
                        assert self.prev_action
                        for _ in range(self.prev_multiplier):
                                self.do_action(self.prev_action)
                                if self.mode == 'insert':
                                        self.text = self.text[:self.pos] + \
                                                self.prev_insertion + \
                                                self.text[self.pos:]
                                        self.mode == 'normal'
                if self.thing_to_repeat == 'operation':
                        assert self.prev_operator and self.prev_motion
                        for _ in range(self.prev_multiplier):
                                self.do_operation(self.prev_operator)

        def __str__(self):
                mode_prompt = self.mode_prompt_dict[self.mode]
                prefix = mode_prompt + self.prompt
                cursor = ansi.codes['reverse'] + \
                        (self.text[self.pos] if self.pos<len(self.text) else ' ') + \
                        ansi.codes['reset']
                text_with_cursor = self.text[:self.pos] + cursor + self.text[self.pos+1:]
                return prefix + text_with_cursor

        def __repr__(self):
                cursor = '|' if self.mode == 'insert' else '['
                text_with_cursor = self.text[:self.pos] + cursor + self.text[self.pos:]
                return text_with_cursor

        @property
        def screen_lines(self):
                # the prompt has some ANSI Control Codes
                # so use a dummy prompt of the same length
                text = '_' * self.prompt_length + self.text
                screen_lines = 0
                for line in text.splitlines():
                        if not line:
                                screen_lines += 1
                                continue
                        screen_lines += ceil( len(line) / terminal.COLUMNS )
                if text.endswith('\n'):
                        screen_lines += 1
                return screen_lines

        def scrollback(self):
                ansi.up_line(self.screen_lines)
                ansi.clear_to_end()

        def run(self):
                with terminal.NoCursor():
                        while True:
                                print(self)
                                key = readkey()
                                if key in ('\n','\r'):
                                        break
                                self.scrollback() # clear for next iter
                                self.process_key(key)   

                        self.line_history.append(self.text)
                        return self.text

if __name__ == '__main__':
        import doctest
        test_vim = VimEditor(text = 'The quick brown fox jumped over the lazy dog.')
        doctest.testfile('vim_tests.py',
                        optionflags=doctest.REPORT_ONLY_FIRST_FAILURE,
                        globs = {'v': test_vim, 'ESC':keys.ESC, 'BACK':keys.BACK,
                                 'LEFT':keys.LEFT, 'RIGHT':keys.RIGHT})
