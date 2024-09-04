import base64

base64_message = b'HWID:10:42'
data = base64.b64encode(base64_message)
print(data.decode("utf-8"))
