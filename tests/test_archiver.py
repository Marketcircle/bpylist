from unittest import TestCase
from tests.fixtures import get_fixture
from datetime import datetime, timezone
from bpylist.archive_types import uid, timestamp
from bpylist import archiver, bplist


class FooArchive:

    def __init__(self, title, stamp, count, cats, meta, empty, recursive):
        self.title = title
        self.stamp = stamp
        self.count = count
        self.categories = cats
        self.metadata = meta
        self.empty = empty
        self.recursive = recursive

    def encode_archive(self, archive):
        archive.encode('title', self.title)
        archive.encode('recurse', self.recursive)

    def decode_archive(self, archive):
        self.title = archive.decode('title')
        self.stamp = archive.decode('stamp')
        self.count = archive.decode('count')
        self.categories = archive.decode('categories')
        self.metadata = archive.decode('metadata')
        self.empty = archive.decode('empty')
        self.recursive = archive.decode('recursive')


class UnarchiveTest(TestCase):

    def fixture(self, name):
        return get_fixture(f'{name}_archive.plist')

    def unarchive(self, plist, with_class_map=True, opaque=False):
        class_map = {'crap.Foo': FooArchive} if with_class_map else None
        return archiver.unarchive(self.fixture(plist), class_map, opaque)

    def test_complains_about_incorrect_archive_type(self):
        with self.assertRaises(archiver.UnsupportedArchiver):
            self.unarchive('invalid_type')

    def test_complains_about_incorrect_version(self):
        with self.assertRaises(archiver.UnsupportedArchiveVersion):
            self.unarchive('invalid_version')

    def test_complains_about_missing_top_object(self):
        with self.assertRaises(archiver.MissingTopObject):
            self.unarchive('no_top')

    def test_complains_about_missing_top_object_uid(self):
        with self.assertRaises(archiver.MissingTopObjectUID):
            self.unarchive('no_root')

    def test_complains_about_missing_objects(self):
        with self.assertRaises(archiver.MissingObjectsArray):
            self.unarchive('no_objects')

    def test_complains_about_missing_class_metadata(self):
        with self.assertRaises(archiver.MissingClassMetaData):
            self.unarchive('no_class_meta')

    def test_complains_about_missing_class_names(self):
        with self.assertRaises(archiver.MissingClassName):
            self.unarchive('no_class_name')

    def test_complains_about_unmapped_classes(self):
        with self.assertRaises(archiver.MissingClassMapping):
            self.unarchive('simple', with_class_map=False)

    def test_complains_about_missing_class_uid(self):
        with self.assertRaises(archiver.MissingClassUID):
            self.unarchive('missing_uid')

    def test_unpack_archive_with_null_value(self):
        foo = self.unarchive('null')
        self.assertIsNone(foo.empty)

    def test_unpack_archive_with_no_values(self):
        foo = self.unarchive('empty')
        self.assertIsNone(foo.title)
        self.assertIsNone(foo.count)
        self.assertIsNone(foo.categories)
        self.assertIsNone(foo.metadata)

    def test_unpack_simple_archive(self):
        foo = self.unarchive('simple')
        self.assertEqual('yo', foo.title)
        self.assertEqual(42, foo.count)

    def test_unpack_complex_archive(self):
        foo = self.unarchive('complex')
        self.assertEqual('yo', foo.title)
        self.assertEqual(42, foo.count)
        self.assertEqual(['banana', 'apple'], foo.categories)
        self.assertEqual({'fruit': 'kiwi', 'veg': 'asparagus'}, foo.metadata)

    def test_unpack_recursive_archive(self):
        foo = self.unarchive('recursive')
        bar = foo.recursive
        self.assertTrue('hello', bar.title)
        self.assertTrue('yo', foo.title)

    def test_unpack_date(self):
        exp = datetime(2017, 2, 23, 6, 15, 58, 684097, tzinfo=timezone.utc)
        foo = self.unarchive('date')
        act = foo.stamp.to_datetime()
        self.assertEqual(exp, act)

    def test_unpack_data(self):
        foo = self.unarchive('data')
        self.assertEqual(foo, b'\xca\xfe\xba\xbe\x00\x01\x02\x03')
        self.assertTrue(isinstance(foo, bytearray))
        self.assertFalse(isinstance(foo, archiver.Mutable))

    def test_unpack_mutable_data(self):
        foo = self.unarchive('mutable_data')
        self.assertEqual(foo, b'\xca\xfe\xba\xbe\x00\x01\x02\x03')
        self.assertTrue(isinstance(foo, bytearray))
        self.assertTrue(isinstance(foo, archiver.Mutable))

    def test_unpack_circular_ref(self):
        foo = self.unarchive('circular')
        self.assertIs(foo.recursive, foo)

    def test_unpack_recursive_array(self):
        x2 = self.unarchive('recursive_array')
        self.assertIsInstance(x2, list)
        self.assertFalse(isinstance(x2, archiver.Mutable))
        self.assertEqual(len(x2), 1)
        x1 = x2[0]
        self.assertIsInstance(x2, list)
        self.assertIsInstance(x1, archiver.Mutable)
        self.assertIs(x1[0], x2)

    def test_unpack_recursive_dict(self):
        x2 = self.unarchive('recursive_dict')
        self.assertIsInstance(x2, dict)
        self.assertFalse(isinstance(x2, archiver.Mutable))
        self.assertEqual(len(x2), 1)
        x1 = x2['foo']
        self.assertIsInstance(x2, dict)
        self.assertIsInstance(x1, archiver.Mutable)
        self.assertIs(x1['bar'], x2)

    def test_index_set(self):
        foo = self.unarchive('index_set', opaque=True)
        self.assertIsInstance(foo, archiver.OpaqueObject)
        self.assertEqual(foo.__class__.__name__, 'NSIndexSet')
        self.assertEqual(foo.NSRangeCount, 1)
        self.assertEqual(foo.NSLocation, 3)
        self.assertEqual(foo.NSLength, 213)

    def test_mutable_index_set(self):
        foo = self.unarchive('mutable_index_set', opaque=True)
        self.assertIsInstance(foo, archiver.OpaqueObject)
        self.assertEqual(foo.__class__.__name__, 'NSMutableIndexSet')
        self.assertEqual(foo.NSRangeCount, 3)
        self.assertEqual(foo.NSRangeData, b'\x03\x08#\x0c\xea\xf2\x04\xaa\x12')

    def test_index_path(self):
        foo = self.unarchive('index_path', opaque=True)
        self.assertIsInstance(foo, archiver.OpaqueObject)
        self.assertEqual(foo.__class__.__name__, 'NSIndexPath')
        self.assertEqual(foo.NSIndexPathData, b'\x03\x04\t')
        self.assertEqual(foo.NSIndexPathLength, 3)

    def test_unpack_opaque(self):
        foo = self.unarchive('opaque', opaque=True)
        self.assertIsInstance(foo, archiver.OpaqueObject)
        self.assertEqual(foo.foo, 'abc')
        self.assertEqual(foo.bar, 42)
        self.assertEqual(len(foo.__dict__), 2)


class ArchiveTest(TestCase):

    def archive(self, obj):
        archived = archiver.archive(obj)
        unarchived = archiver.unarchive(archived)
        self.assertEqual(obj, unarchived)

    def test_primitive(self):
        self.archive(True)
        self.archive(9001)
        self.archive('banana')

    def test_core_types(self):
        self.archive(1)
        self.archive('two')
        self.archive(3.14)
        self.archive([1, 'two', 3.14])
        self.archive({ 'fruit': 'kiwi', 'veg': 'asparagus' })
        self.archive(b'hello')
        self.archive({ 'data': b'hello' })
        self.archive(timestamp(0))
        self.archive([timestamp(-4)])

    def test_custom_type(self):
        foo = FooArchive('herp', timestamp(9001), 42,
                         ['strawberries', 'dragonfruit'],
                         { 'key': 'value' },
                         False,
                         None)

    def test_circular_ref(self):
        foo = FooArchive('herp', timestamp(9001), 42,
                         ['strawberries', 'dragonfruit'],
                         { 'key': 'value' },
                         False,
                         None)
        foo.recursive = foo
        plist = bplist.parse(archiver.archive(foo, class_map={'crap.Foo': FooArchive}))
        foo_obj = plist['$objects'][1]
        self.assertEqual(uid(1), foo_obj['recurse'])

    def test_opaque(self):
        klass = archiver.OpaqueClassMap(archiver.ClassMap()).get_python_class(['XXCustomObject', 'NSObject'])
        foo = klass({'foo': 'abc', 'bar': 42})
        plist = bplist.parse(archiver.archive(foo, opaque=True))
        foo_obj = plist['$objects'][1]
        self.assertEqual('abc', plist['$objects'][foo_obj['foo']])
        self.assertEqual(42, foo_obj['bar'])
        klass_uid = foo_obj['$class']
        self.assertEqual(len(foo_obj), 3)
        class_obj = plist['$objects'][klass_uid]
        self.assertEqual('XXCustomObject', class_obj['$classname'])
        self.assertEqual(['XXCustomObject', 'NSObject'], class_obj['$classes'])


if __name__ == '__main__':
    from unittest import main
    main()
