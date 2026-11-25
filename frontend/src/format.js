export const formatMoney = (value) =>
  new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR" }).format(value || 0);

export const percentUsed = (budget) => Math.min((budget.spent / budget.amount) * 100, 100);

export const totalsBy = (rows, key) => {
  const totals = {};
  for (const row of rows) totals[row[key]] = (totals[row[key]] || 0) + row.total;
  return Object.entries(totals)
    .map(([label, total]) => ({ label, total }))
    .sort((a, b) => b.total - a.total);
};
// ADD these to the bottom of frontend/src/format.js

// ₹12,000 instead of ₹12,000.00 (keeps paise only when they exist)
export const formatRupees = (value) =>
  new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  }).format(value || 0);

const toDate = (value) => {
  const [year, month, day] = String(value).slice(0, 10).split("-").map(Number);
  return new Date(year, month - 1, day);
};

// "9 Aug 2026"
export const formatDate = (value) =>
  toDate(value).toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" });

// "Today", "Yesterday", or "Sunday, 9 Aug"
export const dayLabel = (value) => {
  const date = toDate(value);
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const diff = Math.round((today - date) / 86400000);
  if (diff === 0) return "Today";
  if (diff === 1) return "Yesterday";
  return date.toLocaleDateString("en-GB", { weekday: "long", day: "numeric", month: "short" });
};
