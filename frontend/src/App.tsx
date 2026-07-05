import React, { useState, useEffect } from 'react';
import { Activity, GitCommit, Users, Clock, TrendingDown, Download, Printer, Upload, Database, AlertTriangle, BarChart3, Search } from 'lucide-react';
import ReactECharts from 'echarts-for-react';
import { KPIResponse, TrendResponse, CodeStats, HeatmapResponse, MemberRadar, AnomalyReport, FilterState, RepositoryConfig, SyncResult } from './types';
import { statsApi, mockApi, exportApi, commitApi, syncApi } from './services/api';
import './index.css';

const formatNumber = (n: number) => n.toLocaleString();
const getDateRange = (days: number) => {
  const end = new Date();
  const start = new Date();
  start.setDate(end.getDate() - days);
  return { start: start.toISOString().split('T')[0], end: end.toISOString().split('T')[0] };
};

function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);
  useEffect(() => {
    const timer = setTimeout(() => setDebouncedValue(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);
  return debouncedValue;
}

// ========== Header ==========
const Header: React.FC = () => (
  <header className="bg-slate-800 border-b border-slate-700/50 sticky top-0 z-50">
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <div className="bg-blue-600 p-2 rounded-lg">
          <Activity className="w-5 h-5 text-white" />
        </div>
        <h1 className="text-xl font-bold text-slate-100">CodePulse</h1>
        <span className="text-xs text-slate-400 bg-slate-700 px-2 py-0.5 rounded-full">研发活跃度智能分析平台</span>
      </div>
      <div className="flex items-center gap-3 no-print">
        <button onClick={() => window.print()} className="btn-secondary">
          <Printer className="w-4 h-4" />
          打印报表
        </button>
      </div>
    </div>
  </header>
);

// ========== ControlPanel ==========
interface ControlPanelProps {
  filters: FilterState;
  setFilters: React.Dispatch<React.SetStateAction<FilterState>>;
  onGenerateMock: () => void;
  onImport: () => void;
  onRepoManage: () => void;
  loading: boolean;
}

const ControlPanel: React.FC<ControlPanelProps> = ({ filters, setFilters, onGenerateMock, onImport, onRepoManage, loading }) => {
  const presets = [
    { label: '最近7天', days: 7 },
    { label: '最近30天', days: 30 },
    { label: '本季度', days: 90 },
  ];

  const applyPreset = (days: number) => {
    const range = getDateRange(days);
    setFilters(prev => ({ ...prev, startDate: range.start, endDate: range.end }));
  };

  return (
    <div className="card no-print mb-6">
      <div className="card-body">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-[1fr_1.2fr_0.8fr_1fr] gap-4">
          <div className="space-y-2">
            <label className="text-sm text-slate-400">快速筛选</label>
            <div className="flex gap-2">
              {presets.map(p => (
                <button key={p.days} onClick={() => applyPreset(p.days)} className="btn-secondary text-xs py-1.5">
                  {p.label}
                </button>
              ))}
            </div>
          </div>
          <div className="space-y-2">
            <label className="text-sm text-slate-400">日期范围</label>
            <div className="flex gap-2 items-center min-w-0">
              <input type="date" className="input text-sm py-1.5 flex-1 min-w-[150px]" value={filters.startDate} onChange={e => setFilters(prev => ({ ...prev, startDate: e.target.value }))} />
              <span className="text-slate-500 shrink-0">~</span>
              <input type="date" className="input text-sm py-1.5 flex-1 min-w-[150px]" value={filters.endDate} onChange={e => setFilters(prev => ({ ...prev, endDate: e.target.value }))} />
            </div>
          </div>
          <div className="space-y-2">
            <label className="text-sm text-slate-400">搜索</label>
            <div className="relative">
              <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
              <input type="text" className="input text-sm py-1.5 pl-9 w-full max-w-[220px]" placeholder="成员或 Commit Message..." value={filters.search} onChange={e => setFilters(prev => ({ ...prev, search: e.target.value }))} />
            </div>
          </div>
          <div className="space-y-2">
            <label className="text-sm text-slate-400">数据操作</label>
            <div className="flex gap-2">
              <button onClick={onGenerateMock} disabled={loading} className="btn-primary text-sm py-1.5">
                <Database className="w-4 h-4" />
                {loading ? '生成中...' : '生成模拟数据'}
              </button>
              <button onClick={onImport} className="btn-secondary text-sm py-1.5">
                <Upload className="w-4 h-4" />
                导入
              </button>
            </div>
              <button onClick={onRepoManage} className="btn-secondary text-sm py-1.5">
                <GitCommit className="w-4 h-4" />
                仓库管理
              </button>
          </div>
        </div>
      </div>
    </div>
  );
};

// ========== KPICards ==========
const KPICards: React.FC<{ data: KPIResponse | null }> = ({ data }) => {
  if (!data) return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      {[1, 2, 3, 4].map(i => <div key={i} className="card h-28 animate-pulse" />)}
    </div>
  );

  const items = [
    { icon: GitCommit, label: '总提交次数', value: formatNumber(data.total_commits), color: 'text-blue-400' },
    { icon: BarChart3, label: '净增代码行数', value: formatNumber(data.net_lines), color: 'text-emerald-400' },
    { icon: Users, label: '活跃开发者', value: formatNumber(data.active_developers), color: 'text-purple-400' },
    { icon: Clock, label: '平均评审响应', value: `${data.avg_review_response_hours}h`, color: 'text-amber-400' },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      {items.map((item, idx) => (
        <div key={idx} className="card p-5 flex items-center gap-4">
          <div className="p-3 bg-slate-700/50 rounded-lg">
            <item.icon className={`w-6 h-6 ${item.color}`} />
          </div>
          <div>
            <p className="text-sm text-slate-400">{item.label}</p>
            <p className="text-2xl font-bold text-slate-100">{item.value}</p>
          </div>
        </div>
      ))}
    </div>
  );
};

// ========== TrendChart ==========
const TrendChart: React.FC<{ data: TrendResponse | null }> = ({ data }) => {
  if (!data) return <div className="card h-80 animate-pulse" />;

  const option = {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis' },
    legend: { data: ['提交次数', '新增行数', '删除行数'], textStyle: { color: '#94a3b8' } },
    grid: { left: '3%', right: '4%', bottom: '10%', top: '15%', containLabel: true },
    xAxis: {
      type: 'category',
      data: data.data.map(d => d.date.slice(5)),
      axisLine: { lineStyle: { color: '#475569' } },
      axisLabel: { color: '#94a3b8' }
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: '#334155' } },
      axisLabel: { color: '#94a3b8' }
    },
    series: [
      {
        name: '提交次数',
        type: 'line',
        data: data.data.map(d => d.count),
        smooth: true,
        itemStyle: { color: '#3b82f6' },
        areaStyle: { color: 'rgba(59, 130, 246, 0.15)' },
        markLine: data.has_decline ? {
          data: [{ type: 'average', name: '平均值' }],
          lineStyle: { color: '#ef4444', type: 'dashed' }
        } : undefined
      },
      {
        name: '新增行数',
        type: 'line',
        data: data.data.map(d => d.additions),
        smooth: true,
        itemStyle: { color: '#10b981' }
      },
      {
        name: '删除行数',
        type: 'line',
        data: data.data.map(d => d.deletions),
        smooth: true,
        itemStyle: { color: '#ef4444' }
      }
    ]
  };

  return (
    <div className="card mb-6">
      <div className="card-header">
        <div>
          <h3 className="text-lg font-semibold text-slate-100">提交频率趋势</h3>
          <p className="text-sm text-slate-400">X轴为日期，Y轴为提交次数 / 代码行数</p>
        </div>
        {data.has_decline && (
          <div className="flex items-center gap-2 text-red-400 bg-red-400/10 px-3 py-1 rounded-full text-sm">
            <TrendingDown className="w-4 h-4" />
            检测到活跃度下降
          </div>
        )}
      </div>
      <div className="card-body">
        <ReactECharts option={option} style={{ height: 320 }} />
      </div>
    </div>
  );
};

// ========== CodeStatsChart ==========
const CodeStatsChart: React.FC<{ data: CodeStats[] | null }> = ({ data }) => {
  if (!data) return <div className="card h-80 animate-pulse" />;

  const sorted = [...data].sort((a, b) => b.net - a.net).slice(0, 15);

  const option = {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { data: ['新增行数', '删除行数', '净增行数'], textStyle: { color: '#94a3b8' } },
    grid: { left: '3%', right: '4%', bottom: '5%', top: '10%', containLabel: true },
    xAxis: {
      type: 'category',
      data: sorted.map(d => d.author),
      axisLine: { lineStyle: { color: '#475569' } },
      axisLabel: { color: '#94a3b8', rotate: 30, fontSize: 10 }
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: '#334155' } },
      axisLabel: { color: '#94a3b8' }
    },
    series: [
      {
        name: '新增行数',
        type: 'bar',
        stack: 'total',
        data: sorted.map(d => d.additions),
        itemStyle: { color: '#10b981' }
      },
      {
        name: '删除行数',
        type: 'bar',
        stack: 'total',
        data: sorted.map(d => -d.deletions),
        itemStyle: { color: '#ef4444' }
      },
      {
        name: '净增行数',
        type: 'bar',
        data: sorted.map(d => d.net),
        itemStyle: { color: '#3b82f6' }
      }
    ]
  };

  return (
    <div className="card mb-6">
      <div className="card-header">
        <div>
          <h3 className="text-lg font-semibold text-slate-100">代码量构成分析</h3>
          <p className="text-sm text-slate-400">新增 vs 删除 vs 净增行数（TOP 15 成员）</p>
        </div>
      </div>
      <div className="card-body">
        <ReactECharts option={option} style={{ height: 320 }} />
      </div>
    </div>
  );
};

// ========== HeatmapChart ==========
const HeatmapChart: React.FC<{ data: HeatmapResponse | null }> = ({ data }) => {
  if (!data) return <div className="card h-80 animate-pulse" />;

  const days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'];
  const hours = Array.from({ length: 24 }, (_, i) => `${i}时`);

  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      position: 'top',
      formatter: (params: any) => `${days[params.value[1]]} ${params.value[0]}:00<br/>提交次数: ${params.value[2]}`
    },
    grid: { left: '10%', right: '5%', top: '5%', bottom: '15%' },
    xAxis: {
      type: 'category',
      data: hours,
      splitArea: { show: true, areaStyle: { color: ['transparent'] } },
      axisLine: { lineStyle: { color: '#475569' } },
      axisLabel: { color: '#94a3b8', fontSize: 10 }
    },
    yAxis: {
      type: 'category',
      data: days,
      splitArea: { show: true },
      axisLine: { lineStyle: { color: '#475569' } },
      axisLabel: { color: '#94a3b8' }
    },
    visualMap: {
      min: 0,
      max: data.max_count,
      calculable: true,
      orient: 'horizontal',
      left: 'center',
      bottom: '0%',
      inRange: { color: ['#1e293b', '#3b82f6', '#8b5cf6', '#ef4444'] },
      textStyle: { color: '#94a3b8' }
    },
    series: [{
      name: '提交密度',
      type: 'heatmap',
      data: data.data.map(d => [d.hour, d.day, d.count]),
      label: { show: false },
      itemStyle: {
        borderColor: '#1e293b',
        borderWidth: 2
      }
    }]
  };

  return (
    <div className="card mb-6">
      <div className="card-header">
        <div>
          <h3 className="text-lg font-semibold text-slate-100">提交时段热力图</h3>
          <p className="text-sm text-slate-400">X轴为小时，Y轴为星期，颜色深浅代表提交密度</p>
        </div>
        {data.anomalies.length > 0 && (
          <div className="flex items-center gap-2 text-amber-400 bg-amber-400/10 px-3 py-1 rounded-full text-sm">
            <AlertTriangle className="w-4 h-4" />
            发现 {data.anomalies.length} 处异常
          </div>
        )}
      </div>
      <div className="card-body">
        <ReactECharts option={option} style={{ height: 360 }} />
        {data.anomalies.length > 0 && (
          <div className="mt-4 space-y-2">
            <p className="text-sm font-semibold text-slate-300">异常标记：</p>
            {data.anomalies.slice(0, 5).map((a, i) => (
              <div key={i} className="text-sm text-slate-400 bg-slate-700/50 px-3 py-2 rounded">
                {a.description}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

// ========== RadarChart ==========
const RadarChart: React.FC<{ data: MemberRadar[] | null }> = ({ data }) => {
  if (!data) return <div className="card h-80 animate-pulse" />;

  const topMembers = data.slice(0, 5);
  const dimensions = topMembers[0]?.dimensions.map(d => d.dimension) || [];
  const colors = ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ef4444'];

  const option = {
    backgroundColor: 'transparent',
    tooltip: {},
    legend: { data: topMembers.map(m => m.author), textStyle: { color: '#94a3b8' }, bottom: 0 },
    radar: {
      indicator: dimensions.map(d => ({ name: d, max: 100 })),
      axisLine: { lineStyle: { color: '#475569' } },
      splitLine: { lineStyle: { color: '#334155' } },
      splitArea: { areaStyle: { color: ['transparent'] } },
      axisName: { color: '#94a3b8' }
    },
    series: [{
      type: 'radar',
      data: topMembers.map((m, idx) => ({
        value: m.dimensions.map(d => d.value),
        name: m.author,
        itemStyle: { color: colors[idx % colors.length] },
        areaStyle: { opacity: 0.2 }
      }))
    }]
  };

  return (
    <div className="card mb-6">
      <div className="card-header">
        <div>
          <h3 className="text-lg font-semibold text-slate-100">评审参与度雷达图</h3>
          <p className="text-sm text-slate-400">评论数量、参与率、响应速度、代码贡献、提交频率</p>
        </div>
      </div>
      <div className="card-body">
        <ReactECharts option={option} style={{ height: 400 }} />
      </div>
    </div>
  );
};

// ========== MemberTable ==========
const MemberTable: React.FC<{ data: CodeStats[] | null; onExport: () => void }> = ({ data, onExport }) => {
  if (!data) return <div className="card h-80 animate-pulse" />;

  const sorted = [...data].sort((a, b) => b.commits - a.commits);

  const isAnomaly = (item: CodeStats) => {
    if (item.deletions > 1000 && item.additions < 100) return 'high';
    if (item.deletions > item.additions * 2) return 'medium';
    return null;
  };

  return (
    <div className="card mb-6">
      <div className="card-header">
        <div>
          <h3 className="text-lg font-semibold text-slate-100">成员详细报表</h3>
          <p className="text-sm text-slate-400">提交数、代码行数、评审指标</p>
        </div>
        <button onClick={onExport} className="btn-primary text-sm py-1.5 no-print">
          <Download className="w-4 h-4" />
          导出 CSV
        </button>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-slate-700/30">
            <tr>
              <th className="table-header">成员</th>
              <th className="table-header">提交数</th>
              <th className="table-header">新增行数</th>
              <th className="table-header">删除行数</th>
              <th className="table-header">净增行数</th>
              <th className="table-header">状态</th>
            </tr>
          </thead>
          <tbody>
            {sorted.map((item, idx) => {
              const anomaly = isAnomaly(item);
              return (
                <tr key={idx} className="table-row">
                  <td className="table-cell font-medium text-slate-100">{item.author}</td>
                  <td className="table-cell">{item.commits}</td>
                  <td className="table-cell text-emerald-400">+{formatNumber(item.additions)}</td>
                  <td className="table-cell text-red-400">-{formatNumber(item.deletions)}</td>
                  <td className={`table-cell font-medium ${item.net >= 0 ? 'text-blue-400' : 'text-red-400'}`}>
                    {item.net > 0 ? '+' : ''}{formatNumber(item.net)}
                  </td>
                  <td className="table-cell">
                    {anomaly === 'high' && (
                      <span className="inline-flex items-center gap-1 text-red-400 bg-red-400/10 px-2 py-0.5 rounded text-xs">
                        <AlertTriangle className="w-3 h-3" />大文件删除
                      </span>
                    )}
                    {anomaly === 'medium' && (
                      <span className="inline-flex items-center gap-1 text-amber-400 bg-amber-400/10 px-2 py-0.5 rounded text-xs">
                        <AlertTriangle className="w-3 h-3" />删除异常
                      </span>
                    )}
                    {!anomaly && <span className="text-emerald-400 text-xs">正常</span>}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};

// ========== AnomalyTable ==========
const AnomalyTable: React.FC<{ data: AnomalyReport[] | null }> = ({ data }) => {
  if (!data || data.length === 0) return null;

  const severityColor = {
    low: 'text-emerald-400 bg-emerald-400/10',
    medium: 'text-amber-400 bg-amber-400/10',
    high: 'text-red-400 bg-red-400/10'
  };

  return (
    <div className="card mb-6">
      <div className="card-header">
        <div>
          <h3 className="text-lg font-semibold text-slate-100">异常检测报告</h3>
          <p className="text-sm text-slate-400">自动识别的异常模式</p>
        </div>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-slate-700/30">
            <tr>
              <th className="table-header">成员</th>
              <th className="table-header">异常类型</th>
              <th className="table-header">描述</th>
              <th className="table-header">严重程度</th>
            </tr>
          </thead>
          <tbody>
            {data.map((item, idx) => (
              <tr key={idx} className="table-row">
                <td className="table-cell font-medium text-slate-100">{item.author}</td>
                <td className="table-cell">{item.anomaly_type}</td>
                <td className="table-cell max-w-md">{item.description}</td>
                <td className="table-cell">
                  <span className={`inline-block px-2 py-0.5 rounded text-xs ${severityColor[item.severity]}`}>
                    {item.severity === 'high' ? '高' : item.severity === 'medium' ? '中' : '低'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

// ========== ImportModal ==========
const ImportModal: React.FC<{ open: boolean; onClose: () => void; onSuccess: () => void }> = ({ open, onClose, onSuccess }) => {
  const [file, setFile] = useState<File | null>(null);
  const [jsonText, setJsonText] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  if (!open) return null;

  const handleFileUpload = async () => {
    if (!file) {
      alert('请先选择文件再进行上传');
      return;
    }
    setLoading(true);
    try {
      const res = await commitApi.uploadGitLog(file);
      onSuccess();
      alert(`上传成功：${res.data.message || 'Git Log 文件已导入'}`);
      onClose();
    } catch (e: any) {
      setError(e.response?.data?.detail || '上传失败');
    } finally {
      setLoading(false);
    }
  };

  const normalizeCommit = (item: any): any => {
    if (!item || typeof item !== 'object') return null;

    // 支持嵌套结构（如 GitHub API 的 commit.commit.author）
    const commit = item.commit || item;
    const stats = item.stats || item;

    const hash = item.commit_hash || item.hash || item.sha || commit.sha || commit.hash || commit.id || '';
    const author = commit.author_name || commit.author?.name || commit.author || item.author || item.name || item.committer || 'Unknown';
    const email = commit.author_email || commit.author?.email || item.email || null;
    const message = commit.message || commit.subject || commit.title || item.message || item.msg || item.title || '';
    const dateRaw = commit.date || commit.committed_at || commit.created_at || item.date || item.datetime || item.timestamp || new Date().toISOString();
    const additions = Number(commit.additions || stats.additions || stats.insertions || item.additions || item.insertions || 0);
    const deletions = Number(commit.deletions || stats.deletions || stats.removals || item.deletions || item.removals || 0);
    const files_changed = Number(commit.files_changed || stats.total || stats.files || item.files_changed || item.files || item.changed_files || 0);
    const review_comments_count = Number(item.review_comments_count || item.comments || 0);
    const is_automated = Boolean(item.is_automated || item.automated || false);
    const repository = item.repository || item.repo || item.project || null;
    const branch = item.branch || item.ref || null;

    let date: string;
    if (typeof dateRaw === 'number') {
      date = new Date(dateRaw).toISOString();
    } else {
      const d = new Date(dateRaw);
      if (isNaN(d.getTime())) {
        date = new Date().toISOString();
      } else {
        date = d.toISOString();
      }
    }

    return {
      commit_hash: hash,
      author,
      email,
      date,
      message,
      additions,
      deletions,
      files_changed,
      review_comments_count,
      is_automated,
      repository,
      branch,
    };
  };

  const handleJsonUpload = async () => {
    if (!jsonText.trim()) {
      alert('请先输入Git Log JSON 数据再进行导入JSON数据');
      return;
    }
    setLoading(true);
    try {
      const parsed = JSON.parse(jsonText);
      // 支持被包裹在常见字段中的数据（如 { commits: [...] }）
      let rawData = parsed;
      if (parsed && typeof parsed === 'object' && !Array.isArray(parsed)) {
        rawData = parsed.commits || parsed.data || parsed.items || parsed.results || parsed;
      }
      const rawCommits = Array.isArray(rawData) ? rawData : [rawData];
      const commits = rawCommits.map(normalizeCommit).filter(Boolean);
      if (commits.length === 0) {
        setError('未能解析到有效的提交记录，请检查 JSON 格式');
        setLoading(false);
        return;
      }
      const res = await commitApi.uploadJson(commits);
      onSuccess();
      alert(res.data.message || `导入成功：${res.data.count} 条提交记录已导入`);
      onClose();
    } catch (e: any) {
      setError(e.message || '解析失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="card w-full max-w-lg mx-4">
        <div className="card-header">
          <h3 className="text-lg font-semibold">导入数据</h3>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-200">✕</button>
        </div>
        <div className="card-body space-y-4">
          <div className="space-y-2">
            <label className="text-sm text-slate-400">上传 Git Log 文件</label>
            <input type="file" accept=".txt,.log,.csv" onChange={e => setFile(e.target.files?.[0] || null)} className="input w-full text-sm" />
            <button onClick={handleFileUpload} disabled={loading} className="btn-primary w-full justify-center">
              {loading ? '上传中...' : '上传文件'}
            </button>
          </div>
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-slate-600" />
            </div>
            <div className="relative flex justify-center text-xs">
              <span className="bg-slate-800 px-2 text-slate-400">或粘贴 JSON 数据</span>
            </div>
          </div>
          <div className="space-y-2">
            <textarea value={jsonText} onChange={e => setJsonText(e.target.value)} className="input w-full h-32 text-sm font-mono" placeholder={`[{"commit_hash": "abc...", "author": "张三", "date": "2024-01-01T00:00:00", "additions": 100, "deletions": 20}]`} />
            <button onClick={handleJsonUpload} disabled={loading} className="btn-primary w-full justify-center">
              {loading ? '导入中...' : '导入 JSON'}
            </button>
          </div>
          {error && <p className="text-red-400 text-sm">{error}</p>}
        </div>
      </div>
    </div>
  );
};

// ========== RepositoryConfigModal ==========
const RepositoryConfigModal: React.FC<{ open: boolean; onClose: () => void; onSuccess: () => void }> = ({ open, onClose, onSuccess }) => {
  const [configs, setConfigs] = useState<RepositoryConfig[]>([]);
  const [loading, setLoading] = useState(false);
  const [syncLoading, setSyncLoading] = useState<number | null>(null);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState<Partial<RepositoryConfig>>({
    name: '',
    repo_type: 'local',
    local_path: '',
    remote_url: '',
    access_token: '',
    branch: 'main',
    is_active: true,
    auto_sync: false,
  });
  const [editingId, setEditingId] = useState<number | null>(null);

  useEffect(() => {
    if (open) fetchConfigs();
  }, [open]);

  const fetchConfigs = async () => {
    try {
      const res = await syncApi.getConfigs();
      setConfigs(res.data.data || []);
    } catch (e) {
      console.error('获取仓库配置失败', e);
    }
  };

  const handleSubmit = async () => {
    if (!formData.name) {
      setError('请输入仓库名称');
      return;
    }
    if (formData.repo_type === 'local' && !formData.local_path) {
      setError('本地仓库必须提供路径');
      return;
    }
    if (formData.repo_type !== 'local' && (!formData.remote_url || !formData.access_token)) {
      setError('远程仓库必须提供URL和Access Token');
      return;
    }

    setLoading(true);
    setError('');
    try {
      if (editingId) {
        await syncApi.updateConfig(editingId, formData);
      } else {
        await syncApi.createConfig(formData);
      }
      setFormData({
        name: '',
        repo_type: 'local',
        local_path: '',
        remote_url: '',
        access_token: '',
        branch: 'main',
        is_active: true,
        auto_sync: false,
      });
      setEditingId(null);
      await fetchConfigs();
    } catch (e: any) {
      setError(e.response?.data?.detail || '保存失败');
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (config: RepositoryConfig) => {
    setFormData({
      name: config.name,
      repo_type: config.repo_type,
      local_path: config.local_path || '',
      remote_url: config.remote_url || '',
      access_token: config.access_token || '',
      branch: config.branch || 'main',
      is_active: config.is_active,
      auto_sync: config.auto_sync,
    });
    setEditingId(config.id);
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('确定删除此仓库配置？')) return;
    try {
      await syncApi.deleteConfig(id);
      await fetchConfigs();
    } catch (e) {
      console.error('删除失败', e);
    }
  };

  const handleSync = async (id: number) => {
    setSyncLoading(id);
    try {
      const res = await syncApi.syncRepo(id, 90, true);
      const result: SyncResult = res.data;
      if (result.success) {
        alert(`同步成功！导入 ${result.imported_count} 条提交记录`);
        onSuccess();
      } else {
        alert(`同步失败: ${result.message}`);
      }
    } catch (e: any) {
      alert(`同步失败: ${e.response?.data?.detail || e.message}`);
    } finally {
      setSyncLoading(null);
    }
  };

  const handleSyncAll = async () => {
    setSyncLoading(-1);
    try {
      const res = await syncApi.syncAll(90);
      const results = res.data.results || [];
      const successCount = results.filter((r: any) => r.success).length;
      alert(`同步完成！成功 ${successCount}/${results.length} 个仓库`);
      onSuccess();
    } catch (e: any) {
      alert(`同步失败: ${e.response?.data?.detail || e.message}`);
    } finally {
      setSyncLoading(null);
    }
  };

  const handleCancelEdit = () => {
    setEditingId(null);
    setFormData({
      name: '',
      repo_type: 'local',
      local_path: '',
      remote_url: '',
      access_token: '',
      branch: 'main',
      is_active: true,
      auto_sync: false,
    });
    setError('');
  };

  if (!open) return null;

  const repoTypeLabel = { local: '本地仓库', github: 'GitHub', gitlab: 'GitLab' };

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm overflow-y-auto py-8">
      <div className="card w-full max-w-2xl mx-4 my-auto">
        <div className="card-header">
          <div>
            <h3 className="text-lg font-semibold">Git 仓库管理</h3>
            <p className="text-sm text-slate-400">配置本地或远程 Git 仓库，自动同步提交数据</p>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-200">✕</button>
        </div>
        <div className="card-body space-y-6">
          {/* 添加/编辑表单 */}
          <div className="space-y-4 border border-slate-700 rounded-lg p-4">
            <h4 className="text-sm font-semibold text-slate-300">{editingId ? '编辑仓库' : '添加仓库'}</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-sm text-slate-400">仓库名称</label>
                <input type="text" className="input w-full text-sm" placeholder="例如: my-project" value={formData.name} onChange={e => setFormData(prev => ({ ...prev, name: e.target.value }))} />
              </div>
              <div className="space-y-2">
                <label className="text-sm text-slate-400">仓库类型</label>
                <select className="input w-full text-sm" value={formData.repo_type} onChange={e => setFormData(prev => ({ ...prev, repo_type: e.target.value as any }))}>
                  <option value="local">本地仓库</option>
                  <option value="github">GitHub</option>
                  <option value="gitlab">GitLab</option>
                </select>
              </div>
              {formData.repo_type === 'local' ? (
                <div className="space-y-2 md:col-span-2">
                  <label className="text-sm text-slate-400">本地路径</label>
                  <input type="text" className="input w-full text-sm font-mono" placeholder="例如: E:/projects/my-project" value={formData.local_path} onChange={e => setFormData(prev => ({ ...prev, local_path: e.target.value }))} />
                </div>
              ) : (
                <>
                  <div className="space-y-2 md:col-span-2">
                    <label className="text-sm text-slate-400">仓库 URL</label>
                    <input type="text" className="input w-full text-sm" placeholder="例如: https://github.com/owner/repo" value={formData.remote_url} onChange={e => setFormData(prev => ({ ...prev, remote_url: e.target.value }))} />
                  </div>
                  <div className="space-y-2 md:col-span-2">
                    <label className="text-sm text-slate-400">Access Token</label>
                    <input type="password" className="input w-full text-sm font-mono" placeholder="ghp_... 或 glpat-..." value={formData.access_token} onChange={e => setFormData(prev => ({ ...prev, access_token: e.target.value }))} />
                  </div>
                </>
              )}
              <div className="space-y-2">
                <label className="text-sm text-slate-400">分支</label>
                <input type="text" className="input w-full text-sm" placeholder="main" value={formData.branch} onChange={e => setFormData(prev => ({ ...prev, branch: e.target.value }))} />
              </div>
              <div className="flex items-center gap-4 pt-6">
                <label className="flex items-center gap-2 text-sm text-slate-400 cursor-pointer">
                  <input type="checkbox" checked={formData.is_active} onChange={e => setFormData(prev => ({ ...prev, is_active: e.target.checked }))} />
                  激活
                </label>
                <label className="flex items-center gap-2 text-sm text-slate-400 cursor-pointer">
                  <input type="checkbox" checked={formData.auto_sync} onChange={e => setFormData(prev => ({ ...prev, auto_sync: e.target.checked }))} />
                  自动同步
                </label>
              </div>
            </div>
            {error && <p className="text-red-400 text-sm">{error}</p>}
            <div className="flex gap-2">
              <button onClick={handleSubmit} disabled={loading} className="btn-primary text-sm">
                {loading ? '保存中...' : (editingId ? '更新' : '添加')}
              </button>
              {editingId && (
                <button onClick={handleCancelEdit} className="btn-secondary text-sm">
                  取消编辑
                </button>
              )}
            </div>
          </div>

          {/* 仓库列表 */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h4 className="text-sm font-semibold text-slate-300">已配置仓库</h4>
              {configs.length > 0 && (
                <button onClick={handleSyncAll} disabled={syncLoading === -1} className="btn-primary text-xs py-1.5">
                  {syncLoading === -1 ? '同步中...' : '同步全部'}
                </button>
              )}
            </div>
            {configs.length === 0 ? (
              <p className="text-sm text-slate-500 text-center py-4">暂无仓库配置，请添加本地或远程 Git 仓库</p>
            ) : (
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {configs.map(config => (
                  <div key={config.id} className="flex items-center justify-between p-3 bg-slate-700/30 rounded-lg">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium text-slate-100">{config.name}</span>
                        <span className="text-xs bg-slate-600 px-1.5 py-0.5 rounded text-slate-300">{repoTypeLabel[config.repo_type]}</span>
                        {config.is_active ? (
                          <span className="text-xs bg-emerald-500/20 text-emerald-400 px-1.5 py-0.5 rounded">已激活</span>
                        ) : (
                          <span className="text-xs bg-slate-600 text-slate-400 px-1.5 py-0.5 rounded">已停用</span>
                        )}
                      </div>
                      <p className="text-xs text-slate-400 font-mono">
                        {config.repo_type === 'local' ? config.local_path : config.remote_url}
                      </p>
                      <p className="text-xs text-slate-500">
                        分支: {config.branch || 'main'} | 上次同步: {config.last_sync_at ? new Date(config.last_sync_at).toLocaleString() : '从未'}
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      <button onClick={() => handleSync(config.id)} disabled={syncLoading === config.id} className="btn-primary text-xs py-1.5">
                        {syncLoading === config.id ? '同步中' : '同步'}
                      </button>
                      <button onClick={() => handleEdit(config)} className="btn-secondary text-xs py-1.5">
                        编辑
                      </button>
                      <button onClick={() => handleDelete(config.id)} className="text-red-400 hover:text-red-300 text-xs px-2 py-1.5">
                        删除
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

// ========== App ==========
function App() {
  const [filters, setFilters] = useState<FilterState>(() => {
    const range = getDateRange(30);
    return { startDate: range.start, endDate: range.end, authors: [], repositories: [], search: '' };
  });
  const [kpi, setKpi] = useState<KPIResponse | null>(null);
  const [trend, setTrend] = useState<TrendResponse | null>(null);
  const [codeStats, setCodeStats] = useState<CodeStats[] | null>(null);
  const [heatmap, setHeatmap] = useState<HeatmapResponse | null>(null);
  const [radar, setRadar] = useState<MemberRadar[] | null>(null);
  const [anomalies, setAnomalies] = useState<AnomalyReport[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [importOpen, setImportOpen] = useState(false);
  const [repoConfigOpen, setRepoConfigOpen] = useState(false);
  const debouncedSearch = useDebounce(filters.search, 200);

  const fetchData = async () => {
    setLoading(true);
    const params = {
      start_date: filters.startDate ? new Date(filters.startDate).toISOString() : undefined,
      end_date: filters.endDate ? new Date(filters.endDate + 'T23:59:59').toISOString() : undefined,
      authors: filters.authors.length ? filters.authors : undefined,
      search: debouncedSearch || undefined,
    };

    try {
      const [kpiRes, trendRes, codeRes, heatRes, radarRes, anomalyRes] = await Promise.all([
        statsApi.getKPI(params),
        statsApi.getTrend(params),
        statsApi.getCodeStats(params),
        statsApi.getHeatmap(params),
        statsApi.getRadar(params),
        statsApi.getAnomalies(params),
      ]);
      setKpi(kpiRes.data);
      setTrend(trendRes.data);
      setCodeStats(codeRes.data);
      setHeatmap(heatRes.data);
      setRadar(radarRes.data);
      setAnomalies(anomalyRes.data);
    } catch (e) {
      console.error('数据加载失败', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [filters.startDate, filters.endDate, filters.authors.join(','), debouncedSearch]);

  const handleGenerateMock = async () => {
    setLoading(true);
    try {
      await mockApi.generate();
      await fetchData();
    } catch (e) {
      console.error('模拟数据生成失败', e);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async () => {
    const params = {
      start_date: filters.startDate,
      end_date: filters.endDate,
    };
    try {
      const res = await exportApi.exportMemberCSV(params);
      const blob = new Blob([res.data], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `codepulse_members_${filters.startDate}_${filters.endDate}.csv`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (e) {
      console.error('导出失败', e);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900">
      <Header />
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <ControlPanel
          filters={filters}
          setFilters={setFilters}
          onGenerateMock={handleGenerateMock}
          onImport={() => setImportOpen(true)}
          onRepoManage={() => setRepoConfigOpen(true)}
          loading={loading}
        />

        <KPICards data={kpi} />

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="lg:col-span-2">
            <TrendChart data={trend} />
          </div>
          <div className="lg:col-span-2">
            <CodeStatsChart data={codeStats} />
          </div>
          <div>
            <HeatmapChart data={heatmap} />
          </div>
          <div>
            <RadarChart data={radar} />
          </div>
        </div>

        <AnomalyTable data={anomalies} />
        <MemberTable data={codeStats} onExport={handleExport} />
      </main>

      <ImportModal open={importOpen} onClose={() => setImportOpen(false)} onSuccess={fetchData} />
      <RepositoryConfigModal open={repoConfigOpen} onClose={() => setRepoConfigOpen(false)} onSuccess={fetchData} />

      <footer className="border-t border-slate-700/50 py-6 mt-8">
        <p className="text-center text-sm text-slate-500">
          CodePulse - 研发活跃度智能分析平台
        </p>
      </footer>
    </div>
  );
}

export default App;
