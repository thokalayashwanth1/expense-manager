// Picks an emoji + a soft colour for any category name.
// Order matters: the first rule that matches wins, so specific words go first.
const ICON_RULES = [
  [["uncategor"], "❓"],
  [["delivery", "zomato", "swiggy"], "🍕"],
  [["grocer", "vegetable", "fruit", "supermarket"], "🛒"],
  [["food", "lunch", "dinner", "breakfast", "meal", "restaurant", "snack", "cafe", "coffee", "tea"], "🍽️"],
  [["rent", "house", "home", "mortgage", "maintenance"], "🏠"],
  [["transport", "travel", "petrol", "fuel", "cab", "taxi", "auto", "bus", "metro", "train", "flight"], "🚌"],
  [["fitness", "gym", "sport", "yoga"], "💪"],
  [["shop", "cloth", "fashion", "amazon", "flipkart"], "🛍️"],
  [["bill", "electric", "water", "gas", "internet", "wifi", "recharge", "phone", "mobile"], "💡"],
  [["health", "medic", "doctor", "pharma", "hospital"], "💊"],
  [["education", "school", "tuition", "course", "book", "fees"], "📚"],
  [["entertain", "movie", "game", "netflix", "music", "fun"], "🎬"],
  [["pocket", "allowance"], "👛"],
  [["saving", "invest", "sip", "deposit"], "🏦"],
  [["gift", "donat", "charity"], "🎁"],
  [["insurance", "emi", "loan", "tax"], "🧾"],
  [["pet"], "🐾"],
];

// Static class names so Tailwind keeps them in the build.
const TONES = [
  "bg-orange-50 text-orange-700",
  "bg-blue-50 text-blue-700",
  "bg-green-50 text-green-700",
  "bg-purple-50 text-purple-700",
  "bg-pink-50 text-pink-700",
  "bg-yellow-50 text-yellow-800",
  "bg-teal-50 text-teal-700",
  "bg-red-50 text-red-700",
];

export const categoryIcon = (name = "") => {
  const key = name.toLowerCase();
  const rule = ICON_RULES.find(([words]) => words.some((word) => key.includes(word)));
  return rule ? rule[1] : "🏷️";
};

// Same category always gets the same colour.
export const categoryTone = (name = "") => {
  let hash = 0;
  for (const char of name) hash = (hash * 31 + char.charCodeAt(0)) % 997;
  return TONES[hash % TONES.length];
};
