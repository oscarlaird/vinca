# commit at the end of every session (if diff says to do so)
# if it has been more than a day fetch to determine what to do next
# handle no internet

from pathlib import Path as _Path
from subprocess import run
import pymysql
import datetime
TODAY = datetime.date.today()
DAY = datetime.datetime(days = 1)

class Dolt_Repo:

    def __init__(self, dolt_repo_path):
            self.path = Path(dolt_repo_path).expanduser()
            assert path.exists()
            self.cursor = self.launch_server()

    def init_dolt_repo(self):
            raise NotImplementedError

    def create_dolt_remote_dolthub(self):
            raise NotImplementedError

    def launch_server(self): 
            # locally run a mysql server
           run(['dolt','sql-server', '--multi-db-dir',self.path.parent])
           cursor = pymysql.connect(host="127.0.0.1",port=3306,user="root",db=self.path.name)
           return cursor

    def commit(self):
            self.cursor.execute('-a','-m','normal study')

    def ancestors_log(self, commit):
            'get all the ancestors of a commit, excluding merged branches'
            # select parent_index=0 excludes merged ancestors
            log = [commit]
            while log[-1] is not None:
                    self.cursor.execute('select parent_hash from dolt_commit_ancestors '
                    'where parent_index = 0 and commit_hash = ?', (log[-1],))
                    parent = self.cursor.fetchone()[0]
                    log.append(parent)
            return log

    def common_ancestor(self, commit_1, commit_2):
            # find the mergebase of two commits
            ancestors_1 = self.ancestors_log(commit_1)
            ancestors_2 = self.ancestors_log(commit_2)
            common_ancestors = [a for a in ancestors_1 if a in ancestors_2]
            assert common_ancestors, f"commits {commit_1} and {commit_2} are not cousins!"
            return common_ancestors[0]

    def fetch_origin(self):
            self.cursor.execute("call dolt_fetch('origin','main')")

    @property
    def head(self):
            self.execute("select hashof('main')")
            return self.cursor.fetchone()[0]

    @property
    def origin_head(self):
            'hash of last origin commit. remember that origin/main needs to be fetched first'
            self.execute("select hashof('origin/main')")
            return self.cursor.fetchone()[0]

    @property
    def days_since_sync(self):
            return (TODAY - self.last_sync_date) / DAY

    @property
    def days_since_fetch(self):
            return (TODAY - self.commit_date(self.origin_head)) / DAY

    def commit_date(self, commit):
            'return the date of the most recent commit'
            self.cursor.execute('select date from dolt_commits where commit = ?', ?)
            return self.cursor.fetchone()[0]

    @property
    def last_sync_commit(self):
            return self.common_ancestor(self.head, self.origin_head)
            
    @property
    def last_sync_date(self):
            return self.commit_date(self.last_sync_commit)

    @propery
    def synchronized(self):
            ' this requires a fetch '
            self.fetch()
            return self.last_sync_commit == self.head


    def push(self):
            self.cursor.execute('call dolt_push();')

    def merge(self):
            self.cursor.execute('call dolt_merge();')

    def sync(self):
            'shorthand for merge and push'
            self.merge()
            self.push()

    def local_unsynced_steps(self):
            return self.ancestors_log(self.head).index(self.last_sync_commit)

    def origin_unsynced_steps(self):
            return self.ancestors_log(self.origin_head).index(self.last_sync_commit)

    def ask_and_sync(self):
            self.fetch()
            if self.local_unsynced_steps == self.origin_unsynced_steps == 0:
                    print('Synchronized. Everything is up to date.')
                    return
            print f'local machine is ahead by {self.local_unsynced_steps} \n'
                  f'online server is ahead by {self.origin_unsynced_steps}\n'
            permission = input('Would you like to sync? Y/n\n')
            if permission in ('\n','y'):
                    self.sync()
                    assert self.synchronized
                    print('Synchronized. Everything is up to date.')

    def status(self):
            self.fetch()
            if self.local_unsynced_steps == self.origin_unsynced_steps == 0:
                    print('Synchronized. Everything is up to date.')
                    return
            print f'local machine is ahead by {self.local_unsynced_steps} \n'
                  f'online server is ahead by {self.origin_unsynced_steps}\n'
