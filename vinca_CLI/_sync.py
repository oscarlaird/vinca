import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
from pathlib import Path
from tempfile import NamedTemporaryFile
import shutil
import datetime


url = "http://127.0.0.1:8000/"
client_changes_url = url + 'sync/client_changes'
server_changes_url = url + 'sync/server_changes'
test_url = url + 'sync/test'
token_url = url + 'auth/token'

token_file = Path(__file__).parent / 'access_token'
messenger_template = Path(__file__).parent / 'messenger_template.sqlite'

class Sync:
    def __init__(self, cursor):
        self.cursor = cursor

    def test(self):
        response = requests.get(test_url)
        return response.json

    @staticmethod
    def auth_header():
        if not token_file.exists():
            print('You need to login first.')
            exit()
        return {'Authorization':'Bearer '+token_file.read_text()}


    def client_changes(self):
        ''' upload all records with a null timestamp '''
        # 1 copy messenger_template to messenger.name
        # 2 attach messenger db
        # 3 Copy all records with null timestamp to messenger
        # 4 POST
        # 5 receive back a db containing the server timestamps
        # 6 update records with the timestamps received from the server
        with NamedTemporaryFile() as messenger, NamedTemporaryFile() as server_reply:
            # 1 copy messenger_template to messenger.name
            shutil.copy(messenger_template, messenger.name)
            # 2 attach messenger db
            self.cursor.execute(f'ATTACH DATABASE "{messenger.name}" AS messenger')
            # 3 Copy all records with null timestamp to messenger
            rowcount = 0
            for table in ('edits','reviews','media'):
                self.cursor.execute(f'INSERT INTO messenger.{table} SELECT * FROM {table} WHERE server_timestamp IS NULL')
                rowcount += self.cursor.rowcount
                self.cursor.connection.commit()
            # POST
            self.cursor.execute('DETACH DATABASE messenger')
            print(f'uploading {rowcount} records to the server')
            messenger.seek(0)
            content = messenger.read()
            response = requests.post(
                           client_changes_url,
                           headers = self.auth_header(),
                           files = {'file': content},
                        )
            if response.status_code==401:
                print('Access denied. Your token has probably expired. Login again')
                return login()
            # 5 receive back the binary of a db with server timestamps
            server_reply.write(response.content) # copy bytes into a file
            # 6 update records with the timestamps received from the server
            self.cursor.execute(f'ATTACH DATABASE "{server_reply.name}" AS reply')
            rowcount = 0
            for table in ('edits','reviews','media'):
                self.cursor.execute(f'UPDATE {table} SET server_timestamp = \
                                     (SELECT server_timestamp FROM reply.{table} AS r WHERE r.id = {table}.id)\
                        WHERE EXISTS (SELECT server_timestamp FROM reply.{table} AS r WHERE r.id = {table}.id)')
                rowcount += self.cursor.rowcount
            self.cursor.connection.commit()
            self.cursor.connection.close()
            print(f'{rowcount} records were time-stamped by the server')

    def server_changes(self):
        # 1 find the lastest_timestamp among our records
        # 2 Ask the server for more recent records which we haven't seen
        # 3 Copy these records into ourself
        #
        # 1 find the lastest_timestamp among our records
        latest_timestamp = 0
        for table in ('edits','reviews','media'):
            ts = self.cursor.execute(f'SELECT max(server_timestamp) FROM {table}').fetchone()[0] or 0
            latest_timestamp = max(latest_timestamp, ts)
        # 2 Ask the server for more recent records which we haven't seen
        print(f'Querying records since {datetime.datetime.fromtimestamp(latest_timestamp)}')
        response = requests.get(server_changes_url,
                                headers = self.auth_header(),
                                params = {'latest_timestamp': latest_timestamp},)
        # 3 Copy these records into ourself
        with NamedTemporaryFile() as server_reply:
            server_reply.write(response.content)
            self.cursor.execute(f'ATTACH DATABASE "{server_reply.name}" AS reply')
            rowcount = 0
            for table in ('edits','reviews','media'):
                self.cursor.execute(f'INSERT INTO {table} SELECT * FROM reply.{table}')
                rowcount += self.cursor.rowcount
            self.cursor.connection.commit()
            self.cursor.connection.close()
        print(f'{rowcount} records were received from the server')

    def sync(self):
        self.client_changes()  # push changes
        self.server_changes()  # pull changes
        

    @staticmethod
    def login():
        params = {
                'username': input('Username: '),
                'password': input('Password: '),
        }
        data = MultipartEncoder(fields = params)
        headers = { 'Content-type': data.content_type }
        response = requests.post( token_url, data = data, headers = headers)
        json = response.json()
        if response.ok:
            token_file.touch()
            token_file.write_text(json['access_token'])
            return 'Access token granted and saved. You can now access the sync server.'
        else:
            return json
