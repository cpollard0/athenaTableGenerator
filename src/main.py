import json
from os import path

tab = '\t'
sep = ','
serde = ' \n) ROW FORMAT SERDE \'org.openx.data.jsonserde.JsonSerDe\' \
WITH SERDEPROPERTIES ( \
  \'serialization.format\' = \'1\' \
) LOCATION \'s3://private.halocoach.com/data/\' '


#builds a map of json nodes and how "deep" they go; important for making sure we don't add an extra row dleimitere where we don't need one
def define_node_count(obj,node_dict,node):
    for key,value in obj.items():
        if node in node_dict:
            node_dict[node] = node_dict[node] + 1
        else:
            node_dict[node] = 1
        if type(value) is dict:
            define_node_count(value,node_dict,node + '.' + key)
        elif type(value) is list:
            if type(value[0]) is dict:
                define_node_count(value[0],node_dict,node + '.' + key)


def recursive_items(dictionary, level=0,node='root'):
    for key, value in dictionary.items():
        #print('key ' + key + ' node ' + node)
        node_dict[node] = node_dict[node] - 1 
        if node_dict[node] == 0:
            sep = " "
        else:
            sep = ","
        if level == 0:
            spacer = ' '
        else:
            spacer = ': '
        if type(value) is dict:
            yield (level * tab + key + spacer + 'struct<')
            # yield (key, value)
            yield from recursive_items(value, level + 1,node + '.' + key)
            yield (level + 1) * tab + '>' + sep
        elif type(value) is list:
            try:
                
                if type(value[0]) is dict: 
                    yield (level * tab + key + spacer + 'array<struct<')
                    yield from recursive_items(value[0], level + 1,node + '.' + key)
                    yield (level + 1) * tab + '>>' + sep
                else:
                    yield (level * tab + key + spacer + 'array<' + value[0] +'>') 
                
            except:
                pass  # print("error in list")
        else:
            if isinstance(value, int):
                yield (level * tab + key + spacer + "int" + sep)
            else: 
                # yield (level * '\t' + key + spacer + str(value) + ",")
                yield (level * tab + key + spacer + str(value) + sep)


data = ""

#fileName = '/Users/Chris/PycharmProjects/HaloCoach/Halo5.json'
fileName = 'C:\\Users\\cpollard\\Desktop\\athenaGenerator\\athenaTableGenerator\\sampleJsonDocs\\halo5_matchResult.json'
#fileName = 'C:\\Users\\cpollard\\Desktop\\athenaGenerator\\athenaTableGenerator\\sampleJsonDocs\\simple.json'

with open(fileName, 'r') as f:
    # read_data = f.read()
    lines = f.readlines()
f.closed
for line in lines:
    # print(line)
    if line.replace(' ', '')[:2] != '//':
        data = data + line.replace('null', '""')

data = json.loads(data)

table_name = "test_table"
table_schema = "default"
table = 'CREATE EXTERNAL TABLE IF NOT EXISTS {}.{}(\n'.format(table_schema,table_name)
schema = 'default'

# for item in data:
#   print(item)


node_dict = {}
define_node_count(data,node_dict,'root')

for value in recursive_items(data):
    table = table + value.replace('guid', 'string').replace('uint32', 'int') + '\n'

# print (table_def)
#table = table.replace(",>", ">")
print(table)
print(serde)
 

# print(table_def[:-3] + ')' + serde)
# for key,value in data.items():
#    print(value)
