
from mido import MidiFile, tick2second; from math import gcd; import copy, os, re

def NewPrint(my_dict):
    [[print("\033[1;32m" + str(key) + ":" + "\033[0m", '['+value[0:-1]+']', end='\n\n') for key, value in my_dict.items()] if type(my_dict) == dict else print(my_dict)]

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

def SibToMidi(path, split=False, precise=25, flag=False, interval=None):
    tip = 0; Str = {}; Dict = {}; List = []; new_List = []; new_new_new_List = []; mid = MidiFile(path)
    for track in mid.tracks:
        passed_time = 0
        for msg in track:
            if (msg.type == 'note_on' or msg.type == 'note_off'):
                note = [j.split('_') if j[0] == 's' else j.split('=') for j in ('state'+str(msg)[4:]).split(' ')]
                for k in range(len(note)):
                    Dict[note[k][0]] = note[k][1]
                Dict['time'] = int(Dict['time']) + tip; Dict['note'] = int(Dict['note'])
                tip = Dict['time']; ab_time = tick2second(msg.time, mid.ticks_per_beat, tempo)
                real_time = ((ab_time + passed_time) * (bpm) * 1000 + 25) // 50; passed_time += ab_time
                if Dict['state'] == 'on':
                    del Dict['state']; Dict['time'] = int(real_time); List.append(copy.deepcopy(Dict))
            else:
                try:
                    tempo = msg.tempo; bpm = int(60000000/msg.tempo)
                except AttributeError:
                    pass
    def ratio(numbers):
        intervals = [(num - precise, num + precise) for num in sorted(numbers)]
        gys = [interval if interval != None else min(abc(intervals[i-1], intervals[i]) for i in range(len(intervals)))][0]
        return [int((numbers[i] + gys/2)/gys) for i in range(len(numbers))]
    def abc(num1, num2):
        return max(gcd(a, b) for a in range(int(num1[0]), int(num1[1])+1) for b in range(int(num2[0]), int(num2[1])+1))
    List.sort(key=lambda elem: elem['time'])
    [new_List[-1]['note'].append(k['note']) if len(new_List) > 0 and new_List[-1]['time'] == k['time'] else new_List.append({'time': k['time'], 'note': [k['note']]}) for k in List]
    new_new_List = copy.deepcopy(new_List)
    for k in range(len(new_List)):
        new_new_List[k]['time'] = [0 if k == 0 else new_List[k]['time'] - new_List[k-1]['time']][0]
    numbers = [(new_new_List[k]['time']) for k in range(len(new_new_List))]
    if flag == True:
        return numbers
    atp = ratio(numbers); music_name, _ = os.path.splitext(os.path.basename(path))
    for k in range(len(new_new_List)):
        new_new_List[k]['time'] = atp[k] + split - 1
        a = max(len(k['note']) for k in new_new_List)
        [new_new_List[k]['note'].append(0) for i in range(a-len(new_new_List[k]['note']))]
    [[[new_new_new_List.append([0 for i in range(len(new_new_List[0]['note']))]) for i in range(k['time'])], new_new_new_List.append(k['note']) if k['time'] != (split - 1) else new_new_new_List.append(k['note'])] for k in new_new_List]
    for k in range(len(new_new_new_List[0])):
        locals()['%s_%s' % (music_name, k)] = [new_new_new_List[p][k] for p in range(len(new_new_new_List))]
    for j in range(len(new_new_new_List[0])):
        Str['%s_%s' % (music_name, j)] = []; [[Str['%s_%s' % (music_name, j)].append('R,') if note == 0 else Str['%s_%s' % (music_name, j)].append('f({}),'.format(note))] for note in locals()['%s_%s' % (music_name, j)]]
    for y in range(len(Str['%s_%s' % (music_name, j)])):
        for x in range(len(new_new_new_List[0])):
            if x == 0 and y != 0 and Str['%s_%s' % (music_name, 0)][y] == Str['%s_%s' % (music_name, 0)][y-1]:
                Str['%s_%s' % (music_name, 0)][y], Str['%s_%s' % (music_name, 1)][y] == Str['%s_%s' % (music_name, 1)][y], Str['%s_%s' % (music_name, 0)][y]
            elif x != 0 and y != 0 and Str['%s_%s' % (music_name, x)][y] == Str['%s_%s' % (music_name, x)][y-1]:
                Str['%s_%s' % (music_name, x)][y], Str['%s_%s' % (music_name, x-1)][y] == Str['%s_%s' % (music_name, x-1)][y], Str['%s_%s' % (music_name, x)][y]
    for j in range(len(new_new_new_List[0])):
        Str['%s_%s' % (music_name, j)] = ''.join(Str['%s_%s' % (music_name, j)])
    return Str

NewPrint(ScoreToMidi(notes='[1, 1-], [1, 1-], [5, 1-], [5, 1-], [6, 4-], [6, 4-], [5, 1-], [0, 1-], [4, 5--], [4, 5--], [3, 1-], [3, 1-], [2, 5--], [2, 5--], [1, 1-], [0, 1-], [5, 1-], [5, 1-], [4, 5--], [4, 5--], [3, 1-], [3, 1-], [2, 5--], [0, 5--], [5, 1-], [5, 1-], [4, 5--], [4, 5--], [3, 1-], [3, 1-], [2, 5--], [0, 5--], [1, 1-], [1, 1-], [5, 1-], [5, 1-], [6, 4-], [6, 4-], [5, 1-], [0, 1-], [4, 5--], [4, 5--], [3, 1-], [3, 1-], [2, 5--], [2, 5--], [1, 1-], [0, 1-]',
                     major='C', stair=1, name='小星星', Dict={}, split=True)) # 小星星

NewPrint(SibToMidi(path='Moonlike Smile.mid', split=False, precise=25, flag=False, interval=100)) # Moonlike Smile
