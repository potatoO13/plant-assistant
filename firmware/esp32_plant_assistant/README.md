# ESP32 Firmware Placeholder

当前固件是硬件到货前的占位框架，`readSensors()` 会返回模拟数据。

后续替换位置：

- AHT20 或 DHT22：替换温度、空气湿度读取
- BH1750：替换光照读取
- 土壤湿度传感器：替换土壤湿度读取
- 继电器控制水泵：确认引脚后替换 `RELAY_PIN`

安全限制：

- 启动时继电器默认关闭
- 单次浇水最长 10 秒
- MQTT 控制 Topic：`plant/device001/control`
- MQTT 确认 Topic：`plant/device001/control_ack`
