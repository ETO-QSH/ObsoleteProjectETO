# -*- coding:UTF-8 -*-
import os
import sys
import string
import pefile
import hashlib
import struct
def get_ico(argv_dic, group_dic):
    totalData, lastData, lastIconId = '', None, -1
    if group_dic[0]:
        resIcons = filter(lambda x: x.id==pefile.RESOURCE_TYPE['RT_ICON'], argv_dic['peobj'].DIRECTORY_ENTRY_RESOURCE.entries)
        idCount = struct.unpack('H', group_dic[0][4:6])[0]
        iconIds = set([struct.unpack('H', group_dic[0][i*14+18:i*14+20])[0]
                      for i in xrange(idCount)])
        iconIdMap = dict([(struct.unpack('H', group_dic[0][i*14+18:i*14+20])[0], i) for  i in xrange(idCount)])
        for resIcon in resIcons:
            if resIcon and hasattr(resIcon, 'directory'):
                for resId in resIcon.directory.entries:
                    if resId.id in iconIds:
                        lastIconId = resId.id
                    if hasattr(resId, 'directory'):
                        for resLang in resId.directory.entries:
                            lastData = argv_dic['peobj'].get_data(resLang.data.struct.OffsetToData, resLang.data.struct.Size)
                            if iconIdMap.has_key(resId.id) == False:
                                continue
                            iconIdx = iconIdMap[resId.id]
                            iconHeader = '\x00\x00\x01\x00\x01\x00' + group_dic[0][6 + iconIdx * 14:6 + iconIdx * 14 + 12] + '\x16\x00\x00\x00'
                            lastData = iconHeader + lastData
                            totalData = totalData + lastData
                    else:
                        lastData = argv_dic['peobj'].get_data(
                            resId.data.struct.OffsetToData, resId.data.struct.Size)
                        iconIdx = iconIdMap[resId.id]
                        iconHeader = '\x00\x00\x01\x00\x01\x00' + group_dic[0][6 + ToData, resId.data.struct.Size]
                        lastData = iconHeader + lastData
                        totalData = totalData + lastData
        md5obj = hashlib.md5()
        md5obj.update(totalData)
        path_filter = os.path.join(argv_dic['outdir'], md5obj.hexdigest())
        if os.path.exists(path_filter) == False:
            os.mkdir(path_filter)
            if argv_dic['if_makeico'] != 0:
                os.mkdir(os.path.join(path_filter, "ico"))
                for resIcon in resIcons:
                    if resIcon and hasattr(resIcon, 'directory'):
                        for resId in resIcon.directory.entries:
                            if resId.id in iconIds:
                                lastIconId = resId.id
                            if hasattr(resId, 'directory'):
                                for resLang in resId.directory.entries:
                                    lastData = argv_dic['peobj'].get_data(resLang.data.struct.OffsetToData, resLang.data.struct.Size)
                                    if iconIdMap.has_key(resId.id) == False:
                                        continue
                                    iconIdx = iconIdMap[resId.id]
                                    iconHeader = '\x00\x00\x01\x00\x01\x00' + group_dic[0][6 + iconIdx * 14:6 + iconIdx * 14 + 12] + '\x16\x00\x00\x00'
                                    lastData = iconHeader + lastData
                                    md5obj = hashlib.md5()
                                    md5obj.update(lastData[22:])
                                    file_ico = open(os.path.join(path_filter, "ico", md5obj.hexdigest() + ".ico"), "wb+")
                                    file_ico.write(lastData)
                                    file_ico.close()
                                    print("hash.md5(pe.resources[i].offset, pe.resources[i].length) == \""+md5obj.hexdigest()+ "\" or")
                            else:
                                lastData = argv_dic['peobj'].get_data(
                                    resId.data.struct.OffsetToData, resId.data.struct.Size)
                                iconIdx = iconIdMap[resId.id]
                                iconHeader = '\x00\x00\x01\x00\x01\x00' + group_dic[0][6 + iconIdx * 14:6 + iconIdx * 14 + 12] + '\x16\x00\x00\x00'
                                lastData = iconHeader + lastData
                                file_ico = open(os.path.join(path_filter, "ico", md5obj.hexdigest() + ".ico"), "wb+")
                                file_ico.write(lastData)
                                file_ico.close()
                                print("hash.md5(pe.resources[i].offset, pe.resources[i].length) == \""+md5obj.hexdigest()+ "\" or")
        argv_dic['peobj'].close()
        os.rename(argv_dic['path_sample'], os.path.join(path_filter, os.path.basename(argv_dic['path_sample']) + ".exe"))
        return True
    argv_dic['peobj'].close()
def scan_ico(path_sample, outdir, if_makeico):
    peobj = pefile.PE(path_sample)
    group_dic = {}
    if hasattr(peobj, 'DIRECTORY_ENTRY_RESOURCE'):
        resGroupIcon = filter(lambda x: x.id==pefile.RESOURCE_TYPE['RT_GROUP_ICON'], peobj.DIRECTORY_ENTRY_RESOURCE.entries)
        if len(resGroupIcon) > 0:
            for i in range(len(resGroupIcon)):
                resGroupIcon = resGroupIcon[i]
                if hasattr(resGroupIcon, 'directory'):
                    for resId in resGroupIcon.directory.entries:
                        if hasattr(resId, 'directory'):
                            for resLang in resId.directory.entries:
                                group_dic[0] = peobj.get_data(resLang.data.struct.OffsetToData, resLang.data.struct.Size)
                                return get_ico({'peobj':peobj, 'outdir':outdir, 'path_sample':path_sample, 'if_makeico':if_makeico}, group_dic)
                        else:
                            group_dic[0] = peobj.get_data(resId.data.struct.OffsetToData, resId.data.struct.Size)
                            return get_ico({'peobj':peobj, 'outdir':outdir, 'path_sample':path_sample, 'if_makeico':if_makeico}, group_dic)
                else:
                    peobj.close()
        else:
            peobj.close()
    else:
        peobj.close()
def plan():
#这里你可传参，我先帮你写死了
    if len(sys.argv) > 1:
        path_sample = sys.argv[1]
    if len(sys.argv) > 2:
        outdir = sys.argv[2]
    if len(sys.argv) > 3:
        if_makeico = int(sys.argv[3])
    if_sucess = False
    try:
        path_sample = "D:\新建文件夹\Tencent\QQ\Bin\QQScLauncher.exe"
        outdir = "./"
        if_makeico = 1
        if_sucess = scan_ico(path_sample, outdir, if_makeico)
    except Exception as e:
        if str(e).find("Error") != -1:
            print (path_sample + " scan ico failed.")
        return
    if if_sucess != True:
        os.rename(path_sample, os.path.join(outdir, "no_find_ico", os.path.basename(path.basename(path_sample) + ".exe")))
if __name__ == '__main__':
    plan() 