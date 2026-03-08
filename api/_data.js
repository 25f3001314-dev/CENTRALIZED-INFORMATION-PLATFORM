const issues = [
  {
    id: "CIV-2025-1142",
    title: "Pothole on Main Street - Near Traffic Intersection",
    cat: "Roads",
    dept: "Roads & Infra",
    officer: "Sh. Rajesh Kumar (#R-04)",
    priority: "High",
    date: "06 Mar 2025",
    status: "progress",
    statusLabel: "IN PROGRESS",
    statusBadge: "badge-progress",
    ai: "Roads & Infra",
    aiConf: 96,
    aiCat: "Road Damage - Pothole",
    aiSeverity: "High",
    aiEst: "2-4 days",
    aiVerify: "Pending",
    loc: "Sector 4, Block A, New Delhi",
    lat: 28.6139,
    lng: 77.209,
    progress: 60,
    photos: { before: true, after: false },
    desc: "Large pothole approximately 40cm diameter and 15cm deep near main traffic intersection.",
    timeline: [
      { s: "Filed", txt: "Photo uploaded. AI categorized as Road Damage - Pothole.", time: "06 Mar 2025, 09:14", done: true },
      { s: "Auto-Assigned", txt: "Assigned to Roads & Infrastructure Dept.", time: "06 Mar 2025, 09:15", done: true },
      { s: "GPS Field Update", txt: "Repair team reached site. Work in progress.", time: "07 Mar 2025, 09:43", done: false, current: true },
      { s: "AI Verification", txt: "Pending after-photo.", time: "-", done: false },
      { s: "Citizen Approval", txt: "Awaiting citizen rating.", time: "-", done: false },
      { s: "Public Archive", txt: "Will publish after citizen approval.", time: "-", done: false }
    ]
  },
  {
    id: "CIV-2025-1138",
    title: "Overflowing Storm Drain - Park Avenue, Sector 7",
    cat: "Water",
    dept: "Water & Drainage",
    officer: "Ms. Sunita Rao (#W-11)",
    priority: "High",
    date: "05 Mar 2025",
    status: "verify",
    statusLabel: "AI VERIFY",
    statusBadge: "badge-verify",
    ai: "Water & Drainage",
    aiConf: 89,
    aiCat: "Drainage Blockage",
    aiSeverity: "Medium",
    aiEst: "3-5 days",
    aiVerify: "In Progress",
    loc: "Park Avenue, Sector 7, Delhi",
    lat: 28.62,
    lng: 77.215,
    progress: 80,
    photos: { before: true, after: true },
    desc: "Blocked drain overflowing onto road after rainfall.",
    timeline: [
      { s: "Filed", txt: "Issue filed and categorized.", time: "05 Mar 2025, 14:20", done: true },
      { s: "Auto-Assigned", txt: "Assigned to Water & Drainage.", time: "05 Mar 2025, 14:21", done: true },
      { s: "GPS Field Update", txt: "Drain cleared and after-photo uploaded.", time: "06 Mar 2025, 11:02", done: true },
      { s: "AI Verification", txt: "Quality verification running.", time: "07 Mar 2025, 08:30", done: false, current: true },
      { s: "Citizen Approval", txt: "Pending verification outcome.", time: "-", done: false },
      { s: "Public Archive", txt: "-", time: "-", done: false }
    ]
  },
  {
    id: "CIV-2025-1127",
    title: "Street Light Non-Functional - MG Road",
    cat: "Electrical",
    dept: "Electrical Dept",
    officer: "Sh. Anil Sharma (#E-03)",
    priority: "Medium",
    date: "03 Mar 2025",
    status: "resolved",
    statusLabel: "RESOLVED",
    statusBadge: "badge-resolved",
    ai: "Electrical Dept",
    aiConf: 98,
    aiCat: "Street Light Failure",
    aiSeverity: "Medium",
    aiEst: "1-2 days",
    aiVerify: "Confirmed",
    loc: "MG Road, Block 2, Delhi",
    lat: 28.605,
    lng: 77.2,
    progress: 100,
    photos: { before: true, after: true },
    desc: "Street light non-functional for 3 weeks.",
    timeline: [
      { s: "Filed", txt: "Issue filed.", time: "03 Mar 2025, 18:45", done: true },
      { s: "Auto-Assigned", txt: "Assigned to Electrical Dept.", time: "03 Mar 2025, 18:46", done: true },
      { s: "GPS Field Update", txt: "Technician replaced bulb and wiring.", time: "04 Mar 2025, 14:30", done: true },
      { s: "AI Verification", txt: "AI confirms fix quality.", time: "04 Mar 2025, 15:10", done: true },
      { s: "Citizen Approval", txt: "Citizen rated 5 stars.", time: "05 Mar 2025, 09:22", done: true },
      { s: "Public Archive", txt: "Published to public archive.", time: "05 Mar 2025, 09:30", done: true }
    ]
  }
];

const archive = [
  { id: "CIV-2025-1089", desc: "Cracked pavement near school gate", cat: "Roads", dept: "Roads", days: 3, conf: 97, rating: 5, outcome: "resolved" },
  { id: "CIV-2025-1082", desc: "Water leakage from main pipeline", cat: "Water", dept: "Water", days: 5, conf: 91, rating: 4, outcome: "resolved" },
  { id: "CIV-2025-1076", desc: "Missing manhole cover - public hazard", cat: "Roads", dept: "Roads", days: 2, conf: 99, rating: 5, outcome: "resolved" },
  { id: "CIV-2025-1071", desc: "Fallen tree blocking residential road", cat: "Parks", dept: "Parks", days: 1, conf: 88, rating: 3, outcome: "resolved" }
];

function todayLabel() {
  const d = new Date();
  return d.toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric" });
}

function makeId() {
  const year = new Date().getFullYear();
  const seq = Math.floor(2000 + Math.random() * 7000);
  return `CIV-${year}-${seq}`;
}

function createIssue(payload) {
  const id = makeId();
  const lat = Number.isFinite(Number(payload.lat)) ? Number(payload.lat) : 28.6139;
  const lng = Number.isFinite(Number(payload.lng)) ? Number(payload.lng) : 77.209;

  return {
    id,
    title: payload.title,
    cat: payload.cat || "Other",
    dept: "Pending Assignment",
    officer: "To be assigned",
    priority: payload.priority || "Normal",
    date: todayLabel(),
    status: "filed",
    statusLabel: "FILED",
    statusBadge: "badge-filed",
    ai: "Auto-detecting",
    aiConf: 0,
    aiCat: "Processing",
    aiSeverity: "-",
    aiEst: "-",
    aiVerify: "-",
    loc: payload.loc || `${lat.toFixed(4)}N, ${lng.toFixed(4)}E`,
    lat,
    lng,
    progress: 5,
    photos: { before: true, after: false },
    desc: payload.desc || "Newly filed issue.",
    timeline: [
      { s: "Filed", txt: "Issue filed by citizen. AI categorization in progress.", time: todayLabel(), done: true },
      { s: "Auto-Assigned", txt: "Pending AI routing.", time: "-", done: false, current: true },
      { s: "GPS Field Update", txt: "-", time: "-", done: false },
      { s: "AI Verification", txt: "-", time: "-", done: false },
      { s: "Citizen Approval", txt: "-", time: "-", done: false },
      { s: "Public Archive", txt: "-", time: "-", done: false }
    ]
  };
}

function analytics() {
  const total = issues.length;
  const resolved = issues.filter((x) => x.status === "resolved").length;
  const active = total - resolved;
  const escalated = issues.filter((x) => x.status === "escalated").length;
  const resolveRate = total ? Number(((resolved / total) * 100).toFixed(1)) : 0;

  return {
    total_issues: total,
    active_cases: active,
    resolved,
    escalated,
    resolve_rate: resolveRate
  };
}

module.exports = {
  issues,
  archive,
  createIssue,
  analytics
};
