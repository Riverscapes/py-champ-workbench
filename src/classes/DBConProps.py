import os
import psycopg
from psycopg.rows import dict_row


class DBConProps():
    def __init__(self, host, port, user, password, db, root_cert=None, client_cert=None, ssl_key=None):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.db = db

        for file in [root_cert, client_cert, ssl_key]:
            if file is not None and not os.path.isfile(file):
                raise FileNotFoundError(f"File not found: {file}")

        self.root_cert = root_cert
        self.client_cert = client_cert
        self.ssl_key = ssl_key

    def connect(self):
        try:
            conn = psycopg.connect(
                dbname=self.db,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
                sslmode="require",
                sslrootcert=self.root_cert,
                sslcert=self.client_cert,
                sslkey=self.ssl_key,
                row_factory=dict_row
            )
            return conn
        except psycopg.OperationalError as e:
            print(f"Connection failed: {e}")

        return None
