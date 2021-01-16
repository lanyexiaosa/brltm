def age_vocab(min_age, max_age, symbol=None):
    age2idx = {}
    idx2age = {}
    if symbol is None:
        symbol = ['PAD', 'UNK']

    for i in range(len(symbol)):
        age2idx[str(symbol[i])] = i
        idx2age[i] = str(symbol[i])
    
    for i in range(min_age,max_age+1):
        age2idx[str(i)] = len(symbol) + i-min_age
        idx2age[len(symbol) + i-min_age] = str(i)
   
    return age2idx, idx2age