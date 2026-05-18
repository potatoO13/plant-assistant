const api = require('../../utils/api');

const POLL_INTERVAL = 1000;
const POLL_TIMEOUT = 15000;
const TERMINAL_STATUS = ['success', 'failed', 'rejected', 'error', 'timeout'];

function isEmpty(value) {
  return value === null || value === undefined || value === '';
}

function displayValue(value, fallback = '--') {
  return isEmpty(value) ? fallback : String(value);
}

function isNumberLike(value) {
  if (isEmpty(value)) return false;
  return !Number.isNaN(Number(value));
}

function parseDate(value) {
  if (!value) return null;
  const normalText = String(value).replace(/-/g, '/');
  const date = new Date(normalText);
  if (!Number.isNaN(date.getTime())) return date;

  const isoDate = new Date(value);
  return Number.isNaN(isoDate.getTime()) ? null : isoDate;
}

function getFreshStatus(createdAt) {
  const date = parseDate(createdAt);
  if (!date) {
    return { text: '状态未知', className: 'tag-warning' };
  }
  const diff = Date.now() - date.getTime();
  if (diff >= 0 && diff <= 2 * 60 * 1000) {
    return { text: '在线 / 数据正常', className: 'tag-normal' };
  }
  return { text: '数据可能延迟', className: 'tag-warning' };
}

function hasCooldownText(text) {
  if (!text) return false;
  const lower = String(text).toLowerCase();
  return lower.indexOf('cooldown') >= 0 ||
    lower.indexOf('too frequent') >= 0 ||
    lower.indexOf('冷却') >= 0 ||
    lower.indexOf('频繁') >= 0;
}

function getMessageFromValue(value) {
  if (!value) return '';
  if (typeof value === 'string') return value;
  if (Array.isArray(value)) {
    return value.map(getMessageFromValue).filter(Boolean).join('；');
  }
  return value.message || value.msg || getMessageFromValue(value.detail) || value.error || '';
}

function statusText(status, message) {
  if (hasCooldownText(message)) return '操作过于频繁，请稍后再试';
  const map = {
    pending: '指令已发送，等待设备执行',
    success: '浇水完成',
    rejected: '浇水请求被拒绝',
    failed: '浇水失败，请检查设备或网络',
    error: '浇水失败，请检查设备或网络',
    timeout: '设备未及时回传结果',
    unknown: '状态未知'
  };
  return map[status || 'unknown'] || message || '状态未知';
}

function statusClass(status) {
  if (status === 'success') return 'tag-normal';
  if (status === 'failed' || status === 'rejected' || status === 'error' || status === 'timeout') return 'tag-danger';
  return 'tag-warning';
}

function normalizeWateringLogsResponse(res) {
  if (!res) return [];
  if (Array.isArray(res)) return res;

  const candidates = [res.items, res.data, res.records, res.list, res.logs];
  for (let i = 0; i < candidates.length; i += 1) {
    if (Array.isArray(candidates[i])) return candidates[i];
  }

  if (res.data && typeof res.data === 'object') {
    return normalizeWateringLogsResponse(res.data);
  }

  return [];
}

function extractRequestId(res) {
  if (!res) return '';
  const data = res.data && typeof res.data === 'object' ? res.data : {};
  return res.request_id || res.id || res.watering_id || data.request_id || data.id || data.watering_id || '';
}

function extractStatus(res) {
  if (!res) return '';
  const data = res.data && typeof res.data === 'object' ? res.data : {};
  return res.status || data.status || '';
}

function normalizeLogItem(item) {
  const status = item.status || 'unknown';
  const message = getMessageFromValue(item.message || item.detail || item.error);
  return {
    request_id: displayValue(item.request_id || item.id || item.watering_id),
    duration_sec: displayValue(item.duration_sec),
    status,
    statusText: statusText(status, message),
    statusClass: statusClass(status),
    source: displayValue(item.source),
    created_at: displayValue(item.created_at),
    finished_at: displayValue(item.finished_at),
    message: displayValue(message)
  };
}

Page({
  data: {
    durations: [
      { value: 3, label: '少量补水' },
      { value: 5, label: '常规浇水' },
      { value: 10, label: '较多补水' }
    ],
    durationSec: 5,
    buttonText: '一键浇水5秒',
    isSubmitting: false,
    isPolling: false,
    currentRequestId: '',
    currentStatus: 'unknown',
    currentStatusText: '未开始',
    currentStatusClass: 'tag-normal',
    currentMessage: '',
    errorText: '',
    logs: [],
    logsEmptyText: '暂无浇水记录',
    logsLoading: false,
    deviceStatusText: '状态未知',
    deviceStatusClass: 'tag-warning',
    deviceErrorText: '',
    deviceIdText: '--',
    deviceLightText: '--',
    deviceTimeText: '--'
  },

  onLoad() {
    this.pollTimer = null;
    this.pollStartedAt = 0;
    this.activeDev15Test = false;
    this.loadDeviceLatest();
    this.loadWateringLogs();
  },

  onShow() {
    this.loadDeviceLatest();
    this.loadWateringLogs();
  },

  onUnload() {
    this.clearPolling();
  },

  selectDuration(e) {
    if (this.data.isSubmitting || this.data.isPolling) return;
    const durationSec = Number(e.currentTarget.dataset.value);
    this.setData({
      durationSec,
      buttonText: `一键浇水${durationSec}秒`
    });
  },

  manualWatering() {
    this.submitWatering(this.data.durationSec);
  },

  devSend15Sec() {
    console.log('[DEV_TEST_15] sending duration_sec=15');
    this.submitWatering(15, { isDev15: true });
  },

  async submitWatering(durationSec, options = {}) {
    const isDev15 = !!options.isDev15;
    if (this.data.isSubmitting || this.data.isPolling) {
      wx.showToast({ title: '当前指令处理中，请稍后', icon: 'none' });
      return;
    }

    this.clearPolling();
    this.activeDev15Test = isDev15;
    this.setData({
      isSubmitting: true,
      buttonText: '指令发送中...',
      currentRequestId: '',
      currentStatus: 'pending',
      currentStatusText: '指令发送中',
      currentStatusClass: 'tag-warning',
      currentMessage: `请求浇水 ${durationSec} 秒`,
      errorText: ''
    });

    try {
      const result = await api.manualWatering(durationSec);
      if (isDev15) {
        console.log('[DEV_TEST_15] response:', result);
      }
      const requestId = extractRequestId(result);
      const message = getMessageFromValue(result);
      const responseStatus = extractStatus(result) || 'pending';

      if (isDev15 && !requestId) {
        const displayMessage = message || '15秒测试请求已被后端接口拒绝，但后端未生成watering_log记录';
        this.setData({
          isSubmitting: false,
          isPolling: false,
          currentRequestId: '--',
          currentStatus: responseStatus,
          currentStatusText: displayMessage,
          currentStatusClass: statusClass(responseStatus),
          currentMessage: '请后端补充 rejected 日志，便于前端按 request_id 追踪异常闭环。',
          errorText: displayMessage,
          logs: [],
          logsEmptyText: '本次15秒测试未生成watering_log记录',
          buttonText: `一键浇水${this.data.durationSec}秒`
        });
        wx.showToast({ title: displayMessage, icon: 'none' });
        return;
      }

      this.setData({
        isSubmitting: false,
        isPolling: TERMINAL_STATUS.indexOf(responseStatus) < 0,
        currentRequestId: requestId || '--',
        currentStatus: responseStatus,
        currentStatusText: statusText(responseStatus, message),
        currentStatusClass: statusClass(responseStatus),
        currentMessage: message || '已发送浇水指令',
        buttonText: TERMINAL_STATUS.indexOf(responseStatus) < 0 ? '等待设备执行...' : `一键浇水${this.data.durationSec}秒`
      });

      await this.loadWateringLogs(requestId);
      if (TERMINAL_STATUS.indexOf(responseStatus) >= 0) {
        this.finishCurrentStatus(responseStatus, message);
        return;
      }
      this.startPolling(requestId);
    } catch (err) {
      if (isDev15) {
        console.log('[DEV_TEST_15] response:', err && err.response ? err.response : err);
      }
      const response = err && err.response ? err.response : null;
      const requestId = extractRequestId(response);
      const responseStatus = extractStatus(response) || 'rejected';
      const rawMessage = getMessageFromValue(response) || (err && err.message ? err.message : '');
      const noLogMessage = '15秒测试请求已被后端接口拒绝，但后端未生成watering_log记录';
      const message = isDev15 && !requestId ? noLogMessage : (rawMessage || '浇水指令发送失败');

      if (isDev15 && requestId) {
        this.setData({
          isSubmitting: false,
          isPolling: TERMINAL_STATUS.indexOf(responseStatus) < 0,
          currentRequestId: requestId,
          currentStatus: responseStatus,
          currentStatusText: statusText(responseStatus, rawMessage),
          currentStatusClass: statusClass(responseStatus),
          currentMessage: rawMessage || '后端拒绝请求，但已生成异常日志',
          errorText: rawMessage || '',
          logsEmptyText: '暂无浇水记录',
          buttonText: TERMINAL_STATUS.indexOf(responseStatus) < 0 ? '等待设备执行...' : `一键浇水${this.data.durationSec}秒`
        });
        await this.loadWateringLogs(requestId);
        if (TERMINAL_STATUS.indexOf(responseStatus) >= 0) {
          this.finishCurrentStatus(responseStatus, rawMessage);
          return;
        }
        this.startPolling(requestId);
        return;
      }

      this.setData({
        isSubmitting: false,
        isPolling: false,
        currentStatus: isDev15 ? 'rejected' : 'error',
        currentStatusText: isDev15 ? message : statusText('error', message),
        currentStatusClass: 'tag-danger',
        currentRequestId: '--',
        currentMessage: isDev15 ? '请后端补充 rejected 日志，便于前端按 request_id 追踪异常闭环。' : message,
        errorText: message,
        logs: isDev15 ? [] : this.data.logs,
        logsEmptyText: isDev15 ? '本次15秒测试未生成watering_log记录' : this.data.logsEmptyText,
        buttonText: `一键浇水${this.data.durationSec}秒`
      });
      wx.showToast({ title: isDev15 ? message : statusText('error', message), icon: 'none' });
      if (!isDev15) {
        this.loadWateringLogs();
      }
    }
  },

  startPolling(requestId) {
    if (!requestId || requestId === '--') {
      this.setData({
        isSubmitting: false,
        isPolling: false,
        currentStatus: 'rejected',
        currentStatusText: '15秒测试请求已被后端接口拒绝，但后端未生成watering_log记录',
        currentStatusClass: 'tag-danger',
        currentMessage: '没有 request_id，前端不会进入伪轮询状态。',
        buttonText: `一键浇水${this.data.durationSec}秒`
      });
      return;
    }
    this.clearPolling();
    this.pollStartedAt = Date.now();
    this.setData({ isPolling: true });

    const pollOnce = async () => {
      const elapsed = Date.now() - this.pollStartedAt;
      if (elapsed >= POLL_TIMEOUT) {
        this.finishCurrentStatus('timeout', '等待回执超时，请检查设备状态');
        return;
      }

      try {
        const matchedLog = await this.loadWateringLogs(requestId);
        if (matchedLog && TERMINAL_STATUS.indexOf(matchedLog.status) >= 0) {
          this.finishCurrentStatus(matchedLog.status, matchedLog.message);
          return;
        }
        if (matchedLog) {
          this.setData({
            currentStatus: matchedLog.status || 'pending',
            currentStatusText: statusText(matchedLog.status || 'pending', matchedLog.message),
            currentStatusClass: statusClass(matchedLog.status || 'pending'),
            currentMessage: matchedLog.message || '设备执行中',
            buttonText: '等待设备执行...'
          });
        } else {
          this.setData({
            currentStatusText: '已发送，等待日志更新',
            currentStatusClass: 'tag-warning',
            currentMessage: requestId ? `request_id：${requestId}` : '等待后端生成日志',
            buttonText: '等待设备执行...'
          });
        }
      } catch (err) {
        const message = err && err.message ? err.message : '浇水记录刷新失败';
        this.setData({ errorText: message });
      }

      this.pollTimer = setTimeout(pollOnce, POLL_INTERVAL);
    };

    this.pollTimer = setTimeout(pollOnce, POLL_INTERVAL);
  },

  clearPolling() {
    if (this.pollTimer) {
      clearTimeout(this.pollTimer);
      this.pollTimer = null;
    }
  },

  finishCurrentStatus(status, message) {
    this.clearPolling();
    const text = status === 'timeout' && message ? message : statusText(status, message);
    this.setData({
      isSubmitting: false,
      isPolling: false,
      currentStatus: status,
      currentStatusText: text,
      currentStatusClass: statusClass(status),
      currentMessage: message || text,
      buttonText: `一键浇水${this.data.durationSec}秒`
    });
    wx.showToast({ title: text, icon: status === 'success' ? 'success' : 'none' });
    this.loadWateringLogs(this.data.currentRequestId === '--' ? '' : this.data.currentRequestId);
  },

  async loadWateringLogs(requestId = '') {
    this.setData({ logsLoading: true });

    try {
      let raw = null;
      if (requestId) {
        raw = await api.getWateringLogs({ request_id: requestId, limit: 20 });
      } else {
        raw = await api.getWateringLogs({ limit: 10 });
      }

      let list = normalizeWateringLogsResponse(raw);
      let matched = requestId ? list.find((item) => String(item.request_id || item.id || item.watering_id) === String(requestId)) : null;

      if (requestId && !matched) {
        const fallbackRaw = await api.getWateringLogs({ limit: 20 });
        list = normalizeWateringLogsResponse(fallbackRaw);
        matched = list.find((item) => String(item.request_id || item.id || item.watering_id) === String(requestId));
      }

      const logs = this.activeDev15Test && requestId
        ? (matched ? [normalizeLogItem(matched)] : [])
        : list.slice(0, 10).map(normalizeLogItem);
      this.setData({
        logs,
        logsLoading: false,
        logsEmptyText: this.activeDev15Test && requestId ? '本次15秒测试日志尚未出现' : '暂无浇水记录'
      });
      return matched ? normalizeLogItem(matched) : null;
    } catch (err) {
      const message = err && err.message ? err.message : '浇水记录加载失败';
      this.setData({ logsLoading: false, errorText: message });
      return null;
    }
  },

  async refreshLogs() {
    await this.loadWateringLogs(this.data.currentRequestId === '--' ? '' : this.data.currentRequestId);
  },

  async loadDeviceLatest() {
    try {
      const latest = await api.getLatest();
      const createdAt = latest.created_at || latest.timestamp || latest.time || '';
      const status = getFreshStatus(createdAt);
      this.setData({
        deviceIdText: displayValue(latest.device_id),
        deviceLightText: isNumberLike(latest.light) ? `${Math.round(Number(latest.light))} lux` : '--',
        deviceTimeText: displayValue(createdAt),
        deviceStatusText: status.text,
        deviceStatusClass: status.className,
        deviceErrorText: ''
      });
    } catch (err) {
      this.setData({
        deviceStatusText: '设备状态获取失败',
        deviceStatusClass: 'tag-warning',
        deviceErrorText: err && err.message ? err.message : '设备状态获取失败'
      });
    }
  }
});
