from app import getPhonemes
import pandas as pd
import sys

triphones = []

def phonemize(sentence):

    tokens = sentence.split(' ')
    phonemes = getPhonemes(tokens)
    return '$'.join(phonemes)

def generateTriphones(phonemes):
    triphones = []
    for i in range(len(phonemes)):
        for j in range(len(phonemes)):
            for k in range(len(phonemes)):
                triphones.append(phonemes[i] + ' ' + phonemes[j] + ' ' + phonemes[k])
    return triphones

def scoreSentence(sentence,phonemes):
    flag = 0
    global triphones
    score = 0
    tokens = sentence.split('$')
    uniqueTokens = set(tokens)
    triphoneticTokens = [token for token in uniqueTokens if token.count(' ') > 1]
    for token in triphoneticTokens:
        for triphone in triphones:
            if token.find(triphone) != -1:
                score += 1
                triphones.remove(triphone)
                if triphones == []:
                    triphones = generateTriphones(phonemes)
                    flag = -1
    return score, flag

def Process(fil):

    global triphones
    file = open('itudict/vocab.phoneme', 'r',encoding='utf-8')
    data = []
    for line in file:
        data.append(line.strip())
    file.close()
    phonemes = data[4:]
    triphones = generateTriphones(phonemes)

    data = pd.read_csv(fil+'.csv')
    data = data.drop(['score','covered_vocab'],axis=1)

    i = 1
    while len(data) > 0:
        print('Processing File: '+str(i))
        sentencee = data[:20000]
        data = data[20000:]
        sentences = sentencee['sentence'].tolist()
        phonemes = []
        scores = []
        for j in range(len(sentences)):
            if j%1000 == 0:
                print('Processing Sentence: '+str(j))
                print(len(triphones))
            phones = phonemize(sentences[j])
            score, flag = scoreSentence(phones,phonemes)
            if flag == -1:
                data = []
            phonemes.append(phones)
            scores.append(score)
        data['Phonemes'] = phonemes
        data['score'] = scores
        data.to_csv(fil+'phonemized'+str(i)+'.csv', index=False)
        i += 1

if __name__ == '__main__':

    Process(sys.argv[1])