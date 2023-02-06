import threading
import pandas as pd
import sys
from app import getPhonemes

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
                    flag = -1
    return score, flag

def worker(sentences, phonemes, scores, i):
    for j in range(len(sentences)):
        if j%1000 == 0:
            print(f'Processing Sentence {j} in Thread {i}')
        phones = phonemize(sentences[j])
        score, flag = scoreSentence(phones, phonemes)
        phonemes.append(phones)
        scores.append(score)
        if flag == -1:
            break
    return phonemes, scores

def Process(fil):
    global triphones
    file = open('itudict/vocab.phoneme', 'r', encoding='utf-8')
    data = []
    for line in file:
        data.append(line.strip())
    file.close()
    phonemes = data[4:]
    triphones = generateTriphones(phonemes)

    data = pd.read_csv(fil+'.csv')
    data = data.drop(['score', 'covered_vocab'], axis=1)

    i = 1
    while len(data) > 0:
        print(f'Processing File {i}')
        sentencee = data[:10000]
        data = data[10000:]
        sentences = sentencee['sentence'].tolist()
        phonemes_list = []
        scores_list = []
        threads = []
        num_threads = 16
        step = len(sentences)//num_threads
        for t in range(num_threads):
            start = step * t
            end = start + step
            if t == num_threads - 1:
                end = len(sentences)
            thread = threading.Thread(target=worker, args=(sentences[start:end], phonemes_list, scores_list, t))
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()
        data['Phonemes'] = phonemes_list
        data['score'] = scores_list
        data.to_csv(fil + 'phonemized' + str(i) + '.csv', index=False)
        i += 1


if __name__ == '__main__':
    Process(sys.argv[1])