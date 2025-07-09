from pyrfc import Connection

conn = Connection(
    user='rfc1',
    password='Uniqus@1234',
    ashost='riseeccdev',      # Sandbox
    sysnr='10',
    client='300',
    lang='EN'
)

# conn = Connection(
#     user='hammad',
#     password='Uniqus@1234',
#     ashost='172.16.200.17',     # Production
#     sysnr='02',
#     client='300',
#     lang='EN'
# )

# result = conn.call(
#     'RFC_READ_TABLE',
#     QUERY_TABLE='KNA1',
#     DELIMITER='|',
#     ROWCOUNT=10,
#     FIELDS=[
#         {'FIELDNAME': 'KUNNR'},
#         {'FIELDNAME': 'NAME1'},
#         {'FIELDNAME': 'ORT01'}
#     ]
# )

result = conn.call('STFC_CONNECTION')
print("Connection Test Result:", result)

# print(result)