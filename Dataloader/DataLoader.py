# @Author : bamtercelboo
# @Datetime : 2019/01/14 15:00
# @File : DataLoader.py
# @Last Modify Time : 2018/1/30 15:58
# @Contact : bamtercelboo@{gmail.com, 163.com}

"""
    FILE :
    FUNCTION :
"""
import os
import sys
import re
import random
import json
import time
import torch
import numpy as np
from sklearn.externals import joblib
from collections import OrderedDict
from Dataloader.Instance import Instance

from Dataloader.Dependency import readDepTree
from Dataloader.Dependency import *

from DataUtils.Common import *
torch.manual_seed(seed_num)
random.seed(seed_num)
np.random.seed(seed_num)


def batch_variable_depTree(trees, heads, rels, lengths, alphabet):
    """
    :param trees:
    :param heads:
    :param rels:
    :param lengths:
    :param alphabet:
    :return:
    """
    for tree, head, rel, length in zip(trees, heads, rels, lengths):
        sentence = []
        for idx in range(length):
            sentence.append(Dependency(idx, tree[idx].org_form, tree[idx].tag, head[idx], alphabet.rel_alphabet.id2words[rel[idx]]))
        yield sentence


class DataLoaderHelp(object):
    """
    DataLoaderHelp
    """

    @staticmethod
    def _clean_str(string):
        """
        Tokenization/string cleaning for all datasets except for SST.
        Original taken from https://github.com/yoonkim/CNN_sentence/blob/master/process_data.py
        """
        string = re.sub(r"[^A-Za-z0-9(),!?\'\`]", " ", string)
        string = re.sub(r"\'s", " \'s", string)
        string = re.sub(r"\'ve", " \'ve", string)
        string = re.sub(r"n\'t", " n\'t", string)
        string = re.sub(r"\'re", " \'re", string)
        string = re.sub(r"\'d", " \'d", string)
        string = re.sub(r"\'ll", " \'ll", string)
        string = re.sub(r",", " , ", string)
        string = re.sub(r"!", " ! ", string)
        string = re.sub(r"\(", " \( ", string)
        string = re.sub(r"\)", " \) ", string)
        string = re.sub(r"\?", " \? ", string)
        string = re.sub(r"\s{2,}", " ", string)
        return string.strip().lower()

    @staticmethod
    def _clean_punctuation(string):
        """
        :param string:
        :return:
        """
        string = re.sub(r"\'s", " \'s", string)
        string = re.sub(r"，", "", string)
        string = re.sub(r"。", "", string)
        string = re.sub(r"“", "", string)
        string = re.sub(r"”", "", string)
        string = re.sub(r"、", "", string)
        string = re.sub(r"：", "", string)
        string = re.sub(r"；", "", string)
        string = re.sub(r"（", "", string)
        string = re.sub(r"）", "", string)
        string = re.sub(r"《 ", "", string)
        string = re.sub(r"》", "", string)
        # string = re.sub(r"× ×", "", string)
        # string = re.sub(r"x")
        string = re.sub(r"  ", " ", string)
        return string.lower()

    @staticmethod
    def _sort(insts):
        """
        :param insts:
        :return:
        """
        sorted_insts = []
        sorted_dict = {}
        for id_inst, inst in enumerate(insts):
            sorted_dict[id_inst] = inst.words_size
        dict = sorted(sorted_dict.items(), key=lambda d: d[1], reverse=True)
        for key, value in dict:
            sorted_insts.append(insts[key])
        print("Sort Finished.")
        return sorted_insts


class DataLoader(DataLoaderHelp):
    """
    DataLoader
    """
    def __init__(self, path, shuffle, config, alphabet=None):
        """
        :param path: data path list
        :param shuffle:  shuffle bool
        :param config:  config
        """
        #
        print("Loading Data......")
        self.data_list = []
        self.max_count = config.max_count
        self.path = path
        self.shuffle = shuffle
        self.alphabet = alphabet

    def dataLoader(self):
        """
        :return:
        """
        start_time = time.time()
        path = self.path
        shuffle = self.shuffle
        assert isinstance(path, list), "Path Must Be In List"
        print("Data Path {}".format(path))
        for id_data in range(len(path)):
            print("Loading Data Form {}".format(path[id_data]))
            insts = self._Load_Each_JsonData(path=path[id_data])
            print("shuffle data......")
            random.shuffle(insts)
            self.data_list.append(insts)
        end_time = time.time()
        print("DataLoader Time {:.4f}".format(end_time - start_time))
        # return train/dev/test data
        if len(self.data_list) == 3:
            return self.data_list[0], self.data_list[1], self.data_list[2]
        elif len(self.data_list) == 2:
            return self.data_list[0], self.data_list[1]

    def _Load_Each_JsonData(self, path=None, train=False):
        assert path is not None, "The Data Path Is Not Allow Empty."
        insts = []
        now_lines = 0
        print()
        with open(path, encoding="UTF-8") as inf:
            for sentence in readDepTree(inf, self.alphabet):
                now_lines += 1
                if now_lines % 2000 == 0:
                    sys.stdout.write("\rreading the {} line\t".format(now_lines))
                inst = Instance()
                inst.sentence = sentence
                insts.append(inst)
                if len(insts) == self.max_count:
                    break
            sys.stdout.write("\rreading the {} line\t".format(now_lines))
        return insts

