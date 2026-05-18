function nowISO(offsetMinutes = 0) {
  const date = new Date(Date.now() + offsetMinutes * 60 * 1000);
  return date.toISOString();
}

function buildHistory(range = 'day') {
  const count = range === 'week' ? 7 : 12;
  const labels = [];
  const temperature = [];
  const soil = [];
  const light = [];
  for (let i = 0; i < count; i += 1) {
    if (range === 'week') {
      labels.push(`周${i + 1}`);
      temperature.push(Number((22 + Math.sin(i / 1.5) * 2 + i * 0.12).toFixed(1)));
      soil.push(Math.max(26, Math.round(48 - i * 1.5 + Math.cos(i) * 4)));
      light.push(Math.round(760 + Math.sin(i) * 220 + i * 35));
    } else {
      labels.push(`${String(8 + i).padStart(2, '0')}:00`);
      temperature.push(Number((21.5 + Math.sin(i / 2) * 3).toFixed(1)));
      soil.push(Math.max(24, Math.round(52 - i * 1.8 + Math.cos(i / 2) * 3)));
      light.push(Math.max(80, Math.round(300 + Math.sin(i / 2) * 520 + i * 38)));
    }
  }
  return {
    range,
    labels,
    series: {
      temperature,
      soil_moisture: soil,
      light
    },
    items: labels.map((label, index) => ({
      time: label,
      temperature: temperature[index],
      soil_moisture: soil[index],
      light: light[index]
    }))
  };
}

const plantList = [
  {
    id: 1,
    name: '绿萝',
    alias: '黄金葛、魔鬼藤',
    temp_min: 18,
    temp_max: 28,
    soil_min: 35,
    soil_max: 70,
    light_min: 300,
    light_max: 2500,
    light_desc: '明亮散射光，避免夏季强直射',
    watering_advice: '保持盆土微湿，表层土变干后再补水。',
    care_tips: '适合室内养护，注意通风，冬季减少浇水。',
    common_problems: '叶片发黄多与积水、低温或光照不足有关。'
  },
  {
    id: 2,
    name: '多肉',
    alias: '景天科多肉植物',
    temp_min: 15,
    temp_max: 30,
    soil_min: 20,
    soil_max: 45,
    light_min: 1200,
    light_max: 6000,
    light_desc: '需要充足光照，夏季高温适当遮阴',
    watering_advice: '遵循干透浇透，避免长期潮湿。',
    care_tips: '使用透气颗粒土，保持通风，雨季减少浇水。',
    common_problems: '徒长通常与光照不足有关，黑腐通常与积水有关。'
  },
  {
    id: 3,
    name: '薄荷',
    alias: '留兰香、香草植物',
    temp_min: 15,
    temp_max: 28,
    soil_min: 45,
    soil_max: 80,
    light_min: 800,
    light_max: 5000,
    light_desc: '喜光，可接受半日照',
    watering_advice: '生长期需水较多，土壤偏干时及时浇水。',
    care_tips: '定期修剪可促进分枝，避免盆土长期积水。',
    common_problems: '叶片萎蔫多与缺水或强光暴晒有关。'
  }
];

function latest() {
  return {
    plant_id: 1,
    plant_name: '绿萝',
    device_id: 'device001',
    device_status: 'online',
    temperature: 27.2,
    air_humidity: 58.6,
    soil_moisture: 28.5,
    light: 245,
    created_at: nowISO(-1)
  };
}

function wateringLogs() {
  return [
    { id: 3, request_id: 'water_mock_003', duration_sec: 5, source: 'manual', status: 'success', created_at: nowISO(-15), finished_at: nowISO(-15) },
    { id: 2, request_id: 'water_mock_002', duration_sec: 3, source: 'manual', status: 'success', created_at: nowISO(-120), finished_at: nowISO(-120) },
    { id: 1, request_id: 'water_mock_001', duration_sec: 5, source: 'manual', status: 'success', created_at: nowISO(-480), finished_at: nowISO(-480) }
  ];
}

function advice() {
  return {
    status: 'warning',
    summary: '当前绿萝存在土壤偏干、光照偏弱两项提醒。建议先补水并移动到明亮散射光位置。',
    advices: [
      {
        type: 'soil_moisture',
        severity: 'warning',
        title: '土壤偏干',
        text: '当前土壤湿度低于绿萝适宜范围，建议浇水3-5秒后观察盆底是否积水。',
        suggest_watering: true
      },
      {
        type: 'light',
        severity: 'warning',
        title: '光照不足',
        text: '当前光照强度较低，建议将植物移动到靠窗但无强烈直射的位置。',
        suggest_watering: false
      }
    ]
  };
}

function searchPlants(keyword = '') {
  const kw = keyword.trim();
  if (!kw) return plantList;
  return plantList.filter((item) => item.name.indexOf(kw) >= 0 || item.alias.indexOf(kw) >= 0);
}

function plantDetail(id) {
  return plantList.find((item) => String(item.id) === String(id)) || plantList[0];
}

function mockRequest(path, data = {}) {
  if (path.includes('/api/health')) return { status: 'ok', time: nowISO() };
  if (path.includes('/api/device/latest')) return latest();
  if (path.includes('/api/device/history')) return buildHistory(data.range || 'day');
  if (path.includes('/api/watering/manual')) {
    const duration = Number(data.duration_sec || 5);
    return {
      request_id: `water_mock_${Date.now()}`,
      status: 'pending',
      message: `已下发${duration}秒浇水指令`,
      duration_sec: duration
    };
  }
  if (path.includes('/api/watering/logs')) return wateringLogs();
  if (path.includes('/api/plants/search')) return searchPlants(data.keyword || '');
  if (path.includes('/api/plants/')) {
    const id = path.split('/').pop();
    return plantDetail(id);
  }
  if (path.includes('/api/advice/current')) return advice();
  return {};
}

module.exports = {
  mockRequest
};
