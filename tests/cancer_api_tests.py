from nose.tools import *
import cancer_api


class test_database_connection(object):

    @classmethod
    def setup_class(cls):
        cnx = cancer_api.connect(cancer_api.SqliteConnection())
        cnx.create_tables()

    @classmethod
    def teardown_class(cls):
        cancer_api.connection.close()

    def test_table_creation(self):
        pass
