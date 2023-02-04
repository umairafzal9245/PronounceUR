from app import getPhonemes
import pandas as pd

def phonemize(sentence):

    tokens = sentence.split(' ')
    phonemes = getPhonemes(tokens)
    return '$'.join(phonemes)


if __name__ == '__main__':

    # filename = '../data/short'
    # data = pd.read_csv(filename+'.csv')
    # data['phonemes'] = data['sentence'].apply(phonemize)
    # data.to_csv(filename+'phonemized'+'.csv', index=False)
    print(phonemize('جنگ چھڑنے سے پہلے بروے نے مجھے کچھ آڑھا سیدھا طریقہ اور مشق سمجھائے'))