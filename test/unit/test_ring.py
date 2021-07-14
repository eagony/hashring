# -*- coding: utf-8 -*-

import unittest

from hashring.app.ringbuilder import RingBuilder
from hashring.common import exceptions as exc


class TestRingBase(unittest.TestCase):
    u"""测试基类."""

    def setUp(self):
        pass

    def tearDown(self):
        pass


class TestRingData(unittest.TestCase):
    u"""ring测试类."""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_add_dev(self):
        """添加设备接口.

        测试点：判断接口是否抛指定异常
        注意：单测案例为示例，增加具体逻辑后需修改
        """
        self.assertRaises(
            exc.ErrorNotImplemented,
            RingBuilder().add_dev,
            None)

    def test_remove_dev(self):
        """删除设备接口.

        测试点：检查接口返回值是否为空
        注意：单测案例为示例，增加具体逻辑后需修改
        """
        actual_res = RingBuilder().remove_dev(None)
        self.assertIsNone(actual_res)

    def test_hash_dev(self):
        """hash设备接口.

        测试点：检查hash结果是否符合预期
        注意：单测案例为示例，增加具体逻辑后需修改
        """
        actual_res = RingBuilder().hash_dev(None)
        self.assertEqual(actual_res, [])


if __name__ == '__main__':
    unittest.main()
