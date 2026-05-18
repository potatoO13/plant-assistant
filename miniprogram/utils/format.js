function pad(num) {
  return num < 10 ? `0${num}` : `${num}`;
}

function formatTime(value) {
  if (!value) return '--';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return `${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

function formatNumber(value, digits = 1) {
  if (value === null || value === undefined || value === '') return '--';
  const num = Number(value);
  if (Number.isNaN(num)) return '--';
  return num.toFixed(digits);
}

function normalizeResponse(res) {
  if (!res) return res;
  if (res.data && res.data.data !== undefined) return res.data.data;
  if (res.data !== undefined) return res.data;
  return res;
}

function statusText(status) {
  const map = {
    online: '在线',
    offline: '离线',
    normal: '正常',
    warning: '提醒',
    danger: '异常',
    pending: '执行中',
    success: '成功',
    failed: '失败'
  };
  return map[status] || status || '--';
}

function statusClass(status) {
  if (status === 'danger' || status === 'offline' || status === 'failed') return 'tag-danger';
  if (status === 'warning' || status === 'pending') return 'tag-warning';
  return 'tag-normal';
}

module.exports = {
  formatTime,
  formatNumber,
  normalizeResponse,
  statusText,
  statusClass
};
