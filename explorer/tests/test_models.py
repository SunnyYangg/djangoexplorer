from django.test import TestCase
from explorer.tests.factories import SimpleQueryFactory
from explorer.models import QueryLog, Query, QueryResult


class TestQueryModel(TestCase):

    def test_params_get_merged(self):
        q = SimpleQueryFactory(sql="select '$$foo$$';")
        q.params = {'foo': 'bar', 'mux': 'qux'}
        self.assertEqual(q.available_params(), {'foo': 'bar'})

    def test_query_log(self):
        self.assertEqual(0, QueryLog.objects.count())
        q = SimpleQueryFactory()
        q.log(None)
        self.assertEqual(1, QueryLog.objects.count())
        log = QueryLog.objects.first()
        self.assertEqual(log.run_by_user, None)
        self.assertEqual(log.query, q)
        self.assertFalse(log.is_playground)

    def test_playground_query_log(self):
        query = Query(sql='select 1;', title="Playground")
        query.log(None)
        log = QueryLog.objects.first()
        self.assertTrue(log.is_playground)


class TestQueryResults(TestCase):

    def setUp(self):
        self.qr = QueryResult('select 1 as "foo", "qux" as "mux";')

    def test_column_access(self):
        self.qr._data = [[1,2,3],[4,5,6],[7,8,9]]
        self.assertEqual(self.qr.column(1), [2,5,8])

    def test_headers(self):
        self.assertEqual(self.qr.headers[0], "foo")
        self.assertEqual(self.qr.headers[1], "mux")

    def test_data(self):
        self.assertEqual(self.qr.data, [[1, "qux"]])

    def test_unicode_detection(self):
        self.assertEqual(self.qr._get_unicodes(), [1])

    def test_numeric_detection(self):
        self.assertEqual(self.qr._get_numerics(), [(0, 'foo')])

    def test_transforms_are_identified(self):
        self.qr._headers = ['foo']
        got = self.qr._get_transforms()
        self.assertEqual([(0, '<a href="{0}">{0}</a>')], got)

    def test_transform_alters_row(self):
        self.qr._headers = ['foo', 'qux']
        self.qr._data = [[1,2]]
        self.qr.process()
        self.assertEqual(['<a href="1">1</a>', 2], self.qr._data[0])

    def test_multiple_transforms(self):
        self.qr._headers = ['foo', 'bar']
        self.qr._data = [[1,2]]
        self.qr.process()
        self.assertEqual(['<a href="1">1</a>', 'x: 2'], self.qr._data[0])