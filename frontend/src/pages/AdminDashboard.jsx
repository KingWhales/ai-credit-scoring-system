import { useEffect, useState } from "react";
import { getApplications, submitReview } from "../api";

function AdminDashboard() {
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [reviewingId, setReviewingId] = useState(null);
  const [notes, setNotes] = useState("");

  const loadApplications = async () => {
    setLoading(true);
    try {
      const response = await getApplications();
      setApplications(response.data);
      setError(null);
    } catch (err) {
      setError("Could not load applications. Is the backend running?");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadApplications();
  }, []);

  const handleReview = async (applicationId, decision) => {
    try {
      await submitReview(applicationId, {
        reviewer_name: "Admin",
        decision,
        notes,
      });
      setReviewingId(null);
      setNotes("");
      loadApplications();
    } catch (err) {
      alert("Failed to submit review");
    }
  };

  const riskLabel = (probability) => {
    if (probability == null) return "No prediction";
    if (probability < 0.2) return "Low risk";
    if (probability < 0.5) return "Medium risk";
    return "High risk";
  };

  const riskColor = (probability) => {
    if (probability == null) return "#999";
    if (probability < 0.2) return "green";
    if (probability < 0.5) return "orange";
    return "red";
  };

  if (loading) return <p style={{ padding: "2rem" }}>Loading applications...</p>;
  if (error) return <p style={{ padding: "2rem", color: "red" }}>{error}</p>;

  return (
    <div style={{ maxWidth: 900, margin: "0 auto", padding: "2rem" }}>
      <h1>Admin Dashboard</h1>
      <p>{applications.length} application(s)</p>

      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr style={{ borderBottom: "2px solid #ccc", textAlign: "left" }}>
            <th>Submitted</th>
            <th>Income</th>
            <th>Credit</th>
            <th>Risk</th>
            <th>Status</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          {applications.map((app) => (
            <tr key={app.id} style={{ borderBottom: "1px solid #eee" }}>
              <td>{new Date(app.submitted_at).toLocaleDateString()}</td>
              <td>{app.amt_income_total ?? "-"}</td>
              <td>{app.amt_credit ?? "-"}</td>
              <td style={{ color: riskColor(app.prediction?.default_probability) }}>
                {riskLabel(app.prediction?.default_probability)}
                {app.prediction &&
                  ` (${(app.prediction.default_probability * 100).toFixed(1)}%)`}
              </td>
              <td>{app.status}</td>
              <td>
                {app.status === "pending" ? (
                  reviewingId === app.id ? (
                    <div>
                      <textarea
                        placeholder="Notes"
                        value={notes}
                        onChange={(e) => setNotes(e.target.value)}
                        rows={2}
                        style={{ display: "block", marginBottom: "0.5rem" }}
                      />
                      <button onClick={() => handleReview(app.id, "approved")}>
                        Approve
                      </button>
                      <button onClick={() => handleReview(app.id, "rejected")}>
                        Reject
                      </button>
                      <button onClick={() => setReviewingId(null)}>Cancel</button>
                    </div>
                  ) : (
                    <button onClick={() => setReviewingId(app.id)}>Review</button>
                  )
                ) : (
                  <em>Reviewed</em>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default AdminDashboard;

