# -*- coding: utf-8 -*-
import hashlib
import json
import random
from hashring.common import exceptions as exc

BUILDER_FILE_PATH = '../Builder.json'
RING_FILE_PATH = '../Ring.json'

class Device(object):
    def __init__(self, id, name, weight, part_num):
        self.id = id
        self.name = name
        self.weight = weight
        self.part_num = part_num


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


class RingBuilder(object):
    """ring builder."""

    def __init__(self):
        # 分区比例，乘以weight后得到对应分区数量
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
        dev_info = dict()
        # 校验参数是否合法，这里假设id为正整数，
        # name不为空，weight为正数且为整百，part_num为正整数
        param_error_count = 0
        if isinstance(dev.id, int) and dev.id > 0:
            # 如果id不存在则添加到文件
            if dev.id in self.dev_id_to_dev_info.keys():
                param_error_count += 1
            else:
                dev_info['dev_id'] = dev.id
        else:
            param_error_count += 1

        if dev.name != "":
            dev_info['dev_name'] = dev.name
        else:
            param_error_count += 1

        if dev.weight > 0 and dev.weight % 100 == 0:
            dev_info['dev_weight'] = dev.weight
            dev_info['part_num'] = int(dev.weight * self.p)
        else:
            param_error_count += 1

        if param_error_count > 0:
            print("非法参数，请重试！")
            exit()

        # 保存到设备列表
        self.dev_list.append(dev_info)
        # 保存到设备id到设备信息的映射
        self.dev_id_to_dev_info[dev.id] = dev_info
        # 保存虚拟设备到设备id的映射
        for i in range(dev_info['part_num']):
            key = self.gen_key('device_%s_%s' % (dev.id, i))
            self.ring[key] = dev.id
            self._sorted_keys.append(key)
        self._sorted_keys.sort()

        # 保存设备信息到本地JSON文件
        write_to_json(BUILDER_FILE_PATH, self.dev_list)

        self.rebalance()

    def update_dev(self, dev_id, weight=None):
        u"""更新设备信息.

        :param dev_id: 设备ID
        :param weight: 权重
        """
        # 缓存旧dev
        dev = self.dev_id_to_dev_info.pop(dev_id)
        # 更新weight
        if weight > 0 and weight % 100 == 0:
            dev['dev_weight'] = weight
            dev['part_num'] = weight * self.p
        else:
            print("非法参数，请重试！")
            exit()
        # 删除设备
        self.remove_dev(dev.id)
        # 添加新设备
        self.add_dev(dev)

        write_to_json(BUILDER_FILE_PATH, self.dev_list)
        self.rebalance()

    def remove_dev(self, dev_id):
        u"""删除设备.

        :param dev_id: 待删除的设备ID
        """
        # 删除虚拟分区到磁盘的映射
        for i in range(0, self.dev_id_to_dev_info[dev_id]['part_num']):
            key = self.gen_key('device_%s_%s' % (dev_id, i))
            del self.ring[key]
            self._sorted_keys.remove(key)

        # 从设备列表中移除
        for dev in self.dev_list:
            if dev['dev_id'] == dev_id:
                self.dev_list.remove(dev)

        write_to_json(BUILDER_FILE_PATH, self.dev_list)
        self.rebalance()

    def rebalance(self):
        u"""重新平衡ring."""
        # 保存到本地JSON文件
        write_to_json(RING_FILE_PATH, self.ring)

    def hash_dev(self, key):
        u"""获取指定key hash到的设备."""
        if not self.ring:
            return None, None

        key = self.gen_key(key)

        nodes = self._sorted_keys
        for i in range(0, len(nodes)):
            node = nodes[i]
            # 返回就近节点
            if key <= node:
                return self.ring[node], i

        return self.ring[nodes[0]], 0

    def gen_key(self, key):
        u"""根据字符串哈希出key值"""
        m = hashlib.md5()
        m.update(key.encode('utf-8'))
        return m.hexdigest()


# 将数据写入到json文件
def write_to_json(filename, data):
    with open(filename, 'w', encoding='utf-8') as fp:
        json.dump(data, fp, ensure_ascii=False)


if __name__ == '__main__':
    rb = RingBuilder()
    # 批量添加设备
    for i in range(0, 100):
        id = 1 + i
        name = 'device_%s' % id
        weight = 200 + random.randint(1, 10) * 100
        part_num = int(weight * rb.p)

        dev = Device(id, name, weight, part_num)
        rb.add_dev(dev)

    # 随机删除一个设备
    rb.remove_dev(rb.dev_list[5]['dev_id'])
    # 获取指定key哈希到的设备
    print(rb.hash_dev("euihfoiwejfowef"))
    print("finished...")
