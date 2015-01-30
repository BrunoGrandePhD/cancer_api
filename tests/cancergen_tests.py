from nose import with_setup
from nose.tools import *
from cancergen import database


class test_database(object):

    @classmethod
    def setup_class(cls):
        cls.db_cnx = database.MysqlConnection(host="localhost", user="admin",
                                               password="Perl$nPython",
                                               database="cancergen_tests_db")
        cls.db_cnx.create_tables()
        cls.session = cls.db_cnx.start_session()

    @classmethod
    def teardown_class(cls):
        cls.db_cnx.close_session()
        cls.db_cnx.drop_tables()

    def test_table_creation(self):
        cnx = self.db_cnx.engine.connect()
        result = cnx.execute("SHOW TABLES;")
        print ", ".join([x[0] for x in result])
