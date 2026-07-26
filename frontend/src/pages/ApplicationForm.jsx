import { useState } from "react";
import { submitApplication } from "../api";

const initialFormState = {
  applicant: { full_name: "", email: "", phone: "" },
  amt_income_total: "",
  amt_credit: "",
  amt_annuity: "",
  amt_goods_price: "",
  days_employed: "",
  name_education_type: "Higher education",
  name_family_status: "Married",
  name_income_type: "Working",
  flag_own_car: "N",
  flag_own_realty: "N",
  cnt_children: 0,
  ext_source_1: "",
  ext_source_2: "",
  ext_source_3: "",
};

function ApplicationForm() {
  const [form, setForm] = useState(initialFormState);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    if (name.startsWith("applicant.")) {
      const field = name.split(".")[1];
      setForm((prev) => ({
        ...prev,
        applicant: { ...prev.applicant, [field]: value },
      }));
    } else {
      setForm((prev) => ({ ...prev, [name]: value }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    setResult(null);

    // Convert numeric fields, drop empty strings so backend/ML service
    // treats them as missing rather than invalid
    const payload = {
      ...form,
      amt_income_total: form.amt_income_total ? Number(form.amt_income_total) : null,
      amt_credit: form.amt_credit ? Number(form.amt_credit) : null,
      amt_annuity: form.amt_annuity ? Number(form.amt_annuity) : null,
      amt_goods_price: form.amt_goods_price ? Number(form.amt_goods_price) : null,
      days_employed: form.days_employed ? Number(form.days_employed) : null,
      cnt_children: Number(form.cnt_children),
      ext_source_1: form.ext_source_1 ? Number(form.ext_source_1) : null,
      ext_source_2: form.ext_source_2 ? Number(form.ext_source_2) : null,
      ext_source_3: form.ext_source_3 ? Number(form.ext_source_3) : null,
    };

    try {
      const response = await submitApplication(payload);
      setResult(response.data);
    } catch (err) {
      setError(
        err.response?.data?.detail
          ? JSON.stringify(err.response.data.detail)
          : "Something went wrong submitting your application."
      );
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div style={{ maxWidth: 600, margin: "0 auto", padding: "2rem" }}>
      <h1>Loan Application</h1>

      <form onSubmit={handleSubmit}>
        <fieldset>
          <legend>Applicant Details</legend>
          <label>
            Full Name
            <input
              name="applicant.full_name"
              value={form.applicant.full_name}
              onChange={handleChange}
              required
            />
          </label>
          <label>
            Email
            <input
              type="email"
              name="applicant.email"
              value={form.applicant.email}
              onChange={handleChange}
              required
            />
          </label>
          <label>
            Phone
            <input
              name="applicant.phone"
              value={form.applicant.phone}
              onChange={handleChange}
            />
          </label>
        </fieldset>

        <fieldset>
          <legend>Financial Information</legend>
          <label>
            Total Income
            <input
              type="number"
              name="amt_income_total"
              value={form.amt_income_total}
              onChange={handleChange}
            />
          </label>
          <label>
            Loan Amount Requested
            <input
              type="number"
              name="amt_credit"
              value={form.amt_credit}
              onChange={handleChange}
            />
          </label>
          <label>
            Annuity
            <input
              type="number"
              name="amt_annuity"
              value={form.amt_annuity}
              onChange={handleChange}
            />
          </label>
          <label>
            Goods Price
            <input
              type="number"
              name="amt_goods_price"
              value={form.amt_goods_price}
              onChange={handleChange}
            />
          </label>
          <label>
            Days Employed (negative number)
            <input
              type="number"
              name="days_employed"
              value={form.days_employed}
              onChange={handleChange}
            />
          </label>
        </fieldset>

        <fieldset>
          <legend>Demographics</legend>
          <label>
            Education
            <select
              name="name_education_type"
              value={form.name_education_type}
              onChange={handleChange}
            >
              <option>Secondary / secondary special</option>
              <option>Higher education</option>
              <option>Incomplete higher</option>
              <option>Lower secondary</option>
            </select>
          </label>
          <label>
            Family Status
            <select
              name="name_family_status"
              value={form.name_family_status}
              onChange={handleChange}
            >
              <option>Married</option>
              <option>Single / not married</option>
              <option>Civil marriage</option>
              <option>Widow</option>
            </select>
          </label>
          <label>
            Own Car
            <select
              name="flag_own_car"
              value={form.flag_own_car}
              onChange={handleChange}
            >
              <option value="Y">Yes</option>
              <option value="N">No</option>
            </select>
          </label>
          <label>
            Own Realty
            <select
              name="flag_own_realty"
              value={form.flag_own_realty}
              onChange={handleChange}
            >
              <option value="Y">Yes</option>
              <option value="N">No</option>
            </select>
          </label>
          <label>
            Number of Children
            <input
              type="number"
              name="cnt_children"
              value={form.cnt_children}
              onChange={handleChange}
              min="0"
            />
          </label>
        </fieldset>

        <button type="submit" disabled={submitting}>
          {submitting ? "Submitting..." : "Submit Application"}
        </button>
      </form>

      {error && (
        <div style={{ color: "red", marginTop: "1rem" }}>Error: {error}</div>
      )}

      {result && (
        <div style={{ marginTop: "1rem", padding: "1rem", border: "1px solid #ccc" }}>
          <h3>Application Submitted</h3>
          <p>Application ID: {result.id}</p>
          <p>Status: {result.status}</p>
          {result.prediction && (
            <p>
              Predicted Default Probability:{" "}
              {(result.prediction.default_probability * 100).toFixed(1)}%
            </p>
          )}
        </div>
      )}
    </div>
  );
}

export default ApplicationForm;

