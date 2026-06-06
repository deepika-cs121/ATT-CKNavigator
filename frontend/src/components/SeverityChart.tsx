import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Cell } from 'recharts';

interface SeverityChartProps {
  findings: Array<{ severity: string }>;
}

export const SeverityChart = ({ findings }: SeverityChartProps) => {
  const severityCounts = findings.reduce(
    (acc, finding) => {
      acc[finding.severity] = (acc[finding.severity] || 0) + 1;
      return acc;
    },
    {} as Record<string, number>
  );

  const data = [
    { name: 'Critical', count: severityCounts['Critical'] || 0, color: '#ef4444' },
    { name: 'High', count: severityCounts['High'] || 0, color: '#f97316' },
    { name: 'Medium', count: severityCounts['Medium'] || 0, color: '#eab308' },
    { name: 'Low', count: severityCounts['Low'] || 0, color: '#22c55e' },
  ];

  return (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
          <XAxis
            dataKey="name"
            stroke="#6b7280"
            style={{ fontSize: '12px', fill: '#9ca3af' }}
          />
          <YAxis stroke="#6b7280" style={{ fontSize: '12px', fill: '#9ca3af' }} />
          <Bar dataKey="count" radius={[8, 8, 0, 0]}>
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} opacity={0.8} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};