import os
import re
import sys
import jieba
import torch
from gensim.models import Word2Vec, word2vec
import numpy as np
import jieba.analyse
import matplotlib.pyplot as plt
from tqdm import tqdm

plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号#固定随机数
np.random.seed(100)
torch.cuda.manual_seed(100)
sys.stdout.flush()
nFile = 200
root_path = "D:\Desktop\内容安全\code\data"
class_list = os.listdir(root_path)
all_word_list = []

for c in class_list:
    class_path = root_path + "/" + c
    file_list = os.listdir(class_path)
    for name in file_list:
        file_path = class_path + "/" + name
        with open(file_path, "r", encoding="utf-8") as f:
            txt = f.read()
            txt = re.sub("[     \t\n]*", "", txt)
            word_list = jieba.analyse.textrank(txt, topK=None,
                                               withWeight=False, allowPOS=('ns', 'n', 'vn', 'v'))
            all_word_list.extend(word_list)
result = " ".join(all_word_list)
with open("result.txt", "w", encoding="utf-8") as f:
    f.write(result)
sentences = word2vec.Text8Corpus("result.txt")  # 加载语料
model = word2vec.Word2Vec(sentences, vector_size=200, min_count=1)  # 训练模型,维度设置为200,最小词频设置为1;
model.save("my_model.model")
model = Word2Vec.load("my_model.model")
'''
词频统计
'''
def train_f():
    class_all_words = {}
    print("对训练集词频统计")
    for c in tqdm(class_list):
        all_words = {}
        class_path = root_path + "/" + c
        file_list = os.listdir(class_path)
        # 取70%的文件作为训练集，并对训练集进行词频统计
        for name in file_list[:int(nFile * rate)]:
            file_path = class_path + "/" + name
            with open(file_path, "r", encoding="utf-8") as f:
                txt = f.read()
                txt = re.sub("[     \t\n]*", "", txt)
                word_list = jieba.analyse.textrank(txt, withWeight=False, allowPOS=('ns', 'n', 'vn', 'v'))
                for word in word_list:
                    if len(word) != 1:
                        if word in all_words.keys():
                            all_words[word] += 1
                        else:
                            all_words[word] = 1
        class_all_words[c] = all_words
    return class_all_words


"""
获取每个类的平均向量
"""
def average_class_vector(keyword_num):
    average_class_dic = {}
    for c in class_all_words:
        all_words_list = sorted(class_all_words[c].items(), key=lambda item: item[1], reverse=True)
        total = 0
        if keyword_num > len(all_words_list):
            for t in range(len(all_words_list)):
                total += model.wv[all_words_list[t][0]]
        else:
            for t in range(keyword_num):
                total += model.wv[all_words_list[t][0]]
        average_class_dic[c] = total / keyword_num
    return average_class_dic


'''计算两个向量之问的余弦相似度'''
def cos_sim(vector_a, vector_b):
    vector_a = np.array(vector_a)
    vector_b = np.array(vector_b)
    a_norm = np.linalg.norm(vector_a)
    b_norm = np.linalg.norm(vector_b)
    sim = np.dot(vector_a, vector_b) / (a_norm * b_norm)
    return sim


def predict(data):
    sim = {}
    for c in average_class_dic:
        sim[c] = cos_sim(data, average_class_dic[c])
        test_words_list = sorted(sim.items(), key=lambda item: item[1], reverse=True)
    return test_words_list[0][0]


def acc(keyword_num):
    true = 0
    false = 0
    print("Keyword_num:{}".format(keyword_num))
    for c in tqdm(class_list):
        class_path = root_path + "/" + c
        file_list = os.listdir(class_path)
        # 取30%的文件作为测试集，并对训练集中每个文件单独进行词频统计
        for name in file_list[int(nFile * rate):]:
            file_path = class_path + "/" + name
            with open(file_path, "r", encoding="utf-8") as f:
                test_data_words = {}
                txt = f.read()
                txt = re.sub("[     \t\n]*", "", txt)
                word_list = jieba.analyse.textrank(txt, withWeight=False, allowPOS=('ns', 'n', 'vn', 'v'))
                for word in word_list:
                    if len(word) != 1:
                        if word in test_data_words.keys():
                            test_data_words[word] += 1
                        else:
                            test_data_words[word] = 1
                test_words_list = sorted(test_data_words.items(), key=lambda item: item[1], reverse=True)

                total = 0
                if keyword_num > len(test_words_list):
                    for t in range(len(test_words_list)):
                        total += model.wv[test_words_list[t][0]]
                else:
                    for t in range(keyword_num):
                        total += model.wv[test_words_list[t][0]]
                average_test_vector = total / keyword_num
                pre = predict(average_test_vector)
                if pre == c:
                    true += 1
                else:
                    false += 1
    return true/(true + false)


if __name__ == '__main__':
    rate = 0.7
    keyword_num_list = [1, 3, 5, 10, 15, 20, 30, 50, 100, 200]
    acc_list = []
    class_all_words = train_f()
    print("计算准确率")
    for keyword_num in keyword_num_list:
        average_class_dic = average_class_vector(keyword_num)
        acc_list.append(round(acc(keyword_num), 3))
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.set_title('关键词个数与准确率的关系')
    ax.set_xlabel('关键词个数')
    ax.set_ylabel('准确率')
    plt.plot(keyword_num_list, acc_list, color='black', markerfacecolor='r', marker='o')
    for a, b in zip(keyword_num_list, acc_list):
        plt.text(a, b, (a, b), ha='center', va='bottom', fontsize=10)
    plt.show()
