def generate_advice(sensor_data, plant):
    advices = []
    status = "ok"

    if sensor_data.soil_moisture < plant.soil_moisture_min:
        status = "warning"
        advices.append(f"土壤湿度偏低，当前 {sensor_data.soil_moisture:.1f}%，建议适量浇水。")
    elif sensor_data.soil_moisture > plant.soil_moisture_max:
        status = "warning"
        advices.append(f"土壤湿度偏高，当前 {sensor_data.soil_moisture:.1f}%，建议暂停浇水并加强通风。")
    else:
        advices.append(f"土壤湿度适宜，当前 {sensor_data.soil_moisture:.1f}%。")

    if sensor_data.temperature < plant.temp_min:
        status = "warning"
        advices.append(f"温度偏低，当前 {sensor_data.temperature:.1f}°C，建议移到更温暖的位置。")
    elif sensor_data.temperature > plant.temp_max:
        status = "warning"
        advices.append(f"温度偏高，当前 {sensor_data.temperature:.1f}°C，建议遮阴或降温。")

    if sensor_data.light < plant.light_min:
        status = "warning"
        advices.append(f"光照偏弱，当前 {sensor_data.light:.0f} lx，建议增加散射光。")
    elif sensor_data.light > plant.light_max:
        status = "warning"
        advices.append(f"光照偏强，当前 {sensor_data.light:.0f} lx，建议避免暴晒。")

    summary = "当前环境基本适宜。" if status == "ok" else "当前环境有需要关注的项目。"
    return {"status": status, "summary": summary, "advices": advices}
