import json

file = open('CustomModel.json', 'r')
json_string = file.read()
# json类型的数据转化为python类型的数据
new_data = json.loads(json_string)
# 获取内容
name = new_data['elements']
new_name = new_data.get('elements')

print(name)
print(new_name)
file.close()