import numpy as np
from torch.utils.data.dataset import Dataset
from dataLoader.utils import seq_padding,code2index, position_idx, index_seg
import torch


class Predict(Dataset):
    def __init__(self, token2idx, age2idx, dataframe, max_len, code='code', age='age', label='label'):
        # dataframe preproecssing
        # filter out the patient with number of visits less than min_visit
        self.vocab = token2idx
        self.max_len = max_len
        self.code = dataframe[code]
        self.age = dataframe[age]
        self.label = dataframe[label]
        self.patid = dataframe['ID']
        self.age2idx = age2idx

    def __getitem__(self, index):
        """
        return: age, code, position, segmentation, mask, label
        """
        # cut data
        age = self.age[index]
        code = self.code[index]
        label = self.label[index]
        patid = self.patid[index]

        # extract data
        age = age[(-self.max_len+1):]
        code = code[(-self.max_len+1):]

        # avoid data cut with first element to be 'SEP'
        if code[0] != 'SEP':
            code = np.append(np.array(['CLS']), code)
            age = np.append(np.array(age[0]), age)
        else:
            code[0] = 'CLS'

        # mask 0:len(code) to 1, padding to be 0
        mask = np.ones(self.max_len)
        mask[len(code):] = 0

        # pad age sequence and code sequence
        age = seq_padding(age, self.max_len, token2idx=self.age2idx)

        tokens, code = code2index(code, self.vocab)
        #_, label = code2index(label, self.label_vocab) do not need to tokenlize label as binary classification

        # get position code and segment code
        tokens = seq_padding(tokens, self.max_len)
        position = position_idx(tokens)
        segment = index_seg(tokens)

        # pad code and label
        code = seq_padding(code, self.max_len, symbol=self.vocab['PAD'])
        #label = seq_padding(label, self.max_len, symbol=-1) no need to pad as one sequence only have one label

        return torch.LongTensor(age), torch.LongTensor(code), torch.LongTensor(position), torch.LongTensor(segment), \
               torch.LongTensor(mask), torch.LongTensor(label), torch.LongTensor([int(patid)])

    def __len__(self):
        return len(self.code)