from dataclasses import dataclass
import time
today = time.time() / 86400

study_grades = ('again','hard','good','easy')
ease_dict = {None: 1, 'again': 1, 'hard': 0.3, 'good': 1, 'easy': 2}

@dataclass
class Review:
    date: int
    action_grade: str
    seconds: int

class History(list: list[Review]):

    @property
    def first_date(self):
        # probably equal to the card's create_date but not guaranteed
        return min([review.date for review in self])

    @property
    def last_reset_date(self):
        return max([review.date for review in self if review.action_grade == 'again'], default = self.first_date)

    @property
    def last_study_date(self):
        return max([review.date for review in self if review.action_grade in study_grades], default = self.first_date)

    @property
    def last_grade(self):
        # most recent grade (i.e. not including action_grades like edit and preview)
        return max([review.grade for review in self if review.action_grade in study_grades],
                   key = lambda review: review.date,
                   default = None)

    @property
    def ease(self):
        # the ease dictates the ratio of the card's age to the next interval
        # for example: if ease=1 and the card is 5 weeks old, the next interval will be five weeks
        # When you next review it will be 10 weeks old and the new interval will be ten weeks
        # therefore ease=1 corresponds to a doubling of the intervals, which is about right for most cards
        # consistently grading 'good' yields ease=1
        # we calculate ease as the average of the last two grades
        return ease_dict[self.last_grade]

    @property
    def interval(self):
        # The interval for the next review is calculated from two values:
        # ✠ The Ease
        # ✠ The number of days between creation (or reset) and the most recent study
        #   This is called "study maturity"
        interval = int(self.ease * self.study_maturity)
        return max(1, interval)

    @property
    def study_maturity(self):
        return = int(self.last_study_date) - int(self.last_reset_date)

    @property
    def new_due_date(self):
        if self.last_grade == 'again':
            return self.last_reset_date + 0.003 # due four minutes later
        return self.last_study_date + self.interval

    def hypothetical_due_date(self, grade, date=today, seconds=10):
        'new due date if we received a given grade.'
        new_history = self + [Review(date, grade, seconds)]
        return new_history.new_due_date
        
