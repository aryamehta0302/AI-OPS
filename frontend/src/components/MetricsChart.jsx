import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer
} from "recharts";

const MetricsChart = ({ data, dataKey, color, title }) => {
  return (
    <div style={{ width: "100%", height: 250 }}>
      <h3>{title}</h3>
      <ResponsiveContainer>
        <LineChart data={data}>
          <XAxis dataKey="time" />
          <YAxis />
          <Tooltip />
          <Line type="monotone" dataKey={dataKey} stroke={color} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default MetricsChart;
