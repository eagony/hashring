# -*- coding: utf-8 -*-
import json
import hashlib
from hashring.common import log
from hashring.common import exceptions as exc

BUILDER_FILE_PATH = '../Builder.json'
RING_FILE_PATH = '../Ring.json'
LOG = log.mylog()


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
        LOG.error('加载文件%s出错。'.format(filename))
        raise exc.ErrorFileOpenFailed

    def save(self, filename):
        u"""保存文件. 将Python字典对象保存到JSON配置文件中.

        :param filename: 文件名
        """
        with open(filename, 'w', encoding='utf-8') as fp:
            json.dump(self.data, fp, ensure_ascii=False)
        LOG.error('保存文件%s出错。'.format(filename))
        raise exc.ErrorFileSaveFailed


class BuilderManager(object):
    """BuilderManager，用于维护BuilderFile"""

    def __init__(self):
        # 设备ID到设备信息的映射
        self.dev_id_to_dev_info = dict()
        # BuilderFile的文件管理器
        self.data_manager = DataManager().load(BUILDER_FILE_PATH)

    def add(self, dev_info):
        u"""新添加设备信息

        :param dev_info: 待添加的设备信息
        """
        self.data_manager.data.append(dev_info)
        self.data_manager.save(BUILDER_FILE_PATH)
        self.dev_id_to_dev_info[dev_info['dev_id']] = dev_info

    def remove(self, dev_id):
        u"""移除设备信息

        :param dev_id: 待移除的设备id
        """
        if dev_id not in self.dev_id_to_dev_info.keys():
            raise exc.ErrorInvalidParam('id，不存在此id')
        # 从设备列表中移除
        for dev in self.data_manager.data:
            if dev['dev_id'] == dev_id:
                self.data_manager.data.remove(dev)
        self.data_manager.save()
        # 移除设备id到设备信息的映射
        del self.dev_id_to_dev_info[dev_id]

    def update(self, dev_id, weight, part_num):
        u"""更新设备信息

        :param dev_id: 待更新的设备的id
        :param weight: 设备新的weight值
        :param part_num: 设备新的part_num值
        """
        # 如果不存在此设备
        if dev_id in self.dev_id_to_dev_info.keys():
            dev = self.dev_id_to_dev_info[dev_id]
        else:
            raise exc.ErrorInvalidParam('id，不存在此id')
        # 更新weight
        if weight > 0 and weight % 100 == 0 and weight != dev['dev_weight']:
            dev['dev_weight'] = weight
            dev['part_num'] = part_num
        else:
            raise exc.ErrorInvalidParam('weight')

    def get_by_id(self, dev_id):
        u"""通过设备id返回设备信息。

        :param dev_id: 要查询的设备的id
        :return 对应id的设备信息，无则返回None
        """
        if dev_id not in self.dev_id_to_dev_info.keys():
            return None
        return self.dev_id_to_dev_info[dev_id]

    def get_first(self):
        u"""返回第一个设备。

        :return 设备信息，无则返回None
        """
        if len(self.dev_id_to_dev_info) >= 1:
            return self.dev_id_to_dev_info[0]
        return None


class RingManager(object):
    """RingManager，用于维护RingFile"""
    def __init__(self):
        # 分区比例，乘以weight后得到分区数量
        self.p = 0.02
        # 虚拟分区到设备id的映射
        self.ring = dict()
        # 虚拟分区列表
        self._sorted_keys = list()
        # RingFile的文件管理器
        self.data_manager = DataManager().load(RING_FILE_PATH)

    def add(self, dev_info):
        u"""新增虚拟分区的映射

        :param dev_info: 设备信息
        """
        # 保存虚拟设备到设备id的映射
        for i in range(dev_info['part_num']):
            key = gen_key('device_%s_p%s' % (dev_info['id'], i))
            self.ring[key] = dev_info['id']
            self._sorted_keys.append(key)
        self.rebanlance()

    def remove(self, dev_id, part_num):
        u"""新增虚拟分区的映射

        :param dev_id: 设备id
        :param part_num: 设备分区数量
        """
        # 删除虚拟分区到磁盘的映射
        for i in range(0, part_num):
            key = gen_key('device_%s_p%s' % (dev_id, i))
            if self.ring[key]:
                del self.ring[key]
            else:
                raise KeyError
            self._sorted_keys.remove(key)
        self.rebanlance()

    def update(self, dev_id, old_part_num, new_part_num):
        u"""更新设备和对应的虚拟分区

        :param dev_id: 设备id
        :param old_part_num: 设备的原分区数量
        :param new_part_num: 沈北的新分区数量
        """
        if new_part_num > old_part_num:
            # 增加设备的分区数量
            for i in range(old_part_num, new_part_num):
                key = gen_key('device_%s_p%s' % (dev_id, i))
                self.ring[key] = dev_id
                self._sorted_keys.append(key)
        else:
            # 减少设备的分区数量
            for i in range(new_part_num, old_part_num):
                key = gen_key('device_%s_p%s' % (dev_id, i))
                del self.ring[key]
                self._sorted_keys.remove(key)
        self.remove()

    def hash_dev(self, key):
        u"""获取指定key hash到的设备.

        :param key: 指定key
        :return 设备id
        """
        if not self.ring:
            return None

        key = gen_key(key)
        for node in self._sorted_keys:
            # 返回就近节点
            if key <= node:
                return self.ring[node]
        # 如果没有对应的匹配，返回第一个设备的id

    def rebanlance(self):
        u"""重新平衡ring."""
        self._sorted_keys.sort()
        # 保存到本地JSON文件
        self.data_manager.save(RING_FILE_PATH)


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
        # RingFile的管理器
        self.ring_manager = RingManager()
        # BuilderFile的管理器
        self.builder_manager = BuilderManager()

    def __enter__(self):
        return self

    def add_dev(self, dev_info):
        u"""添加设备.

        :param dev: 待添加的设备信息
        """
        # 如果设备id已存在
        if self.builder_manager.get_by_id(dev_info['dev_id']) is not None:
            LOG.error('RingBuilder.add_dev: 此id已存在。')
            raise exc.ErrorInvalidParam('id,此id已存在')
        dev_info['part_num'] = int(dev_info['weight'] * self.p)

        self.builder_manager.add(dev_info)
        self.ring_manager.add(dev_info)

    def update_dev(self, dev_id, weight=None):
        u"""更新设备信息.

        :param dev_id: 设备ID
        :param weight: 权重
        """
        old_part_num = self.builder_manager.get_by_id(dev_id)['part_num']
        new_part_num = int(weight * self.p)
        self.builder_manager.update(dev_id, weight, new_part_num)
        self.ring_manager.update(dev_id, old_part_num, new_part_num)

    def remove_dev(self, dev_id):
        u"""删除设备.

        :param dev_id: 待删除的设备ID
        """
        temp_dev = self.builder_manager.get_by_id(dev_id)
        self.builder_manager.remove(dev_id)
        self.ring_manager.remove(dev_id, temp_dev['part_num'])

    def hash_dev(self, key):
        u"""获取指定key hash到的设备."""
        dev = self.ring_manager.hash_dev(key)
        if dev is not None:
            return dev
        # 如果没有对应的匹配，返回第一个设备的id
        return self.builder_manager.get_first()
