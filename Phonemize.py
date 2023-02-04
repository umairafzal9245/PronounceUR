from app import getPhonemes
import pandas as pd

def phonemize(sentence):

    tokens = sentence.split(' ')
    phonemes = getPhonemes(tokens)
    return '$'.join(phonemes)


if __name__ == '__main__':

    filename = 'short'
    data = pd.read_csv(filename+'.csv')
    sentences = data['Sentence'].tolist()
    phonemes = []
    for i in range(len(sentences)):
        phonemes.append(phonemize(sentences[i]))
        if i%50000 == 0:
            print(i)

    data['Phonemes'] = phonemes
    data.to_csv(filename+'phonemized'+'.csv', index=False)