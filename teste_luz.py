import tinytuya

DEVICE_ID = "bfcda6fc99ef575ce9byxu"
IP = "192.168.1.70"
LOCAL_KEY = "v4TA0[}GqOwMdA;5"

d = tinytuya.Device(DEVICE_ID, IP, LOCAL_KEY)
d.set_version(3.5)

print("STATUS:")
print(d.status())

print("DESLIGAR:")
print(d.set_status(False, 20))

print("LIGAR:")
print(d.set_status(True, 20))