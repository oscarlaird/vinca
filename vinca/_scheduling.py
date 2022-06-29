import time
from vinca._lib.julianday import today, JulianDate

study_grades = ('again','hard','good','easy')
ease_dict = {None: 1, 'again': 1, 'hard': 0.3, 'good': 1, 'easy': 2}

class Review:

    def __init__(self, date, grade, seconds):
        self.date = JulianDate(date)
        self.grade = grade
        self.seconds = seconds

    def __str__(self):
        return f'{JulianDate(self.date).isoformat:15s}{self.grade:8s}{self.seconds}\n'

class History(list):

    @property
    def time(self):
        return sum([review.seconds for review in self])

    @property
    def human_time(self):
            minutes, seconds = divmod(self.time, 60)
            return f'{minutes} minutes {seconds} seconds'

    @property
    def first_date(self):
        # probably equal to the card's create_date but not guaranteed
        return min([review.date for review in self])

    @property
    def last_reset_date(self):
        return max([review.date for review in self if review.grade == 'again'], default = self.first_date)

    @property
    def last_study(self):
        # most recent study with a grade (i.e. not including grades like edit and preview)
        return max([review for review in self if review.grade in study_grades], key = lambda review: review.date, default = None)
    
    @property
    def last_study_date(self):
        return self.last_study.date if self.last_study else self.first_date

    @property
    def last_grade(self):
        return self.last_study.grade if self.last_study else None

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
        return int(self.last_study_date) - int(self.last_reset_date)

    @property
    def new_due_date(self):
        if self.last_grade == 'again':
            return self.last_reset_date + 0.003 # due four minutes later
        return self.last_study_date + self.interval

    def hypothetical_due_date(self, grade, date=today(), seconds=10, relative_date=False):
        'new due date if we received a given grade.'
        new_history = History(self + [Review(date, grade, seconds)])
        dd = new_history.new_due_date
        if relative_date:
            # useful for telling user how many days until
            # due if they select a given grade
            return JulianDate(dd).relative_date
        return dd

