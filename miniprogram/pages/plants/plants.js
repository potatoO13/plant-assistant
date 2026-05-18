const api = require('../../utils/api');

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
      const plantList = Array.isArray(list) ? list : (list.items || list.results || []);
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
      this.setData({ selectedPlant: detail || {} });
    } catch (err) {
      console.error(err);
      wx.showToast({ title: '详情加载失败', icon: 'none' });
    }
  }
});
