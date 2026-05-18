Component({
  properties: {
    canvasId: {
      type: String,
      value: 'ec-canvas'
    }
  },
  data: {
    width: 0,
    height: 0
  },
  lifetimes: {
    ready() {
      this.createSelectorQuery()
        .select(`#${this.properties.canvasId}`)
        .boundingClientRect((rect) => {
          if (rect) {
            this.setData({ width: rect.width, height: rect.height });
          }
        })
        .exec();
    }
  },
  methods: {
    init(callback) {
      const canvasId = this.properties.canvasId;
      const query = this.createSelectorQuery();
      query.select(`#${canvasId}`).boundingClientRect((rect) => {
        const width = rect && rect.width ? rect.width : 320;
        const height = rect && rect.height ? rect.height : 260;
        const dpr = wx.getSystemInfoSync().pixelRatio || 1;
        const ctx = wx.createCanvasContext(canvasId, this);
        const canvas = { ctx, width, height, canvasId, component: this };
        this.chart = callback(canvas, width, height, dpr);
      }).exec();
    },
    touchStart(e) {
      if (this.chart && this.chart.dispatchAction) {
        this.chart.dispatchAction({ type: 'touchstart', event: e });
      }
    },
    touchMove(e) {
      if (this.chart && this.chart.dispatchAction) {
        this.chart.dispatchAction({ type: 'touchmove', event: e });
      }
    },
    touchEnd(e) {
      if (this.chart && this.chart.dispatchAction) {
        this.chart.dispatchAction({ type: 'touchend', event: e });
      }
    }
  }
});
