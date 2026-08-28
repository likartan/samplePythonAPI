---
name: sphinx-documentation
description: "Create, configure, write, build, convert content into, and troubleshoot Sphinx documentation. Use for Sphinx projects, converting PDF/Word/Markdown source material into a Sphinx site, conf.py, index.rst, reStructuredText, MyST Markdown, toctrees, autodoc, intersphinx, themes, builders, sphinx-build warnings, link checking, or HTML/PDF/man-page output. Also use for Read the Docs failures with Sphinx commands, toc.* or ref.* warnings, and sphinxcontrib extensions. Use whenever documentation is built with Sphinx, even if the request only mentions a docs page or broken build. Do not use for MkDocs, Docusaurus, generic Markdown editing, or summarizing existing documents unless Sphinx output is requested or confirmed."
argument-hint: "Describe the Sphinx documentation task or build failure"
---

# Sphinx Documentation

Work from the repository's existing documentation structure and dependency tooling. Make the requested documentation change, then prove it builds with the narrowest relevant Sphinx checks.

## Procedure

### 1. Inspect the Documentation Project

Find the source directory and configuration before editing. Inspect the smallest useful set of files:

- `conf.py`, which defines Sphinx configuration
- the root document, normally `index.rst` or `index.md`
- nearby source pages and their `toctree` entries
- `Makefile`, `make.bat`, `pyproject.toml`, requirements files, lock files, and CI workflows
- existing extensions, theme, source suffixes, and build commands

Treat repository commands and conventions as authoritative. Determine:

- source, configuration, and output directories
- reStructuredText, MyST Markdown, or mixed source format
- expected builders such as `html`, `latexpdf`, `man`, or `linkcheck`
- the repository's Python environment and dependency manager

Resolve the exact Python interpreter before installing or invoking Sphinx. If the
user names a virtual environment, configure and inspect that environment
directly. Verify Sphinx through the same interpreter, for example with
`<python> -m sphinx --version`; package metadata from another environment or a
`sphinx-build` found on `PATH` is not proof that the selected interpreter can
import Sphinx.

**Complete when:** the owning `conf.py`, root document, dependency source, exact Python interpreter, and an executable build command are known, and that interpreter can import Sphinx.

### 2. Initialize Only When Needed

For a new documentation project, add Sphinx through the repository's existing dependency manager and use `sphinx-quickstart` to establish the initial source tree. Prefer non-interactive options when the project name, author, version, language, and source/build layout are already known; ask only for consequential missing values.

Do not run `sphinx-quickstart` over an existing Sphinx source directory. Extend the current project instead.

For Markdown sources, install `myst-parser`, add `'myst_parser'` to `extensions`, and retain `.rst` support unless the project explicitly uses Markdown only. Configure nonstandard suffixes with `source_suffix`.

Record documentation dependencies in the repository's existing dependency
source. Keep virtual environments and generated build directories out of
version control.

After initialization, build the untouched scaffold with strict warnings before
adding content. This cheap baseline separates environment and generator defects
from source-conversion defects.

**Complete when:** the project has one configuration file, one root document, tracked dependencies, a discoverable build command, and a clean baseline build.

### 3. Make the Documentation Change

Match the markup and organization of neighboring pages.

#### Structure

- Add every intended page to a `toctree` unless the project deliberately uses orphan pages.
- Write document names without file extensions and with `/` separators, including on Windows.
- Keep the root document focused on navigation and introductory content.
- Preserve the existing heading hierarchy and `toctree` depth unless the request changes information architecture.

#### References

- Prefer semantic Sphinx references over hard-coded output URLs.
- Use `:doc:` for documents, `:ref:` for explicit labels, and domain roles such as `:py:class:` or `:cpp:func:` for documented objects.
- Use `sphinx.ext.intersphinx` for objects in external Sphinx documentation and configure `intersphinx_mapping` in `conf.py`.
- Give labels stable, descriptive names when headings may be renamed.

#### API Documentation

- Use the appropriate Sphinx domain for manually documented APIs.
- For Python docstrings, enable `sphinx.ext.autodoc` only when requested or already established.
- Make the documented package importable in the build environment. Prefer installing the package over adding fragile relative paths to `sys.path`.
- If imports require unavailable optional services or dependencies, use narrowly scoped `autodoc_mock_imports` and explain the compromise.

#### Configuration and Extensions

- Keep `conf.py` values simple and deterministic because Sphinx executes it as Python during every build.
- Add an extension to both project dependencies and `extensions`.
- Resolve relative custom-extension paths from the configuration directory with absolute paths.
- Set `needs_sphinx` when the project relies on behavior introduced by a specific Sphinx version.
- Configure themes through `html_theme` and theme-specific `html_theme_options`; add static assets through `html_static_path`, `html_css_files`, or `html_js_files`.

#### Source Document Conversion

When converting a PDF, Word document, or other existing source into Sphinx:

- Extract the complete readable structure before editing: title, sections,
   ordered steps, tables, deliverables, acceptance criteria, notes, links, and
   image references.
- Treat one-off extraction utilities as conversion tooling, not Sphinx runtime
   dependencies. Add them to the repository only when conversion is an ongoing,
   reproducible project workflow; otherwise record only packages required to
   rebuild the documentation site.
- Compare extracted content with existing repository documents and assets. Reuse
   authoritative local material where it expands or corrects the source; do not
   create disconnected duplicates.
- Split substantial source material into focused pages and connect every page
   through the root `toctree`. Preserve the source hierarchy and requirements,
   while adapting page boundaries for navigation rather than reproducing page
   breaks.
- Place images and other required assets inside the Sphinx source tree, normally
   under `_static` or an established image directory. Verify copied assets are
   non-empty and reference them with source-relative paths.
- Distinguish conversion from summarization: retain all operative requirements,
   deliverables, and acceptance criteria unless the user requests an abridged
   result. Avoid inventing missing content.

Consult the relevant official page in [Reference Map](#reference-map) before using unfamiliar directives, roles, builders, extension settings, or version-sensitive configuration.

**Complete when:** requested content is reachable, references target semantic objects, configuration matches installed dependencies, and source syntax follows adjacent files.

### 4. Build and Diagnose

Use the repository's documented command when it provides equivalent checks. Otherwise invoke Sphinx through the verified interpreter so the build cannot silently switch environments:

```text
<python> -m sphinx -M html <source-dir> <output-dir> --fail-on-warning --nitpicky
```

`-M` must appear before the source and output directories. Make-mode writes output under `<output-dir>/<builder>` and doctrees under `<output-dir>/doctrees`.

Diagnose warnings at their source:

- `toc.*`: repair missing, duplicate, excluded, untitled, or circular `toctree` entries.
- `ref.*`: correct the target, role, domain, label, or intersphinx mapping.
- `autodoc.*`: fix imports, package installation, signatures, or extension configuration.
- `image.not_readable` or `download.not_readable`: correct the source-relative path and ensure the asset is tracked.
- configuration or extension exceptions: rerun with `--show-traceback`; use `--verbose` when discovery or path behavior is unclear.

On Windows, match command syntax to the active shell. In Bash, use `/dev/null`
for discarded output rather than the Windows device name `NUL`, which creates a
real repository file. Avoid `!` inside double-quoted Bash command strings because
history expansion can rewrite validation scripts.

Use `--fresh-env` after changes to extension behavior, cross-reference inventory, or configuration when cached doctrees could hide the result. Use `--write-all` only when all output files must be rewritten; it does not re-read every source.

Suppress a warning only when it is understood, intentional, and narrowly scoped. Prefer fixing invalid documentation. For accepted unresolved references, use precise `nitpick_ignore` entries rather than disabling nitpicky mode.

**Complete when:** the relevant builder exits successfully with warnings treated as failures, or every remaining failure has a precise external blocker.

### 5. Validate the Requested Outputs

Run checks proportional to the change:

1. Build the primary requested format with `--fail-on-warning --nitpicky`.
2. Run the `linkcheck` builder for added or changed external links when network access is available:

   ```text
   sphinx-build -M linkcheck <source-dir> <output-dir> --fail-on-warning
   ```

3. Build each additional format affected by builder-specific configuration, such as `latexpdf` or `man`.
4. Open representative generated pages when navigation, converted content,
   images, theme, or custom CSS changed. Confirm page titles, sidebar or toctree
   links, semantic cross-references, and visible assets rather than treating a
   successful build as visual proof.
5. Confirm the output directory is excluded from version control and audit the
   worktree for accidental shell artifacts before finishing.

Distinguish broken links from transient timeouts, rate limits, authentication requirements, and unavailable networks. Configure `linkcheck_ignore`, authentication, redirects, retries, or timeouts only for verified environmental behavior.

**Complete when:** all affected builders pass, new pages appear in navigation, internal references resolve, and rendered output matches the request.

## Reference Map

Use the official Sphinx documentation as the source of truth for current behavior:

- [Using Sphinx](https://www.sphinx-doc.org/en/master/usage/index.html): guide index
- [Getting started](https://www.sphinx-doc.org/en/master/usage/quickstart.html): project structure, `toctree`, builds, domains, autodoc, and intersphinx
- [sphinx-build](https://www.sphinx-doc.org/en/master/man/sphinx-build.html): command syntax, builders, warnings, caching, and diagnostics
- [Configuration](https://www.sphinx-doc.org/en/master/usage/configuration.html): `conf.py` values and builder options
- [reStructuredText](https://www.sphinx-doc.org/en/master/usage/restructuredtext/index.html): default source syntax, roles, and directives
- [Markdown](https://www.sphinx-doc.org/en/master/usage/markdown.html): MyST-Parser setup
- [Cross-references](https://www.sphinx-doc.org/en/master/usage/referencing.html): document, label, object, and file references
- [Builders](https://www.sphinx-doc.org/en/master/usage/builders/index.html): output formats and specialized checks
- [Domains](https://www.sphinx-doc.org/en/master/usage/domains/index.html): language-specific object directives and roles
- [Extensions](https://www.sphinx-doc.org/en/master/usage/extensions/index.html): built-in and third-party extensions
- [HTML theming](https://www.sphinx-doc.org/en/master/usage/theming.html): themes and customization
- [Internationalization](https://www.sphinx-doc.org/en/master/usage/advanced/intl.html): gettext and translation workflows
- [Extending Sphinx](https://www.sphinx-doc.org/en/master/development/index.html): custom builders, directives, roles, nodes, and extensions

The `/en/master/` pages track the current development documentation. When maintaining a project pinned to an older Sphinx release, consult the matching version of the official documentation before changing version-sensitive behavior.

## Final Response

Report the source and configuration files changed, builders run, warning and link-check results, and the generated output location. State any unverified builder, external tool requirement, or network-dependent check explicitly.

## Example Requests

- "Set up Sphinx documentation for this project and build the HTML output."
- "Add an installation page to the Sphinx toctree and fix all build warnings."
- "Enable MyST Markdown in our Sphinx docs."
- "Generate Python API documentation with autodoc and intersphinx links."
- "Fix the unresolved references reported by sphinx-build."
- "Configure and validate PDF output for this Sphinx manual."
- "Convert this PDF into a navigable Sphinx HTML site using our `.venv`."