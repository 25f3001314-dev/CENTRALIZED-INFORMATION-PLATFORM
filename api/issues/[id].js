const { issues } = require("../_data");
const { withCors } = require("../_utils");

module.exports = (req, res) => {
  withCors(res);
  if (req.method === "OPTIONS") return res.status(200).end();
  if (req.method !== "GET") return res.status(405).json({ status: "error", message: "Method not allowed" });

  const { id } = req.query;
  const issue = issues.find((x) => x.id === id);
  if (!issue) {
    return res.status(404).json({ status: "error", message: "Issue not found" });
  }

  return res.status(200).json({ status: "success", data: issue });
};
