import multiprocessing
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

def Process(fil, chunkStart, chunkEnd):
    global triphones
    file = open('itudict/vocab.phoneme', 'r',encoding='utf-8')
    data = []
    for line in file:
        data.append(line.strip())
    file.close()
    phonemes = data[4:]
    triphones = generateTriphones(phonemes)

    data = pd.read_csv(fil+'.csv')
    sentences = data.iloc[chunkStart:chunkEnd]['sentence'].tolist()
    phonemes = []
    scores = []
    for j in range(len(sentences)):
        if j%1000 == 0:
            print('Processing Sentence: '+str(j))
            print('Chunk: '+str(chunkStart)+' to '+str(chunkEnd))
            print(len(triphones))
        phones = phonemize(sentences[j])
        score, flag = scoreSentence(phones,phonemes)
        phonemes.append(phones)
        scores.append(score)
    return phonemes, scores

def parallelize(fil, n_jobs):
    data = pd.read_csv(fil+'.csv')
    chunkSize = int(len(data) / n_jobs)
    chunks = [(i*chunkSize, (i+1)*chunkSize) for i in range(n_jobs)]
    chunks[-1] = (chunks[-1][0], len(data)) # for the last chunk, the end may be different

    pool = multiprocessing.Pool(processes=n_jobs)
    results = [pool.apply_async(Process, args=(fil, chunk[0], chunk[1])) for chunk in chunks]
    pool.close()
    pool.join()

    phonemes = []
    scores = []
    for result in results:
        p, s = result.get()
        phonemes += p
        scores += s

    data['Phonemes'] = phonemes
    data['score'] = scores
    data.to_csv(fil+'phonemized.csv', index=False)

if __name__ == '__main__':
    fil = sys.argv[1]
    n_jobs = int(sys.argv[2])
    parallelize(fil, n_jobs)
