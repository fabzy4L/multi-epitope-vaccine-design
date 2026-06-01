# extract_s1_sequences.R
# ======================
# R companion to extract_s1_sequences.py
# Extracts SARS-CoV-2 Spike / S1 sequences from a CD-HIT representative
# FASTA for MHC-I / MHC-II epitope prediction.
#
# Uses the seqinr package already present in your pipeline (../../tools/seqinr/).
# Optionally uses Biostrings (Bioconductor) if available.
#
# Usage:
#   Rscript extract_s1_sequences.R \
#       --fasta 1624324292.fas.1 \
#       --out   s1_candidates.fasta
#
#   Or source interactively and call extract_s1() directly.
#
# Output:
#   s1_candidates.fasta         — filtered FASTA, ready for IEDB upload
#   s1_extraction_report.txt    — summary statistics
#   s1_length_distribution.pdf  — sequence length histogram
# -----------------------------------------------------------------------

suppressPackageStartupMessages({
  library(optparse)
  library(seqinr)        # already in your pipeline
})

# -----------------------------------------------------------------------
# Keyword definitions  (mirrors the Python script)
# -----------------------------------------------------------------------

BROAD_KEYWORDS <- c(
  "spike",
  "surface glycoprotein",
  "s protein",
  "\\bS1\\b",
  "receptor.binding domain",
  "\\bRBD\\b",
  "fusion peptide",
  "heptad repeat",
  "SARS.CoV",
  "coronavirus.*spike",
  "spike.*coronavirus",
  "2019.nCoV",
  "COVID"
)

STRICT_KEYWORDS <- c(
  "\\bS1\\b",
  "spike protein.*S1",
  "S1 subunit",
  "receptor.binding domain",
  "\\bRBD\\b"
)

EXCLUDE_KEYWORDS <- c(
  "nucleocapsid",
  "\\bN protein\\b",
  "\\bE protein\\b",
  "envelope protein",
  "membrane protein",
  "\\bM protein\\b",
  "ORF[0-9]",
  "hypothetical",
  "non-structural",
  "nsp[0-9]",
  "replicase",
  "helicase",
  "protease"
)

# S1 domain boundaries (UniProt P0DTC2, 1-based)
S1_START <- 1
S1_END   <- 685

# -----------------------------------------------------------------------
# Helper: build a single regex from a vector of patterns
# -----------------------------------------------------------------------
build_regex <- function(patterns) {
  paste(patterns, collapse = "|")
}

# -----------------------------------------------------------------------
# Filter function
# -----------------------------------------------------------------------
classify_record <- function(name, mode = "broad") {
  keywords <- if (mode == "strict") STRICT_KEYWORDS else BROAD_KEYWORDS
  inc_re   <- build_regex(keywords)
  exc_re   <- build_regex(EXCLUDE_KEYWORDS)

  if (grepl(exc_re, name, ignore.case = TRUE, perl = TRUE)) return(FALSE)
  grepl(inc_re, name, ignore.case = TRUE, perl = TRUE)
}

# -----------------------------------------------------------------------
# S1 domain trimmer
# -----------------------------------------------------------------------
trim_to_s1 <- function(seq_str, start = S1_START, end = S1_END) {
  # seq_str is a plain character string (not a vector of single chars)
  total <- nchar(seq_str)
  actual_end <- min(end, total)
  substr(seq_str, start, actual_end)
}

# -----------------------------------------------------------------------
# FASTA I/O via seqinr
# -----------------------------------------------------------------------
read_fasta_seqinr <- function(path) {
  seqs <- seqinr::read.fasta(
    file        = path,
    seqtype     = "AA",
    as.string   = TRUE,
    forceDNAtolower = FALSE
  )
  # seqinr stores sequences as lowercase; keep as-is, annotate() gives names
  seqs
}

write_fasta_simple <- function(sequences, names, path, line_width = 60) {
  # sequences: character vector of AA strings
  # names    : character vector of headers (without '>')
  con <- file(path, open = "w")
  on.exit(close(con))
  for (i in seq_along(sequences)) {
    writeLines(paste0(">", names[i]), con)
    seq_chars <- sequences[i]
    # wrap at line_width
    n <- nchar(seq_chars)
    starts <- seq(1, n, by = line_width)
    for (s in starts) {
      writeLines(substr(seq_chars, s, min(s + line_width - 1, n)), con)
    }
  }
  invisible(NULL)
}

# -----------------------------------------------------------------------
# CD-HIT .clstr parser
# -----------------------------------------------------------------------
parse_clstr <- function(path) {
  if (!file.exists(path)) {
    message("Cluster file not found: ", path)
    return(NULL)
  }
  lines <- readLines(path)
  clusters <- list()
  current_rep     <- NULL
  current_members <- character(0)
  current_size    <- 0L

  for (line in lines) {
    if (grepl("^>Cluster", line)) {
      if (!is.null(current_rep)) {
        clusters[[current_rep]] <- list(
          size    = current_size,
          members = current_members
        )
      }
      current_rep     <- NULL
      current_members <- character(0)
      current_size    <- 0L
    } else if (nchar(trimws(line)) > 0) {
      current_size <- current_size + 1L
      m <- regmatches(line, regexpr(">([^.]+)\\.\\.\\.", line, perl = TRUE))
      if (length(m) > 0) {
        seq_id <- sub(">([^.]+)\\.\\.\\.", "\\1", m)
        current_members <- c(current_members, seq_id)
        if (grepl("\\*$", line)) {
          current_rep <- seq_id
        }
      }
    }
  }
  # last cluster
  if (!is.null(current_rep)) {
    clusters[[current_rep]] <- list(size = current_size, members = current_members)
  }
  clusters
}

# -----------------------------------------------------------------------
# Plot: sequence length distribution
# -----------------------------------------------------------------------
plot_length_distribution <- function(lengths, out_pdf) {
  if (!requireNamespace("ggplot2", quietly = TRUE)) {
    # Fallback to base R
    pdf(out_pdf, width = 7, height = 5)
    hist(
      lengths,
      breaks = 20,
      main   = "S1 Candidate Sequence Length Distribution",
      xlab   = "Sequence length (aa)",
      ylab   = "Count",
      col    = "#4E79A7",
      border = "white"
    )
    abline(v = mean(lengths), col = "firebrick", lwd = 2, lty = 2)
    legend("topright", legend = paste("Mean =", round(mean(lengths))),
           col = "firebrick", lty = 2, bty = "n")
    dev.off()
  } else {
    library(ggplot2)
    df <- data.frame(length = lengths)
    p  <- ggplot(df, aes(x = length)) +
      geom_histogram(bins = 20, fill = "#4E79A7", color = "white") +
      geom_vline(xintercept = mean(lengths), color = "firebrick",
                 linetype = "dashed", linewidth = 0.8) +
      annotate("text", x = mean(lengths), y = Inf,
               label = paste(" Mean =", round(mean(lengths))),
               vjust = 2, hjust = 0, color = "firebrick", size = 3.5) +
      labs(
        title    = "S1 Candidate Sequence Length Distribution",
        subtitle = paste(nrow(df), "sequences extracted"),
        x        = "Sequence length (aa)",
        y        = "Count"
      ) +
      theme_minimal(base_size = 12)
    ggsave(out_pdf, p, width = 7, height = 5, device = "pdf")
  }
  message("Length distribution plot → ", out_pdf)
}

# -----------------------------------------------------------------------
# Report writer
# -----------------------------------------------------------------------
write_report <- function(total, hits_names, hits_seqs, mode, trim, out_fasta,
                         cluster_info = NULL, report_path) {
  lens <- nchar(hits_seqs)
  lines <- c(
    strrep("=", 60),
    "  S1 Sequence Extraction Report  (R)",
    strrep("=", 60),
    sprintf("  Input sequences     : %d", total),
    sprintf("  S1 candidates found : %d", length(hits_names)),
    sprintf("  Filter mode         : %s", mode),
    sprintf("  S1 domain trim      : %s",
            ifelse(trim, "yes (residues 1-685)", "no (full spike)")),
    sprintf("  Output file         : %s", out_fasta),
    strrep("-", 60)
  )

  if (length(lens) > 0) {
    lines <- c(lines,
      sprintf("  Sequence length — min : %d aa", min(lens)),
      sprintf("  Sequence length — max : %d aa", max(lens)),
      sprintf("  Sequence length — avg : %d aa", round(mean(lens))),
      strrep("-", 60)
    )
  }

  if (!is.null(cluster_info)) {
    lines <- c(lines, "  Cluster sizes for matched sequences:")
    for (nm in sort(hits_names)) {
      short_id <- strsplit(nm, " ")[[1]][1]
      info <- cluster_info[[short_id]]
      if (!is.null(info)) {
        lines <- c(lines,
          sprintf("    %-30s  cluster size = %d", short_id, info$size))
      }
    }
    lines <- c(lines, strrep("-", 60))
  }

  lines <- c(lines, "  Headers of extracted sequences:", "")
  for (i in seq_along(hits_names)) {
    hdr <- substr(hits_names[i], 1, 100)
    lines <- c(lines, sprintf("    [%d aa]  %s", nchar(hits_seqs[i]), hdr))
  }
  lines <- c(lines, "", strrep("=", 60))

  writeLines(lines, report_path)
  cat(paste(lines, collapse = "\n"), "\n")
  invisible(NULL)
}

# -----------------------------------------------------------------------
# Core extraction function  (callable interactively or from CLI)
# -----------------------------------------------------------------------

#' @param fasta_path Path to CD-HIT representative FASTA (*.fas.1)
#' @param out_path   Output FASTA path
#' @param clstr_path Optional path to *.clstr file
#' @param mode       "broad" or "strict"
#' @param trim_s1    Logical — trim to S1 domain (residues 1-685)?
#' @param min_len    Minimum sequence length
#' @param max_len    Maximum sequence length (NULL = no limit)
#' @param dry_run    Logical — if TRUE, prints summary but writes nothing
#' @return Invisible data.frame of hits
extract_s1 <- function(
    fasta_path,
    out_path   = "s1_candidates.fasta",
    clstr_path = NULL,
    mode       = "broad",
    trim_s1    = FALSE,
    min_len    = 8L,
    max_len    = NULL,
    dry_run    = FALSE
) {
  # ── Validate ─────────────────────────────────────────────────────────
  if (!file.exists(fasta_path)) stop("FASTA not found: ", fasta_path)
  stopifnot(mode %in% c("broad", "strict"))

  report_path <- sub("\\.[^.]+$", ".report.txt", out_path)
  plot_path   <- sub("\\.[^.]+$", "_lengths.pdf", out_path)

  # ── Load cluster info ─────────────────────────────────────────────────
  cluster_info <- NULL
  if (!is.null(clstr_path)) {
    message("Parsing cluster file: ", clstr_path)
    cluster_info <- parse_clstr(clstr_path)
    message("  → ", length(cluster_info), " clusters loaded")
  }

  # ── Read FASTA ────────────────────────────────────────────────────────
  message("Reading FASTA: ", fasta_path)
  seqs <- read_fasta_seqinr(fasta_path)
  # seqinr names are the first word of the header by default; recover full
  # annotation via attr(..., "Annot")
  full_headers <- vapply(seqs, function(s) {
    ann <- attr(s, "Annot")
    if (!is.null(ann)) sub("^> *", "", ann) else ""
  }, character(1))
  seq_strings <- vapply(seqs, function(s) toupper(paste(s, collapse = "")),
                        character(1))

  total <- length(seq_strings)
  message(sprintf("  → %d total sequences", total))

  # ── Filter ────────────────────────────────────────────────────────────
  keep_idx <- which(vapply(full_headers, classify_record,
                           mode = mode, FUN.VALUE = logical(1)))

  if (length(keep_idx) == 0) {
    warning("No sequences matched. Try mode='broad' or inspect your headers.")
    return(invisible(NULL))
  }

  hit_headers <- full_headers[keep_idx]
  hit_seqs    <- seq_strings[keep_idx]

  # Trim to S1 domain
  if (trim_s1) {
    hit_seqs <- vapply(hit_seqs, trim_to_s1, character(1))
  }

  # Length filter
  lens <- nchar(hit_seqs)
  len_keep <- lens >= min_len
  if (!is.null(max_len)) len_keep <- len_keep & (lens <= max_len)
  hit_headers <- hit_headers[len_keep]
  hit_seqs    <- hit_seqs[len_keep]

  message(sprintf("  → %d S1 candidates after filtering", length(hit_seqs)))

  # ── Build result data.frame ───────────────────────────────────────────
  result_df <- data.frame(
    header = hit_headers,
    length = nchar(hit_seqs),
    sequence = hit_seqs,
    stringsAsFactors = FALSE
  )

  # ── Write report ──────────────────────────────────────────────────────
  write_report(
    total        = total,
    hits_names   = hit_headers,
    hits_seqs    = hit_seqs,
    mode         = mode,
    trim         = trim_s1,
    out_fasta    = out_path,
    cluster_info = cluster_info,
    report_path  = if (!dry_run) report_path else tempfile()
  )

  if (dry_run) {
    message("Dry run — no files written.")
    return(invisible(result_df))
  }

  # ── Write FASTA ───────────────────────────────────────────────────────
  dir.create(dirname(out_path), recursive = TRUE, showWarnings = FALSE)
  write_fasta_simple(hit_seqs, hit_headers, out_path)
  message("FASTA written → ", out_path)

  # ── Length distribution plot ──────────────────────────────────────────
  if (length(hit_seqs) > 1) {
    tryCatch(
      plot_length_distribution(nchar(hit_seqs), plot_path),
      error = function(e) message("Plot skipped: ", conditionMessage(e))
    )
  }

  invisible(result_df)
}

# -----------------------------------------------------------------------
# CLI entry point (when run as Rscript)
# -----------------------------------------------------------------------

if (!interactive()) {
  option_list <- list(
    make_option("--fasta",   type = "character", help = "CD-HIT representative FASTA"),
    make_option("--out",     type = "character", default = "s1_candidates.fasta",
                help = "Output FASTA path [default: %default]"),
    make_option("--clstr",   type = "character", default = NULL,
                help = "Optional .clstr cluster map"),
    make_option("--mode",    type = "character", default = "broad",
                help = "Filter mode: broad | strict [default: %default]"),
    make_option("--trim-s1", action = "store_true", default = FALSE,
                help = "Trim to S1 domain (residues 1-685)"),
    make_option("--min-len", type = "integer",   default = 8L,
                help = "Minimum sequence length [default: %default]"),
    make_option("--max-len", type = "integer",   default = NULL,
                help = "Maximum sequence length [default: none]"),
    make_option("--dry-run", action = "store_true", default = FALSE,
                help = "Preview only, no files written")
  )

  opt_parser <- OptionParser(
    usage       = "Rscript extract_s1_sequences.R --fasta FILE --out FILE [options]",
    option_list = option_list,
    description = "Extract SARS-CoV-2 S1 sequences from a CD-HIT FASTA for epitope prediction."
  )
  opt <- parse_args(opt_parser)

  if (is.null(opt$fasta)) {
    print_help(opt_parser)
    quit(status = 1)
  }

  extract_s1(
    fasta_path = opt$fasta,
    out_path   = opt$out,
    clstr_path = opt$clstr,
    mode       = opt$mode,
    trim_s1    = opt$`trim-s1`,
    min_len    = opt$`min-len`,
    max_len    = opt$`max-len`,
    dry_run    = opt$`dry-run`
  )
}
