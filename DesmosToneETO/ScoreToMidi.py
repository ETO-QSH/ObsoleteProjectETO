
import re

def ScoreToMidi(notes, major, stair, name, Dict, split):
    NoteDict_0 = {'Ab':-4, 'A':-3, 'Bb':-2, 'B':-1, 'Cb':-1, 'C':0, 'C#':1, 'Db':1, 'D':2, 'Eb':3, 'E':4, 'F':5, 'F#':6, 'Gb':6, 'G':7}
    NoteDict_1 = {'0':None, '1':60, '2':62, '3':64, '4':65, '5':67, '6':69, '7':71}
    result = [(re.findall(r"\[[^\[\]]*\]|[^,\[\]]+", element[1:-1]) if element.startswith("[") and element.endswith("]") else [element]) for element in re.split(r",(?![^\[\]]*\])", notes.replace(" ", ""))]
    [[result[j].append('0') for i in range(max(len(i) for i in result) - len(k))] for j, k in enumerate(result)]
    for k in range(len(result[0])):
        locals()['%s_%s' % (name, k)] = [result[p][k] for p in range(len(result))]
    for j in range(len(result[0])):
        Dict['%s_%s' % (name, j)] = ''
        for note in locals()['%s_%s' % (name, j)]:
            Dict['%s_%s' % (name, j)] += ['R,' if note == '0' else 'f({}),'.format(NoteDict_1[note[0]] + NoteDict_0[major] + (len(re.findall('\+', note)) - len(re.findall('\-', note)) + stair) * 12 + [1 if '#' in note else (-1 if 'b' in note else 0)][0])][0] + ['R,' if split==True else ''][0]
    return Dict


print(ScoreToMidi(notes='[1, 1-], [1, 1-], [5, 1-], [5, 1-], [6, 4-], [6, 4-], [5, 1-], [0, 1-], [4, 5--], [4, 5--], [3, 1-], [3, 1-], [2, 5--], [2, 5--], [1, 1-], [0, 1-], [5, 1-], [5, 1-], [4, 5--], [4, 5--], [3, 1-], [3, 1-], [2, 5--], [0, 5--], [5, 1-], [5, 1-], [4, 5--], [4, 5--], [3, 1-], [3, 1-], [2, 5--], [0, 5--], [1, 1-], [1, 1-], [5, 1-], [5, 1-], [6, 4-], [6, 4-], [5, 1-], [0, 1-], [4, 5--], [4, 5--], [3, 1-], [3, 1-], [2, 5--], [2, 5--], [1, 1-], [0, 1-]',
                  major='C', stair=1, name='A', Dict={}, split=True)) # 小星星
