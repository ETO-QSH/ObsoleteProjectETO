import mido

# 打开MIDI文件
midi_file = mido.MidiFile('深海少女.mid')

# 创建新的MIDI文件对象
new_midi_file = mido.MidiFile()

# 记录每个轨道的速度值
velocities = {}

# 遍历每个轨道
for i, track in enumerate(midi_file.tracks):
    # 创建新的轨道对象
    new_track = mido.MidiTrack()

    # 遍历每个事件
    for msg in track:
        # 如果事件类型是乐器变换消息
        if msg.type == 'program_change':
            # 将乐器变换消息的乐器号改为1（大钢琴）
            new_msg = msg.copy(program=0)

            # 添加新的事件到新的轨道
            new_track.append(new_msg)
        elif msg.type in ['note_on', 'note_off']:
            # 获取该音符的原始速度值
            original_velocity = velocities.get(msg.note, msg.velocity)

            # 调整速度值（保持原始速度）
            new_velocity = original_velocity

            # 记录该音符的速度值
            velocities[msg.note] = original_velocity

            # 创建新的消息
            new_msg = msg.copy(velocity=new_velocity)

            # 添加新的事件到新的轨道
            new_track.append(new_msg)
        else:
            # 添加原始事件到新的轨道
            new_track.append(msg)

    # 添加新的轨道到新的MIDI文件
    new_midi_file.tracks.append(new_track)

# 保存新的MIDI文件
new_midi_file.save('output.mid')
