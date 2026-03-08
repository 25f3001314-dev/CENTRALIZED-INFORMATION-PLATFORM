#!/usr/bin/env Rscript

# Starts CivicPulse R backend on port 8000 by default.

port <- as.integer(Sys.getenv("PORT", "8000"))

required <- c("plumber", "jsonlite")
missing_pkgs <- required[!vapply(required, requireNamespace, logical(1), quietly = TRUE)]
if (length(missing_pkgs) > 0) {
  stop(
    paste0(
      "Missing R packages: ", paste(missing_pkgs, collapse = ", "),
      ". Install with: install.packages(c(\"", paste(missing_pkgs, collapse = "\", \""), "\"))"
    )
  )
}

script_arg <- "--file="
script_path <- "backend/run.R"
for (arg in commandArgs(trailingOnly = FALSE)) {
  if (startsWith(arg, script_arg)) {
    script_path <- substring(arg, nchar(script_arg) + 1)
    break
  }
}
setwd(dirname(normalizePath(script_path, mustWork = FALSE)))

api <- plumber::plumb("plumber.R")
message("CivicPulse R backend running on http://localhost:", port)
api$run(host = "0.0.0.0", port = port)
