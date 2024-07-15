
import nbtlib
from nbtlib import *

with nbtlib.load('D:\\eto\\PCL\\.minecraft\\saves\\新的世界\\data\\idcounts.dat') as count:
    #count['']['data']['map'] = Int(count['']['data']['map'] + 1)
    print(count)


#with nbtlib.load('.\\images\\map_0.dat') as maps:
#    print(maps['']['data']['dimension'])
#    print(maps['']['data']['locked'])
#    print(type(maps['']['data']['scale']))
#    print(maps)
#new_file = File({"": Compound({'data': Compound({'map': Int('54')}), 'DataVersion': Int('2580')})})
#
#new_file.save('.\\images\\123.dat')
#print(new_file)
#new = File({"": Compound({'data': Compound({'zCenter': Int('0'), 'unlimitedTracking': Int('0'), 'trackingPosition': Int('0'), 'frames': List([]), 'scale': Int('0'), 'locked': Int('1'), 'dimension': String('minecraft:overworld'), 'banners': List([]), 'xCenter': Int('0'), 'colors': List(nbtlib.tag.ByteArray([]))})}), 'DataVersion': Int('2580')})
#new.save('.\\images\\map123.dat')
#print(new)
#