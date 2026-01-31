import {
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  Area,
  AreaChart
} from "recharts";
import { motion } from "framer-motion";

const MetricsChart = ({ title, data, dataKey, color }) => {
  // Custom tooltip - tech style
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div style={{
          background: "rgba(10, 14, 23, 0.95)",
          border: `1px solid ${color}40`,
          borderRadius: "4px",
          padding: "10px 14px",
          boxShadow: "0 4px 20px rgba(0, 0, 0, 0.5)"
        }}>
          <p style={{ 
            color: "#64748b", 
            fontSize: "10px", 
            margin: "0 0 4px 0",
            letterSpacing: "1px"
          }}>
            {label}
          </p>
          <p style={{ 
            color: color, 
            fontSize: "18px", 
            fontWeight: 700, 
            margin: 0,
            letterSpacing: "1px"
          }}>
            {payload[0].value.toFixed(1)}%
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <motion.div 
      className="card"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      <h3>{title}</h3>
      {data.length === 0 ? (
        <div className="loading">
          <div className="loading-spinner"></div>
          AWAITING DATA...
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={280}>
          <AreaChart data={data}>
            <defs>
              <linearGradient id={`gradient-${dataKey}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={color} stopOpacity={0.25} />
                <stop offset="100%" stopColor={color} stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid 
              strokeDasharray="3 3" 
              stroke="rgba(255, 255, 255, 0.05)" 
              vertical={false}
            />
            <XAxis 
              dataKey="time" 
              tick={{ fill: "#64748b", fontSize: 10, letterSpacing: "0.5px" }}
              tickLine={{ stroke: "rgba(255, 255, 255, 0.05)" }}
              axisLine={{ stroke: "rgba(255, 255, 255, 0.1)" }}
            />
            <YAxis 
              domain={[0, 100]} 
              tick={{ fill: "#64748b", fontSize: 10 }}
              tickLine={{ stroke: "rgba(255, 255, 255, 0.05)" }}
              axisLine={{ stroke: "rgba(255, 255, 255, 0.1)" }}
              tickFormatter={(value) => `${value}%`}
            />
            <Tooltip content={<CustomTooltip />} />
            <Area
              type="monotone"
              dataKey={dataKey}
              stroke={color}
              strokeWidth={2}
              fill={`url(#gradient-${dataKey})`}
              dot={false}
              activeDot={{ r: 4, fill: color, stroke: "#0a0e17", strokeWidth: 2 }}
              isAnimationActive={true}
              animationDuration={500}
              animationEasing="ease-out"
            />
          </AreaChart>
        </ResponsiveContainer>
      )}
    </motion.div>
  );
};

export default MetricsChart;
