import json
import boto3

tab = '\t'

serde = ' \n) ROW FORMAT SERDE \'org.openx.data.jsonserde.JsonSerDe\' \
WITH SERDEPROPERTIES ( \
  \'serialization.format\' = \'1\' \
) LOCATION \'s3://private.halocoach.com/data/\' '

valid_type_list = ['INT', 'STRING']


def exec_athena_query(query):
    client = boto3.client('athena')
    response = client.start_query_execution(
        QueryString=query,
        # ClientRequestToken='string',
        # QueryExecutionContext={
        #    'Database': 'string'
        # },
        ResultConfiguration={
            'OutputLocation': 's3://private.halocoach.com/results',
            'EncryptionConfiguration': {
                'EncryptionOption': 'SSE_S3'  # | 'SSE_KMS' | 'CSE_KMS',
                # 'KmsKey': 'string'
            }
        }
    )


# builds a map of json nodes and how "deep" they go; important for making sure
# we don't add an extra row delimiter where we don't need one
def define_node_count(obj, node_dict, node):
    for key, value in obj.items():
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
                    yield (level * tab + key + spacer + 'array<' + value[0] + '>' + sep)
                
            except:
                pass  # print("error in list")
        else:
            field_data_type = ""
            if isinstance(value, int):
                field_data_type = "int"
                # yield (level * tab + key + spacer + "int" + sep)
            else:
                field_data_type = "string"
                # yield (level * '\t' + key + spacer + str(value) + ",")
                # yield (level * tab + key + spacer + str(value) + sep)
            yield (level * tab + key + spacer + field_data_type + sep)


data = ""

fileName = '/Users/Chris/PycharmProjects/athenaTableGenerator/sampleJsonDocs/halo5_matchResult.json'
# fileName = '/Users/Chris/PycharmProjects/athenaTableGenerator/sampleJsonDocs/docs_complex_example.json'
#fileName = 'C:\\Users\\cpollard\\Desktop\\athenaGenerator\\athenaTableGenerator\\sampleJsonDocs\\halo5_matchResult.json'
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

table_name = "halo5_matchresult"
table_schema = "default"
table = 'CREATE EXTERNAL TABLE IF NOT EXISTS {}.{}(\n'.format(table_schema,table_name)
schema = 'default'

# for item in data:
#   print(item)


node_dict = {}
define_node_count(data,node_dict,'root')

for value in recursive_items(data):
    table = table + value + '\n'

# print (table_def)
#table = table.replace(",>", ">")

table = table + serde
print(table)

exec_athena_query(table)

# print(table_def[:-3] + ')' + serde)
# for key,value in data.items():
#    print(value)
