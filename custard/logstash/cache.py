# -*- coding:utf-8 -*-
# !/usr/bin/env python3
"""
@File    :  cache.py
@Time    :  2023/6/15 19:55
@Author  :  YuYanQing
@Version :  1.0
@Contact :  mryu168@163.com
@License :  (C)Copyright 2022-2026
@Desc    :  None
"""
from abc import ABC, abstractmethod


class Cache(ABC):
    # ----------------------------------------------------------------------
    @abstractmethod
    def add_event(self, event):
        """Add the event to the cache.

        This method is meant to be called by various other threads.
        All other methods in this class are for caching messages and
        will be called by the log processing worker threads.

        :param str event: A log message
        :return:
        """
        pass

    # ----------------------------------------------------------------------
    @abstractmethod
    def get_queued_events(self):
        """Get pending events and mark them to be deleted

        :return: A list of events to be published
        """
        pass

    # ----------------------------------------------------------------------
    @abstractmethod
    def requeue_queued_events(self, events):
        """Mark pending_delete for events passed in to False.

        Used when an error occurs attempting to publish to logstash. Upon
        failure, we rollback the deletion flag to False.

        :param events:
        :return:
        """
        pass

    # ----------------------------------------------------------------------
    @abstractmethod
    def delete_queued_events(self):
        """Delete events marked for deletion

        :return:
        """
        pass

    # ----------------------------------------------------------------------
    @abstractmethod
    def expire_events(self):
        """Expire events older than the TTL. If no TTL is set, no action is taken.

        :return:
        """
        pass
