# -*- coding: utf-8 -*-
import hashlib
import json
import random
from hashring.common import exceptions as exc

BUILDER_FILE_PATH = '../Builder.json'
RING_FILE_PATH = '../Ring.json'


class Device(object):
    """Device"""

    def __init__(self, id, name, weight):
        self.id = id
        self.name = name
        self.weight = weight


class DataManager(object):
    """Data manager."""

    def __init__(self, data):
        self.data = data

    @classmethod
    def load(cls, filename):
        u"""加载文件. 将JSON配置文件转成Python字典对象.

        :param filename: 文件名
        """
        with open(filename, 'r', encoding='utf-8') as fp:
            return cls(json.load(fp))
        raise exc.ErrorFileOpenFailed

    def save(self, filename):
        u"""保存文件. 将Python字典对象保存到JSON配置文件中.

        :param filename: 文件名
        """
        with open(filename, 'w', encoding='utf-8') as fp:
            json.dump(self.data, fp, ensure_ascii=False)
        raise exc.ErrorFileSaveFailed


def gen_key(key):
    u"""根据字符串哈希出key值"""
    m = hashlib.md5()
    m.update(key.encode('utf-8'))
    return m.hexdigest()


class RingBuilder(object):
    """ring builder."""

    def __init__(self):
        # 分区比例，乘以weight后得到分区数量
        self.p = 0.02
        # 虚拟分区到设备id的映射
        self.ring = dict()
        # 设备列表
        self.dev_list = list()
        # 虚拟分区列表
        self._sorted_keys = list()
        # 设备ID到设备信息的映射
        self.dev_id_to_dev_info = dict()

    def add_dev(self, dev):
        u"""添加设备.

        :param dev: 待添加的设备信息
        """
        # 校验参数是否合法，这里假设id为正整数，
        # name不为空，weight为正数且为整百，part_num为正整数
        dev_info = dict()
        if isinstance(dev.id, int) and dev.id > 0:
            # 如果id不存在则添加到文件
            if dev.id in self.dev_id_to_dev_info.keys():
                raise exc.ErrorInvalidParam('id,此id已存在')
            else:
                dev_info['dev_id'] = dev.id
        else:
            raise exc.ErrorInvalidParam('id')

        if dev.name != "":
            dev_info['dev_name'] = dev.name
        else:
            raise exc.ErrorInvalidParam('name')

        if dev.weight > 0 and dev.weight % 100 == 0:
            dev_info['dev_weight'] = dev.weight
            dev_info['part_num'] = int(dev.weight * self.p)
        else:
            raise exc.ErrorInvalidParam('weight')

        # 保存到设备列表
        self.dev_list.append(dev_info)
        # 保存到设备id到设备信息的映射
        self.dev_id_to_dev_info[dev.id] = dev_info
        # 保存虚拟设备到设备id的映射
        for i in range(dev_info['part_num']):
            key = gen_key('device_%s_p%s' % (dev.id, i))
            self.ring[key] = dev.id
            self._sorted_keys.append(key)

        # 保存设备信息到本地JSON文件
        write_to_json(BUILDER_FILE_PATH, self.dev_list)
        self.rebalance()

    def update_dev(self, dev_id, weight=None):
        u"""更新设备信息.

        :param dev_id: 设备ID
        :param weight: 权重
        """
        if dev_id in self.dev_id_to_dev_info.keys():
            dev = self.dev_id_to_dev_info[dev_id]
        else:
            raise exc.ErrorInvalidParam('id，不存在此id')
        old_part_num = dev['part_num']
        # 更新weight
        if weight > 0 and weight % 100 == 0 and weight != dev['dev_weight']:
            dev['dev_weight'] = weight
            dev['part_num'] = int(weight * self.p)
        else:
            raise exc.ErrorInvalidParam('weight')

        if dev['part_num'] > old_part_num:
            # 扩容虚拟分区到设备的映射
            for i in range(old_part_num, dev['part_num']):
                # TODO 这里需不需要考虑哈希冲突的情况
                key = gen_key('device_%s_p%s' % (dev['dev_id'], i))
                self.ring[key] = dev['dev_id']
                self._sorted_keys.append(key)
        else:
            # 缩容
            for i in range(dev['part_num'], old_part_num):
                key = gen_key('device_%s_p%s' % (dev_id, i))
                del self.ring[key]
                self._sorted_keys.remove(key)

        write_to_json(BUILDER_FILE_PATH, self.dev_list)
        self.rebalance()

    def remove_dev(self, dev_id):
        u"""删除设备.

        :param dev_id: 待删除的设备ID
        """
        if dev_id not in self.dev_id_to_dev_info.keys():
            raise exc.ErrorInvalidParam('id，不存在此id')
        # 删除虚拟分区到磁盘的映射
        for i in range(0, self.dev_id_to_dev_info[dev_id]['part_num']):
            key = gen_key('device_%s_p%s' % (dev_id, i))
            if self.ring[key]:
                del self.ring[key]
            else:
                raise KeyError
            self._sorted_keys.remove(key)

        # 从设备列表中移除
        for dev in self.dev_list:
            if dev['dev_id'] == dev_id:
                self.dev_list.remove(dev)

        write_to_json(BUILDER_FILE_PATH, self.dev_list)
        self.rebalance()

    def rebalance(self):
        u"""重新平衡ring."""
        self._sorted_keys.sort()
        # 保存到本地JSON文件
        write_to_json(RING_FILE_PATH, self.ring)

    def hash_dev(self, key):
        u"""获取指定key hash到的设备."""
        if not self.ring:
            return 0

        key = gen_key(key)
        for node in self._sorted_keys:
            # 返回就近节点
            if key <= node:
                return self.ring[node]
        # 如果没有对应的匹配，返回第一个设备的id
        return self.dev_list[0]['dev_id']


# 将数据写入到json文件
def write_to_json(filename, data):
    with open(filename, 'w', encoding='utf-8') as fp:
        json.dump(data, fp, ensure_ascii=False)
