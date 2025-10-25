import React, { useState, useEffect } from 'react';
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

// API base URL
const API_BASE = 'http://localhost:8000/api/v1';

// Color scheme
const COLORS = ['#A080FF', '#8B6FFF', '#FF6B6B', '#4ECDC4', '#FFE66D'];

const Dashboard = () => {
  const [sources, setSources] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      // Fetch sources
      const sourcesRes = await fetch(`${API_BASE}/sources`);
      const sourcesData = await sourcesRes.json();
      setSources(sourcesData);

      // Mock stats for demo
      setStats({
        totalSources: sourcesData.length,
        totalAnalyses: 1247,
        trendsDetected: 23,
        alertsGenerated: 5
      });

      setLoading(false);
    } catch (error) {
      console.error('Error fetching data:', error);
      setLoading(false);
    }
  };

  // Mock data for charts
  const sentimentData = [
    { name: 'Positive', value: 45 },
    { name: 'Neutral', value: 35 },
    { name: 'Negative', value: 20 }
  ];

  const activityData = [
    { date: 'Mon', commits: 45, issues: 12, prs: 8 },
    { date: 'Tue', commits: 52, issues: 15, prs: 10 },
    { date: 'Wed', commits: 38, issues: 8, prs: 6 },
    { date: 'Thu', commits: 61, issues: 18, prs: 12 },
    { date: 'Fri', commits: 48, issues: 11, prs: 9 },
    { date: 'Sat', commits: 23, issues: 4, prs: 3 },
    { date: 'Sun', commits: 15, issues: 2, prs: 1 }
  ];

  const trendsData = [
    { topic: 'Security Updates', mentions: 45 },
    { topic: 'Bug Fixes', mentions: 38 },
    { topic: 'New Features', mentions: 32 },
    { topic: 'Documentation', mentions: 28 },
    { topic: 'Performance', mentions: 25 }
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-900">
        <div className="text-white text-2xl">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
          OSInt-AI Dashboard
        </h1>
        <p className="text-gray-400">Open Source Intelligence Analyzer</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <StatCard title="Data Sources" value={stats?.totalSources || 0} icon="📊" />
        <StatCard title="Total Analyses" value={stats?.totalAnalyses || 0} icon="🔍" />
        <StatCard title="Trends Detected" value={stats?.trendsDetected || 0} icon="📈" />
        <StatCard title="Alerts" value={stats?.alertsGenerated || 0} icon="🔔" />
      </div>

      {/* Charts Row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Activity Chart */}
        <div className="bg-gray-800 rounded-lg p-6 shadow-xl">
          <h2 className="text-xl font-semibold mb-4">Weekly Activity</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={activityData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="date" stroke="#9CA3AF" />
              <YAxis stroke="#9CA3AF" />
              <Tooltip 
                contentStyle={{ backgroundColor: '#1F2937', border: 'none', borderRadius: '8px' }}
                labelStyle={{ color: '#F3F4F6' }}
              />
              <Legend />
              <Bar dataKey="commits" fill="#A080FF" />
              <Bar dataKey="issues" fill="#8B6FFF" />
              <Bar dataKey="prs" fill="#FF6B6B" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Sentiment Distribution */}
        <div className="bg-gray-800 rounded-lg p-6 shadow-xl">
          <h2 className="text-xl font-semibold mb-4">Sentiment Distribution</h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={sentimentData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {sentimentData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip 
                contentStyle={{ backgroundColor: '#1F2937', border: 'none', borderRadius: '8px' }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Trends and Sources Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Trends */}
        <div className="bg-gray-800 rounded-lg p-6 shadow-xl">
          <h2 className="text-xl font-semibold mb-4">Top Trending Topics</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={trendsData} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis type="number" stroke="#9CA3AF" />
              <YAxis dataKey="topic" type="category" stroke="#9CA3AF" width={120} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#1F2937', border: 'none', borderRadius: '8px' }}
                labelStyle={{ color: '#F3F4F6' }}
              />
              <Bar dataKey="mentions" fill="#4ECDC4" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Data Sources */}
        <div className="bg-gray-800 rounded-lg p-6 shadow-xl">
          <h2 className="text-xl font-semibold mb-4">Active Data Sources</h2>
          <div className="space-y-4 max-h-80 overflow-y-auto">
            {sources.length > 0 ? (
              sources.map((source) => (
                <div key={source.id} className="bg-gray-700 rounded-lg p-4">
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="font-medium">{source.name}</h3>
                    <span className={`px-2 py-1 text-xs rounded ${source.enabled ? 'bg-green-600' : 'bg-red-600'}`}>
                      {source.enabled ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                  <p className="text-sm text-gray-400">Type: {source.source_type}</p>
                  <p className="text-xs text-gray-500 mt-1">
                    Check interval: {source.check_interval}s
                  </p>
                </div>
              ))
            ) : (
              <div className="text-center py-8 text-gray-400">
                <p>No data sources configured</p>
                <button className="mt-4 px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg transition">
                  Add Data Source
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

const StatCard = ({ title, value, icon }) => (
  <div className="bg-gray-800 rounded-lg p-6 shadow-xl hover:shadow-2xl transition-shadow">
    <div className="flex items-center justify-between">
      <div>
        <p className="text-gray-400 text-sm mb-1">{title}</p>
        <p className="text-3xl font-bold">{value}</p>
      </div>
      <div className="text-4xl">{icon}</div>
    </div>
  </div>
);

export default Dashboard;
