const { issues, createIssue } = require("../_data");
const { withCors, parseJsonBody } = require("../_utils");

module.exports = (req, res) => {
  withCors(res);
  if (req.method === "OPTIONS") return res.status(200).end();

  if (req.method === "GET") {
    return res.status(200).json({ status: "success", data: issues });
  }

  if (req.method === "POST") {
    const payload = parseJsonBody(req);
    if (!payload.title || !String(payload.title).trim()) {
      return res.status(400).json({ status: "error", message: "Field 'title' is required" });
    }

    const issue = createIssue(payload);
    issues.unshift(issue);
    return res.status(200).json({ status: "success", message: "Issue created", data: issue });
  }

  return res.status(405).json({ status: "error", message: "Method not allowed" });
};
