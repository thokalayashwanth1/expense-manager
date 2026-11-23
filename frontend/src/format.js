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
