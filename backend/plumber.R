# R backend for CivicPulse using Plumber.
# Exposes the same API contract expected by civicpulse-portal.html.

library(plumber)
library(jsonlite)

# -------- Data bootstrap --------
seed_issues <- list(
  list(
    id = "CIV-2025-1142", title = "Pothole on Main Street - Near Traffic Intersection",
    cat = "Roads", dept = "Roads & Infra", officer = "Sh. Rajesh Kumar (#R-04)",
    priority = "High", date = "06 Mar 2025", status = "progress", statusLabel = "IN PROGRESS",
    statusBadge = "badge-progress", ai = "Roads & Infra", aiConf = 96, aiCat = "Road Damage - Pothole",
    aiSeverity = "High", aiEst = "2-4 days", aiVerify = "Pending",
    loc = "Sector 4, Block A, New Delhi", lat = 28.6139, lng = 77.2090, progress = 60,
    photos = list(before = TRUE, after = FALSE),
    desc = "Large pothole approximately 40cm diameter and 15cm deep near main traffic intersection.",
    timeline = list(
      list(s = "Filed", txt = "Photo uploaded. AI categorized as Road Damage - Pothole.", time = "06 Mar 2025, 09:14", done = TRUE),
      list(s = "Auto-Assigned", txt = "Assigned to Roads & Infrastructure Dept.", time = "06 Mar 2025, 09:15", done = TRUE),
      list(s = "GPS Field Update", txt = "Repair team reached site. Work in progress.", time = "07 Mar 2025, 09:43", done = FALSE, current = TRUE),
      list(s = "AI Verification", txt = "Pending after-photo.", time = "-", done = FALSE),
      list(s = "Citizen Approval", txt = "Awaiting citizen rating.", time = "-", done = FALSE),
      list(s = "Public Archive", txt = "Will publish after citizen approval.", time = "-", done = FALSE)
    )
  ),
  list(
    id = "CIV-2025-1138", title = "Overflowing Storm Drain - Park Avenue, Sector 7",
    cat = "Water", dept = "Water & Drainage", officer = "Ms. Sunita Rao (#W-11)",
    priority = "High", date = "05 Mar 2025", status = "verify", statusLabel = "AI VERIFY",
    statusBadge = "badge-verify", ai = "Water & Drainage", aiConf = 89, aiCat = "Drainage Blockage",
    aiSeverity = "Medium", aiEst = "3-5 days", aiVerify = "In Progress",
    loc = "Park Avenue, Sector 7, Delhi", lat = 28.6200, lng = 77.2150, progress = 80,
    photos = list(before = TRUE, after = TRUE),
    desc = "Blocked drain overflowing onto road after rainfall.",
    timeline = list(
      list(s = "Filed", txt = "Issue filed and categorized.", time = "05 Mar 2025, 14:20", done = TRUE),
      list(s = "Auto-Assigned", txt = "Assigned to Water & Drainage.", time = "05 Mar 2025, 14:21", done = TRUE),
      list(s = "GPS Field Update", txt = "Drain cleared and after-photo uploaded.", time = "06 Mar 2025, 11:02", done = TRUE),
      list(s = "AI Verification", txt = "Quality verification running.", time = "07 Mar 2025, 08:30", done = FALSE, current = TRUE),
      list(s = "Citizen Approval", txt = "Pending verification outcome.", time = "-", done = FALSE),
      list(s = "Public Archive", txt = "-", time = "-", done = FALSE)
    )
  ),
  list(
    id = "CIV-2025-1127", title = "Street Light Non-Functional - MG Road",
    cat = "Electrical", dept = "Electrical Dept", officer = "Sh. Anil Sharma (#E-03)",
    priority = "Medium", date = "03 Mar 2025", status = "resolved", statusLabel = "RESOLVED",
    statusBadge = "badge-resolved", ai = "Electrical Dept", aiConf = 98, aiCat = "Street Light Failure",
    aiSeverity = "Medium", aiEst = "1-2 days", aiVerify = "Confirmed",
    loc = "MG Road, Block 2, Delhi", lat = 28.6050, lng = 77.2000, progress = 100,
    photos = list(before = TRUE, after = TRUE),
    desc = "Street light non-functional for 3 weeks.",
    timeline = list(
      list(s = "Filed", txt = "Issue filed.", time = "03 Mar 2025, 18:45", done = TRUE),
      list(s = "Auto-Assigned", txt = "Assigned to Electrical Dept.", time = "03 Mar 2025, 18:46", done = TRUE),
      list(s = "GPS Field Update", txt = "Technician replaced bulb and wiring.", time = "04 Mar 2025, 14:30", done = TRUE),
      list(s = "AI Verification", txt = "AI confirms fix quality.", time = "04 Mar 2025, 15:10", done = TRUE),
      list(s = "Citizen Approval", txt = "Citizen rated 5 stars.", time = "05 Mar 2025, 09:22", done = TRUE),
      list(s = "Public Archive", txt = "Published to public archive.", time = "05 Mar 2025, 09:30", done = TRUE)
    )
  ),
  list(
    id = "CIV-2025-1118", title = "Uncollected Garbage - Gandhi Nagar Phase 2",
    cat = "Sanitation", dept = "Sanitation", officer = "Ms. Meena Devi (#S-07)",
    priority = "High", date = "05 Mar 2025", status = "assigned", statusLabel = "ASSIGNED",
    statusBadge = "badge-assigned", ai = "Sanitation", aiConf = 92, aiCat = "Waste Accumulation",
    aiSeverity = "High", aiEst = "1-2 days", aiVerify = "-",
    loc = "Gandhi Nagar, Phase 2, Delhi", lat = 28.6300, lng = 77.1950, progress = 25,
    photos = list(before = TRUE, after = FALSE),
    desc = "Large garbage pile at street corner.",
    timeline = list(
      list(s = "Filed", txt = "Issue filed and categorized.", time = "05 Mar 2025, 07:10", done = TRUE),
      list(s = "Auto-Assigned", txt = "Assigned to Sanitation Dept.", time = "05 Mar 2025, 07:11", done = TRUE),
      list(s = "GPS Field Update", txt = "Collection scheduled.", time = "-", done = FALSE, current = TRUE),
      list(s = "AI Verification", txt = "-", time = "-", done = FALSE),
      list(s = "Citizen Approval", txt = "-", time = "-", done = FALSE),
      list(s = "Public Archive", txt = "-", time = "-", done = FALSE)
    )
  ),
  list(
    id = "CIV-2025-1097", title = "Park Bench Vandalized - Nehru Park East Wing",
    cat = "Parks", dept = "Parks & Gardens", officer = "Pending Assignment",
    priority = "Low", date = "04 Mar 2025", status = "filed", statusLabel = "FILED",
    statusBadge = "badge-filed", ai = "Parks & Gardens", aiConf = 87, aiCat = "Public Property Damage",
    aiSeverity = "Low", aiEst = "5-7 days", aiVerify = "-",
    loc = "Nehru Park, East Wing, Delhi", lat = 28.5950, lng = 77.1880, progress = 10,
    photos = list(before = TRUE, after = FALSE),
    desc = "Wooden bench broken and covered in graffiti.",
    timeline = list(
      list(s = "Filed", txt = "Issue filed and categorized.", time = "04 Mar 2025, 16:30", done = TRUE),
      list(s = "Auto-Assigned", txt = "Awaiting routing confirmation.", time = "-", done = FALSE, current = TRUE),
      list(s = "GPS Field Update", txt = "-", time = "-", done = FALSE),
      list(s = "AI Verification", txt = "-", time = "-", done = FALSE),
      list(s = "Citizen Approval", txt = "-", time = "-", done = FALSE),
      list(s = "Public Archive", txt = "-", time = "-", done = FALSE)
    )
  )
)

seed_archive <- list(
  list(id = "CIV-2025-1089", desc = "Cracked pavement near school gate", cat = "Roads", dept = "Roads", days = 3, conf = 97, rating = 5, outcome = "resolved"),
  list(id = "CIV-2025-1082", desc = "Water leakage from main pipeline", cat = "Water", dept = "Water", days = 5, conf = 91, rating = 4, outcome = "resolved"),
  list(id = "CIV-2025-1076", desc = "Missing manhole cover - public hazard", cat = "Roads", dept = "Roads", days = 2, conf = 99, rating = 5, outcome = "resolved"),
  list(id = "CIV-2025-1071", desc = "Fallen tree blocking residential road", cat = "Parks", dept = "Parks", days = 1, conf = 88, rating = 3, outcome = "resolved")
)

issues_db <- seed_issues
archive_db <- seed_archive

format_today <- function() {
  format(Sys.Date(), "%d %b %Y")
}

new_issue_id <- function() {
  year <- format(Sys.Date(), "%Y")
  # 4-digit sequence to reduce collisions for in-memory demo backend.
  seq_num <- sample(2000:9999, 1)
  paste0("CIV-", year, "-", seq_num)
}

safe_or <- function(value, fallback) {
  if (is.null(value) || identical(value, "")) {
    return(fallback)
  }
  value
}

build_issue <- function(payload) {
  issue_id <- new_issue_id()
  lat <- suppressWarnings(as.numeric(safe_or(payload$lat, 28.6139)))
  lng <- suppressWarnings(as.numeric(safe_or(payload$lng, 77.2090)))
  if (is.na(lat)) lat <- 28.6139
  if (is.na(lng)) lng <- 77.2090

  title <- safe_or(payload$title, "Citizen submitted issue")
  category <- safe_or(payload$cat, "Other")
  now <- format_today()

  list(
    id = issue_id,
    title = title,
    cat = category,
    dept = "Pending Assignment",
    officer = "To be assigned",
    priority = safe_or(payload$priority, "Normal"),
    date = now,
    status = "filed",
    statusLabel = "FILED",
    statusBadge = "badge-filed",
    ai = "Auto-detecting",
    aiConf = 0,
    aiCat = "Processing",
    aiSeverity = "-",
    aiEst = "-",
    aiVerify = "-",
    loc = safe_or(payload$loc, paste0(round(lat, 6), "N, ", round(lng, 6), "E")),
    lat = lat,
    lng = lng,
    progress = 5,
    photos = list(before = TRUE, after = FALSE),
    desc = safe_or(payload$desc, "Newly filed issue."),
    timeline = list(
      list(s = "Filed", txt = "Issue filed by citizen. AI categorization in progress.", time = now, done = TRUE),
      list(s = "Auto-Assigned", txt = "Pending AI routing.", time = "-", done = FALSE, current = TRUE),
      list(s = "GPS Field Update", txt = "-", time = "-", done = FALSE),
      list(s = "AI Verification", txt = "-", time = "-", done = FALSE),
      list(s = "Citizen Approval", txt = "-", time = "-", done = FALSE),
      list(s = "Public Archive", txt = "-", time = "-", done = FALSE)
    )
  )
}

build_dashboard <- function() {
  total <- length(issues_db)
  active <- sum(vapply(issues_db, function(x) !identical(x$status, "resolved"), logical(1)))
  resolved <- sum(vapply(issues_db, function(x) identical(x$status, "resolved"), logical(1)))
  escalated <- sum(vapply(issues_db, function(x) identical(x$status, "escalated"), logical(1)))
  resolve_rate <- if (total > 0) round((resolved / total) * 100, 1) else 0

  list(
    total_issues = total,
    active_cases = active,
    resolved = resolved,
    escalated = escalated,
    resolve_rate = resolve_rate
  )
}

# -------- Astral automation --------
automation_jobs <- list()

astral_base_url <- function() {
  base <- Sys.getenv("ASTRAL_BASE_URL", "")
  if (identical(base, "")) {
    return("https://api.astral.example")
  }
  sub("/$", "", base)
}

astral_api_key <- function() {
  Sys.getenv("ASTRAL_API_KEY", "")
}

is_astral_ready <- function() {
  !identical(astral_api_key(), "")
}

astral_request <- function(path, body = list()) {
  if (!is_astral_ready()) {
    stop("ASTRAL_API_KEY is not configured")
  }

  payload <- jsonlite::toJSON(body, auto_unbox = TRUE, null = "null")
  headers <- c(
    "-H", "Content-Type: application/json",
    "-H", paste0("Authorization: Bearer ", astral_api_key())
  )
  args <- c(
    "-sS", "-X", "POST",
    headers,
    "-d", payload,
    paste0(astral_base_url(), path)
  )

  out <- system2("curl", args = args, stdout = TRUE, stderr = TRUE)
  if (!length(out)) {
    return(list(status = "unknown", raw = ""))
  }

  text <- paste(out, collapse = "\n")
  parsed <- tryCatch(
    jsonlite::fromJSON(text, simplifyVector = FALSE),
    error = function(e) list(raw = text)
  )
  parsed
}

new_job_id <- function() {
  paste0("AUTO-", format(Sys.time(), "%Y%m%d%H%M%S"), "-", sample(1000:9999, 1))
}

save_job <- function(job) {
  automation_jobs <<- c(list(job), automation_jobs)
}

find_job <- function(job_id) {
  hits <- Filter(function(x) identical(x$id, job_id), automation_jobs)
  if (length(hits) == 0) {
    return(NULL)
  }
  hits[[1]]
}

# -------- Middleware --------

#* @filter cors
function(req, res) {
  res$setHeader("Access-Control-Allow-Origin", "*")
  res$setHeader("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
  res$setHeader("Access-Control-Allow-Headers", "Content-Type")
  if (req$REQUEST_METHOD == "OPTIONS") {
    res$status <- 200
    return(list())
  }
  plumber::forward()
}

# -------- Static page --------

#* Serve the CivicPulse page from project root
#* @get /
#* @serializer contentType list(type='text/html')
function() {
  readChar("../civicpulse-portal.html", file.info("../civicpulse-portal.html")$size, useBytes = TRUE)
}

#* @get /civicpulse-portal.html
#* @serializer contentType list(type='text/html')
function() {
  readChar("../civicpulse-portal.html", file.info("../civicpulse-portal.html")$size, useBytes = TRUE)
}

# -------- API --------

#* Health check
#* @get /api/health
#* @serializer unboxedJSON
function() {
  list(status = "ok", backend = "R (plumber)", timestamp = format(Sys.time(), "%Y-%m-%d %H:%M:%S"))
}

#* Fetch all issues
#* @get /api/issues
#* @serializer unboxedJSON
function() {
  list(status = "success", data = issues_db)
}

#* Fetch one issue by id
#* @get /api/issues/<id>
#* @serializer unboxedJSON
function(id, res) {
  found <- Filter(function(x) identical(x$id, id), issues_db)
  if (length(found) == 0) {
    res$status <- 404
    return(list(status = "error", message = "Issue not found"))
  }
  list(status = "success", data = found[[1]])
}

#* Create a new issue
#* @post /api/issues
#* @parser json
#* @serializer unboxedJSON
function(req, res) {
  payload <- req$body
  if (is.null(payload) || is.null(payload$title) || identical(trimws(payload$title), "")) {
    res$status <- 400
    return(list(status = "error", message = "Field 'title' is required"))
  }

  new_issue <- build_issue(payload)
  issues_db <<- c(list(new_issue), issues_db)

  list(status = "success", message = "Issue created", data = new_issue)
}

#* Fetch public archive rows
#* @get /api/archive
#* @serializer unboxedJSON
function() {
  list(status = "success", data = archive_db)
}

#* Dashboard analytics summary
#* @get /api/analytics/dashboard
#* @serializer unboxedJSON
function() {
  list(status = "success", data = build_dashboard())
}

#* Astral integration status
#* @get /api/automation/status
#* @serializer unboxedJSON
function() {
  list(
    status = "success",
    data = list(
      provider = "Astral API",
      configured = is_astral_ready(),
      base_url = astral_base_url(),
      jobs_count = length(automation_jobs)
    )
  )
}

#* OCR/scan a document or image via Astral API
#* @post /api/automation/scan
#* @parser json
#* @serializer unboxedJSON
function(req, res) {
  payload <- req$body
  image_url <- if (!is.null(payload$image_url)) payload$image_url else NULL
  document_text <- if (!is.null(payload$text)) payload$text else NULL

  if (is.null(image_url) && is.null(document_text)) {
    res$status <- 400
    return(list(status = "error", message = "Provide either 'image_url' or 'text'"))
  }

  if (!is_astral_ready()) {
    res$status <- 503
    return(list(status = "error", message = "ASTRAL_API_KEY is not configured"))
  }

  job <- list(
    id = new_job_id(),
    type = "scan",
    created_at = format(Sys.time(), "%Y-%m-%d %H:%M:%S"),
    input = list(image_url = image_url, text = document_text),
    steps = list(
      list(name = "scan", status = "running")
    )
  )

  result <- tryCatch(
    astral_request("/ocr", list(image_url = image_url, text = document_text)),
    error = function(e) list(error = e$message)
  )

  job$steps[[1]]$status <- if (!is.null(result$error)) "failed" else "completed"
  job$result <- result
  job$status <- if (!is.null(result$error)) "failed" else "completed"
  save_job(job)

  list(status = "success", data = job)
}

#* Run joined automation pipeline (monitor + scan + OCR)
#* @post /api/automation/monitor
#* @parser json
#* @serializer unboxedJSON
function(req, res) {
  payload <- req$body
  mode <- if (!is.null(payload$mode)) as.character(payload$mode) else "issue-monitor"
  issue_id <- if (!is.null(payload$issue_id)) as.character(payload$issue_id) else ""

  if (identical(tolower(mode), "people-tracking") || identical(tolower(mode), "people_tracking")) {
    res$status <- 400
    return(list(
      status = "error",
      message = "People tracking is not supported. Use issue-level monitoring and document OCR only."
    ))
  }

  if (!is_astral_ready()) {
    res$status <- 503
    return(list(status = "error", message = "ASTRAL_API_KEY is not configured"))
  }

  issue <- NULL
  if (!identical(issue_id, "")) {
    hits <- Filter(function(x) identical(x$id, issue_id), issues_db)
    if (length(hits) > 0) issue <- hits[[1]]
  }

  monitor_payload <- list(
    mode = mode,
    issue_id = issue_id,
    issue_title = if (is.null(issue)) NULL else issue$title,
    issue_status = if (is.null(issue)) NULL else issue$status,
    issue_location = if (is.null(issue)) NULL else issue$loc
  )

  job <- list(
    id = new_job_id(),
    type = "monitor",
    created_at = format(Sys.time(), "%Y-%m-%d %H:%M:%S"),
    input = monitor_payload,
    steps = list(
      list(name = "monitor", status = "running"),
      list(name = "scan", status = "pending"),
      list(name = "ocr", status = "pending")
    )
  )

  monitor_result <- tryCatch(
    astral_request("/monitor", monitor_payload),
    error = function(e) list(error = e$message)
  )

  if (!is.null(monitor_result$error)) {
    job$steps[[1]]$status <- "failed"
    job$status <- "failed"
    job$result <- list(monitor = monitor_result)
    save_job(job)
    return(list(status = "success", data = job))
  }

  job$steps[[1]]$status <- "completed"
  job$steps[[2]]$status <- "completed"
  job$steps[[3]]$status <- "completed"
  job$status <- "completed"
  job$result <- list(monitor = monitor_result)
  save_job(job)

  list(status = "success", data = job)
}

#* List automation jobs
#* @get /api/automation/jobs
#* @serializer unboxedJSON
function() {
  list(status = "success", data = automation_jobs)
}

#* Get one automation job by id
#* @get /api/automation/jobs/<id>
#* @serializer unboxedJSON
function(id, res) {
  job <- find_job(id)
  if (is.null(job)) {
    res$status <- 404
    return(list(status = "error", message = "Automation job not found"))
  }
  list(status = "success", data = job)
}
