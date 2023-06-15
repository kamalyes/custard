# -*- coding:utf-8 -*-
# !/usr/bin/env python3
"""
@File    :  database_test.py
@Time    :  2023/6/15 19:55
@Author  :  YuYanQing
@Version :  1.0
@Contact :  mryu168@163.com
@License :  (C)Copyright 2022-2026
@Desc    :  None
"""
from stat import S_IREAD, S_IRGRP, S_IROTH, S_IWUSR
import os
import sqlite3
import time
import unittest

from custard.logstash.constants import constants
from custard.logstash.database import DATABASE_SCHEMA_STATEMENTS, DatabaseCache, DatabaseDiskIOError


# pylint: disable=protected-access


class DatabaseCacheTest(unittest.TestCase):
    TEST_DB_FILENAME = "test.db"
    _connection = None

    # ----------------------------------------------------------------------
    @classmethod
    def setUpClass(cls):
        if os.path.isfile(cls.TEST_DB_FILENAME):
            os.remove(cls.TEST_DB_FILENAME)

    # ----------------------------------------------------------------------
    def setUp(self):
        self.cache = DatabaseCache(self.TEST_DB_FILENAME)

    # ----------------------------------------------------------------------
    def tearDown(self):
        stmt = "DELETE FROM `event`;"
        self.cache._open()
        with self.cache._connection as conn:
            conn.execute(stmt)
        self.cache._close()

    # ----------------------------------------------------------------------
    @classmethod
    def tearDownClass(cls):
        if os.path.isfile(cls.TEST_DB_FILENAME):
            os.remove(cls.TEST_DB_FILENAME)

    # ----------------------------------------------------------------------
    @classmethod
    def get_connection(cls):
        if cls._connection:
            return cls._connection

        cls._connection = sqlite3.connect(cls.TEST_DB_FILENAME, isolation_level="EXCLUSIVE")
        cls._connection.row_factory = sqlite3.Row
        for statement in DATABASE_SCHEMA_STATEMENTS:
            cls._connection.cursor().execute(statement)
        return cls._connection

    # ----------------------------------------------------------------------
    @classmethod
    def close_connection(cls):
        if cls._connection:
            cls._connection.close()
        cls._connection = None

    # ----------------------------------------------------------------------
    def test_disk_io_exception(self):
        self.cache.add_event("message")
        with self.assertRaises(DatabaseDiskIOError):
            # change permissions to produce error
            os.chmod(os.path.abspath("test.db"), S_IREAD | S_IRGRP | S_IROTH)
            self.cache.add_event("message")
        os.chmod(os.path.abspath("test.db"), S_IWUSR | S_IREAD)

    # ----------------------------------------------------------------------
    def test_add_event(self):
        self.cache.add_event("message")
        conn = self.get_connection()
        cursor = conn.cursor()
        events = cursor.execute("SELECT `event_text`, `pending_delete` FROM `event`;").fetchall()
        self.assertEqual(len(events), 1)
        event = events[0]
        self.assertEqual(event["event_text"], "message")

    # ----------------------------------------------------------------------
    def test_get_queued_events(self):
        self.cache.add_event("message")
        events = self.cache.get_queued_events()
        self.assertEqual(len(events), 1)

    # ----------------------------------------------------------------------
    def test_get_queued_events_batch_size(self):
        constants.QUEUED_EVENTS_BATCH_SIZE = 3

        self.cache.add_event("message 1")
        self.cache.add_event("message 2")
        self.cache.add_event("message 3")
        self.cache.add_event("message 4")
        self.cache.add_event("message 5")

        events = self.cache.get_queued_events()
        # expect only 3 events according to QUEUED_EVENTS_BATCH_SIZE
        self.assertEqual(len(events), constants.QUEUED_EVENTS_BATCH_SIZE)

    # ----------------------------------------------------------------------
    def test_get_queued_events_batch_size_underrun(self):
        constants.QUEUED_EVENTS_BATCH_SIZE = 3

        self.cache.add_event("message 1")

        events = self.cache.get_queued_events()
        # expect only 1 event as there are no more available
        self.assertEqual(len(events), 1)

    # ----------------------------------------------------------------------
    def test_get_queued_events_set_delete_flag(self):
        self.cache.add_event("message")
        events = self.cache.get_queued_events()
        self.assertEqual(len(events), 1)
        events = self.cache.get_queued_events()
        self.assertEqual(len(events), 0)

    # ----------------------------------------------------------------------
    def test_requeue_queued_events(self):
        self.cache.add_event("message")
        events = self.cache.get_queued_events()
        self.assertEqual(len(events), 1)
        self.cache.requeue_queued_events(events)

        events = self.cache.get_queued_events()
        self.assertEqual(len(events), 1)

    # ----------------------------------------------------------------------
    def test_delete_queued_events(self):
        self.cache.add_event("message")
        events = self.cache.get_queued_events()
        self.assertEqual(len(events), 1)
        self.cache.get_queued_events()
        self.cache.delete_queued_events()

        events = self.cache.get_queued_events()
        self.assertEqual(len(events), 0)

    # ----------------------------------------------------------------------
    def test_dont_delete_unqueued_events(self):
        self.cache.add_event("message")
        self.cache.delete_queued_events()

        events = self.cache.get_queued_events()
        self.assertEqual(len(events), 1)

    # ----------------------------------------------------------------------
    def test_expire_events(self):
        self.cache._event_ttl = 0
        self.cache.add_event("message")
        time.sleep(1)
        self.cache.expire_events()

        events = self.cache.get_queued_events()
        self.assertEqual(len(events), 0)


if __name__ == "__main__":
    unittest.main()
