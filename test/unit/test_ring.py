# -*- coding: utf-8 -*-

import unittest

from hashring.app.ringbuilder import RingBuilder, Device
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
        # 正确的测试用例
        for dev in [
            Device(1, 'device_1', 200),
            Device(100, 'device_100', 1000),
            Device(10000, 'device_10000', 20000)
        ]:
            operation_res = RingBuilder().add_dev(dev)
            self.assertIsNone(operation_res)

        # 参数错误的测试用例
        for dev in [
            Device(-1, 'Device_1', 200),
            Device(2, '', 200),
            Device(3, 'Device_3', 211)
        ]:
            self.assertRaises(
                exc.ErrorInvalidParam,
                RingBuilder().add_dev,
                dev
            )

        # 边界情况

    def test_remove_dev(self):
        """删除设备接口.

        测试点：检查接口返回值是否为空
        注意：单测案例为示例，增加具体逻辑后需修改
        """
        ring_builder = RingBuilder()
        # 插入数据
        for dev in [
            Device(1, 'device_1', 200),
            Device(2, 'device_2', 100),
            Device(4, 'device_4', 800)
        ]:
            ring_builder.add_dev(dev)

        # 正常移除
        operation_res = ring_builder.remove_dev(4)
        self.assertIsNone(operation_res)

        # 移除不存在的设备
        self.assertRaises(KeyError, ring_builder.remove_dev, 4)

    def test_update_dev(self):
        """更新设备接口.

        测试点：检查接口返回值是否为空
        """
        ring_builder = RingBuilder()
        # 插入数据
        for dev in [
            Device(1, 'device_1', 200),
            Device(2, 'device_2', 100),
            Device(4, 'device_4', 800)
        ]:
            ring_builder.add_dev(dev)
        # 扩容测试用例
        self.assertIsNone(ring_builder.update_dev(2, 400))
        # 缩容测试用例
        self.assertIsNone(ring_builder.update_dev(4, 200))
        # 错误参数用例
        self.assertRaises(
            exc.ErrorInvalidParam,
            ring_builder.update_dev,
            0, 199
        )
        self.assertRaises(
            exc.ErrorInvalidParam,
            ring_builder.update_dev,
            1, 199
        )
        # 相同参数用例
        self.assertRaises(
            exc.ErrorInvalidParam,
            ring_builder.update_dev,
            4, 200
        )

    def test_hash_dev(self):
        """hash设备接口.

        测试点：检查hash结果是否符合预期
        """
        ring_builder = RingBuilder()
        # 插入数据
        for dev in [
            Device(1, 'device_1', 200),
            Device(2, 'device_2', 100),
            Device(4, 'device_4', 800)
        ]:
            ring_builder.add_dev(dev)

        self.assertGreater(ring_builder.hash_dev('just for test'), 0)


if __name__ == '__main__':
    suit = unittest.TestSuite
    suit.addTest(TestRingData("test_add_dev"))
    suit.addTest(TestRingData("test_update_dev"))
    suit.addTest(TestRingData("test_remove_dev"))
    suit.addTest(TestRingData("test_hash_dev"))


