---
name: log-debugger
description: "Use when analyzing a log file for errors, detecting ERROR/FATAL/Exception/Warning patterns, diagnosing EDA tool failures (Innovus, Cadence, Synopsys), suggesting fixes for log errors, debugging technology file or capacitance errors, sourcing errors in Tcl scripts"
argument-hint: "Path to the log file, or paste log content directly"
---

# Log Debugger Skill

## Step 1 — Ingest the Log
- If the user provides a file path, read the full file.
- If the user pastes content, work directly from that text.

## Step 2 — Scan for Errors
Search every line for the following patterns (case-insensitive), in priority order:

| Priority | Pattern | Severity |
|---|---|---|
| 1 | `FATAL:` | FATAL |
| 2 | `ERROR:` | ERROR |
| 3 | `Error:` / `Exception` | ERROR |
| 4 | `Traceback` | ERROR |
| 5 | `Segmentation fault` | ERROR |
| 6 | `CRITICAL:` | ERROR |
| 7 | `Warning:` / `WARN:` | WARNING |

## Step 3 — Group Related Errors
Errors within 10 lines of each other likely share a root cause. Group them and name each group.

## Step 4 — Diagnose Using the Fix Table
Match each error message against the table below. Apply the documented fix. If no match, infer root cause from the surrounding log context.

| Error Pattern | Common Cause | Suggested Fix |
|---|---|---|
| `Caught error while sourcing file` | Tcl script has syntax error or sources a missing file | Check the sourced file exists; run it interactively to isolate the bad line |
| `Exception occurred while generating capacitance data from technology file` | Corrupt or mismatched `.tf` / `.tlef` tech file | Verify tech file path and PDK version; re-export from vendor if needed |
| `Innovus version not recognised` | PDK or script targets a different Innovus version | Run `innovus -version`; update `INNOVUS_VERSION` env var or load the correct module |
| `Unsupported LEF version` | LEF file newer than tool supports | Downgrade LEF to supported version or upgrade the tool |
| `Cannot open library` | Library path not set or `.cdslib` missing | Check `cds.lib`; verify `$CDS_INST_DIR` and `$CDS_LIB_DIR` env vars |
| `syntax error in` | Tcl syntax error — unclosed bracket or bad variable | Check the referenced line; common culprits: `[`, `{`, `$` |
| `Cannot find design` | Design name mismatch or missing HDL file | Confirm `analyze` succeeded; check module name matches `elaborate` target |
| `No such file or directory` | Wrong path or missing input file | Confirm file exists; check relative vs absolute path; verify env vars |
| `Permission denied` | File or directory not readable/executable | Run `chmod 644 <file>` or `chmod 755 <dir>`; check NFS mount permissions |
| `Segmentation fault` | Memory corruption or incompatible shared library | Check tool–OS compatibility; run `ldd <binary>`; try `ulimit -s unlimited` |
| `Killed` (exit 137) | Process exceeded memory limit (OOM) | Reduce parallelism; increase `ulimit -v`; request more RAM from scheduler |
| `command not found` | Binary not on `PATH` or module not loaded | `module load <tool>`; verify `$PATH`; check installation directory |
| `Traceback (most recent call last)` | Python exception | Read the last line of the traceback for the specific error type and fix accordingly |
| `ModuleNotFoundError` | Python package not installed | `pip install <module>` in the correct virtualenv |

## Step 5 — Output Each Finding

```
──────────────────────────────────────────
Severity  : FATAL | ERROR | WARNING
Line      : <line number>
Message   : <exact error text>
Context   : <1-2 surrounding lines>
Root Cause: <concise explanation>
Suggested Fix:
  1. <primary action>
  2. <secondary action if needed>
──────────────────────────────────────────
```

Then append a **Summary**:

```
=== SUMMARY ===
FATAL   : <count>
ERROR   : <count>
WARNING : <count>

Most Likely Root Cause : <one sentence if errors share a cause>
Fix Priority Order     : 1. <group/error> → 2. <group/error> → ...
```
