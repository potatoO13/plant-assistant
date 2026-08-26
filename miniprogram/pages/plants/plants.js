const api = require('../../utils/api');

function normalizePlant(plant) {
  if (!plant) return {};
  return {
    ...plant,
    alias: plant.alias || '',
    soil_min: plant.soil_min !== undefined ? plant.soil_min : plant.soil_moisture_min,
    soil_max: plant.soil_max !== undefined ? plant.soil_max : plant.soil_moisture_max,
    care_tips: plant.care_tips || plant.care_advice || '',
    common_problems: plant.common_problems || '',
    light_desc: plant.light_desc || ''
  };
}

Page({
  data: {
    keyword: '',
    plantList: [],
    selectedPlant: {}
  },

  onLoad() {
    this.search();
  },

  onKeywordInput(e) {
    this.setData({ keyword: e.detail.value });
  },

  async search() {
    try {
      wx.showLoading({ title: '搜索中' });
      const list = await api.searchPlants(this.data.keyword);
      const rawList = Array.isArray(list) ? list : (list.items || list.results || []);
      const plantList = rawList.map(normalizePlant);
      this.setData({ plantList });
      if (plantList.length) {
        await this.loadPlantDetail(plantList[0].id || plantList[0].plant_id);
      } else {
        this.setData({ selectedPlant: {} });
      }
    } catch (err) {
      console.error(err);
      wx.showToast({ title: '搜索失败', icon: 'none' });
    } finally {
      wx.hideLoading();
    }
  },

  async selectPlant(e) {
    const id = e.currentTarget.dataset.id;
    await this.loadPlantDetail(id);
  },

  async loadPlantDetail(id) {
    if (!id) return;
    try {
      const detail = await api.getPlantDetail(id);
      this.setData({ selectedPlant: normalizePlant(detail) });
    } catch (err) {
      console.error(err);
      wx.showToast({ title: '详情加载失败', icon: 'none' });
    }
  }
});
