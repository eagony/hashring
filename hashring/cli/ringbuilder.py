# -*- coding: utf-8 -*-

from __future__ import print_function

import json
from sys import argv as sys_argv, exit

from hashring.app.ringbuilder import RingBuilder
from hashring.common.log import mylog
from hashring.common import exceptions as exc

EXIT_SUCCESS = 0
EXIT_ERROR = 2
LOG = mylog()


class Commands(object):
    u"""命令行."""

    @staticmethod
    def add():
        u"""添加设备."""
        # 获取dev参数
        args = sys_argv[2:]
        dev_id = int(args[2]),
        dev_name = args[3],
        dev_weight = int(args[4])
        # 初步校验参数是否合法，这里假设id为正整数，
        # name不为空，weight为正数且为整百，part_num为正整数
        dev_info = dict()
        if isinstance(dev_id, int) and dev_id > 0:
            dev_info['dev_id'] = dev_id
        else:
            LOG.error('RingBuilder.add_dev: 无效的参数id。')
            raise exc.ErrorInvalidParam('id')

        if dev_name != "":
            dev_info['dev_name'] = dev_name
        else:
            LOG.error('RingBuilder.add_dev: 无效的参数name。')
            raise exc.ErrorInvalidParam('name')

        if dev_weight > 0 and dev_weight % 100 == 0:
            dev_info['dev_weight'] = dev_weight
        else:
            LOG.error('RingBuilder.add_dev: 无效的参数weight')
            raise exc.ErrorInvalidParam('weight')

        # 执行
        with RingBuilder as rb:
            rb.add_dev(dev_info)

    @staticmethod
    def update():
        u"""更新设备."""
        try:
            dev_id = int(sys_argv[2])
        except exc.ErrorInvalidParam:
            LOG.error('输入的dev_id有误。')
            raise exc.ErrorInvalidParam('dev_id')

        try:
            new_weight = int(sys_argv[3])
        except exc.ErrorInvalidParam:
            LOG.error('输入的weight有误。')
            raise exc.ErrorInvalidParam('weight')

        with RingBuilder as rb:
            rb.update_dev(dev_id, new_weight)

    @staticmethod
    def remove():
        u"""删除设备."""
        try:
            dev_id = int(sys_argv[2])
        except exc.ErrorInvalidParam:
            LOG.error('输入的dev_id有误。')
            raise exc.ErrorInvalidParam('dev_id')

        with RingBuilder as rb:
            rb.remove_dev(dev_id)

    @staticmethod
    def rebalance():
        u"""重新平衡."""
        with RingBuilder as rb:
            rb.rebanlance()

    @staticmethod
    def hash():
        u"""获取指定key hash到的设备."""
        key = sys_argv[2]
        if len(key) == 0:
            LOG.error('key is empty.')
            raise exc.ErrorInvalidParam('key')

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
