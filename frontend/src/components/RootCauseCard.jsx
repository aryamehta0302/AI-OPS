const RootCauseCard = ({ rootCause }) => {
  if (!rootCause) return null;

  if (rootCause.root_cause === "INSUFFICIENT_DATA") {
    return (
      <div className="card">
        <h3>Root Cause</h3>
        <p>Learning baseline…</p>
      </div>
    );
  }

  return (
    <div className="card">
      <h3>Root Cause</h3>
      <div className="value">{rootCause.root_cause}</div>
      <p>Confidence: <b>{Math.round(rootCause.confidence * 100)}%</b></p>
    </div>
  );
};

export default RootCauseCard;
