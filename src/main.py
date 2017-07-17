import json

tab = '\t'
sep = ','
serde = ' \n) ROW FORMAT SERDE \'org.openx.data.jsonserde.JsonSerDe\' \
WITH SERDEPROPERTIES ( \
  \'serialization.format\' = \'1\' \
) LOCATION \'s3://private.halocoach.com/data/\' '


def recursive_items(dictionary, level=0):
    for key, value in dictionary.items():
        if level == 0:
            spacer = ' '
        else:
            spacer = ':'
        if type(value) is dict:
            yield (level * tab + key + spacer + 'struct<')
            # yield (key, value)
            yield from recursive_items(value, level + 1)
            yield (level + 1) * tab + '>'
        elif type(value) is list:
            try:
                yield (level * tab + key + spacer + 'array<')
                yield from recursive_items(value[0], level + 1)
                yield (level + 1) * tab + '>'
            except:
                pass  # print("error in list")
        else:
            if isinstance(value, int):
                pass
            else:
                # yield (level * '\t' + key + spacer + str(value) + ",")
                yield (level * tab + key + spacer + str(value) + sep)


data = ""
with open('/Users/Chris/PycharmProjects/HaloCoach/Halo5.json', 'r') as f:
    # read_data = f.read()
    lines = f.readlines()
f.closed
for line in lines:
    # print(line)
    if line.replace(' ', '')[:2] != '//':
        data = data + line.replace('null', '""')

data = json.loads(data)

table_name = "test_table"
table = 'CREATE EXTERNAL TABLE IF NOT EXISTS default.{}(\n'.format(table_name)
schema = 'default'

# for item in data:
#   print(item)

for value in recursive_items(data):
    table = table + value.replace('guid', 'string').replace('uint32', 'int') + '\n'

# print (table_def)
table = table.replace(",>", ">")
print(table)
print(serde)



# print(table_def[:-3] + ')' + serde)
# for key,value in data.items():
#    print(value)
