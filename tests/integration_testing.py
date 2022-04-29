#!/bin/python

from pathlib import Path
import subprocess
import json

# TODO during testing allow for a dialog for updating the tests

class TestList(list):
        ''' a test is a dictionary with three keys:
        command         the command to execute in the shell
        result          the expected result
        description     synopsis of command '''
        shell = '/bin/fish'

        def __init__(self):
                self.tests_path = Path.cwd() / 'tests.json'
                if not self.tests_path.exists():
                        self.tests_path.touch()
                        self.tests_path.write_text('[]')
                tests = json.loads(self.tests_path.read_text())
                self[:] = tests

        def save(self):
                self.tests_path.write_text(json.dumps(self))

        def add_test(self, test):
                self.append(test)
                self.save()

        def remove_test(self, idx):
                del self[idx]
                self.save()
        
        def build_test(self):
                print('run any command to create a test')
                cmd = input(f'$ ')
                try:
                        s = subprocess.run(cmd, shell=True, check = True, capture_output=True, executable = self.shell)
                except subprocess.CalledProcessError as e:
                        print(e)
                        s = subprocess.run(cmd, shell=True, capture_output=True, executable = self.shell)
                        print(s.stderr.decode('utf-8'))
                        return
                result = s.stdout.decode('utf-8')
                print(result)
                confirm = input('create test y/n?')
                if confirm != 'y':
                        return
                description = input('description: ')
                new_test = {'command': cmd,
                            'result': result,
                            'description': description}
                self.add_test(new_test)

        def run_test(self, test):
                # the shell argument means that the shell
                # processes and executes the command
                try:
                        s = subprocess.run(test['command'], shell = True, capture_output = True, check = True, executable = self.shell)
                        ret = s.stdout.decode('utf-8')
                except subprocess.CalledProcessError as e:
                        return (False, str(e))
                if ret == test['result']:
                        return (True, ret)
                else:
                        return (False, ret)
                
        def run_tests(self, review=False):
                fail_count = 0
                for test in self:
                        success, ret = self.run_test(test)
                        if not success:
                                fail_count += 1
                                print(test['description'])
                                print('WANTED', test['result'].strip(), sep='\n')
                                print('GOT', ret.strip(), sep='\n', end='\n\n')
                                if review:
                                        if input('update test y/n? ') == 'y':
                                                test['result'] = ret
                                                self.save()
                                        elif input('delete test y/n? ') == 'y':
                                                del test
                                                self.save()
                                
                num_tests = len(self)
                print(num_tests - fail_count, 'passed')
                print(fail_count, 'failed')     
                
test_list = TestList()

if __name__ == '__main__':
        import fire
        fire.Fire(test_list)
