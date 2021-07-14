# -*- coding: utf-8 -*-

from __future__ import print_function
from sys import argv as sys_argv, exit

from hashring.app.ringbuilder import RingBuilder

EXIT_SUCCESS = 0
EXIT_ERROR = 2


class Commands(object):
    u"""命令行."""

    @staticmethod
    def add(dev=None):
        u"""添加设备."""
        with RingBuilder as rb:
            rb.add_dev(dev)

    @staticmethod
    def update(dev_id, weight=None):
        u"""更新设备.

        :param dev_id: 设备ID
        :param weight: 目标权重
        """
        with RingBuilder as rb:
            rb.update_dev(dev_id, weight)

    @staticmethod
    def remove(dev_id):
        u"""删除设备."""
        with RingBuilder as rb:
            rb.remove_dev(dev_id)

    @staticmethod
    def rebalance():
        u"""重新平衡."""
        with RingBuilder as rb:
            rb.rebanlance()

    @staticmethod
    def hash(key):
        u"""获取指定key hash到的设备."""
        with RingBuilder as rb:
            rb.hash(key)

    # TODO: 查看builder file、ring file等


def main(arguments=None):
    argv = arguments if arguments is not None \
        else sys_argv

    if len(argv) < 2:
        print("Invalid argument number.")
        exit(EXIT_ERROR)

    func = getattr(Commands, argv[1], None)
    if not func:
        print("Invalid argument.")
        exit(EXIT_ERROR)

    func()
    exit(EXIT_SUCCESS)
