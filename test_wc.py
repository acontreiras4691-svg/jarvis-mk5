from smart_home.tuya_light import TuyaLight

light = TuyaLight(
    device_id="bfcdaf6c99ef575ce9byxu",
    ip="192.168.1.70",
    local_key="v4TA0[}GqOwMdA;5",
    version=3.5,
)

print(light.status())
print(light.ligar())