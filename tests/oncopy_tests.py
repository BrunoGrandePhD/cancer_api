from nose.tools import *
import oncopy


class test_database_connection(object):

    @classmethod
    def setup_class(cls):
        cnx = oncopy.connect(oncopy.SqliteConnection())
        oncopy.connection.create_tables()

    @classmethod
    def teardown_class(cls):
        oncopy.connection.close()

    def test_table_creation(self):
        pass
