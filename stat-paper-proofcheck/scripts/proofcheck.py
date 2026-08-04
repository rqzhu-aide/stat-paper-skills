#!/usr/bin/env python3
"""Cross-platform deterministic support for stat-paper-proofcheck.

This script indexes LaTeX proof objects, audits cross-references, creates a
proof-check workspace, locks proof units to exact source lines, validates
line-by-line ledgers, reconciles canonical issues, and reports resumable state.
It uses only the Python standard library.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = 4
EVIDENCE_CONTRACT_VERSION = 3
METHOD_INTERFACE_SCHEMA_VERSION = 1
CLOSURE_CONTRACT_VERSION = 2
SKILL_NAME = "stat-paper-proofcheck"
SKILL_VERSION = "1.0"
MAX_UNIT_LINES = 100_000
FORMAL_ENVIRONMENTS = {
    "theorem",
    "lemma",
    "proposition",
    "corollary",
    "claim",
    "definition",
    "assumption",
    "remark",
}
TOKEN_RE = re.compile(r"\\(begin|end)\s*\{([^}]+)\}")
NEW_THEOREM_RE = re.compile(r"\\newtheorem\*?\s*\{([^}]+)\}")
INCLUDE_RE = re.compile(r"\\(?:input|include)\s*\{([^}]+)\}")
UNBRACED_INPUT_RE = re.compile(r"\\input\s+([^\s%{}]+)")
SUBFILE_RE = re.compile(r"\\subfile\s*\{([^}]+)\}")
IMPORT_RE = re.compile(r"\\(?:import|subimport)\s*\{([^}]+)\}\s*\{([^}]+)\}")
CLASS_RE = re.compile(
    r"\\(?:documentclass|LoadClass(?:WithOptions)?)"
    r"(?:\s*\[[^]]*\])?\s*\{([^}]+)\}"
)
PACKAGE_RE = re.compile(
    r"\\(?:usepackage|RequirePackage(?:WithOptions)?)"
    r"(?:\s*\[[^]]*\])?\s*\{([^}]+)\}"
)
INCLUSION_COMMAND_RE = re.compile(
    r"\\(?:input|include|subfile|import|subimport|documentclass|"
    r"LoadClass(?:WithOptions)?|usepackage|RequirePackage(?:WithOptions)?)\b"
)
FLS_SOURCE_SUFFIXES = {".tex", ".sty", ".cls", ".ltx", ".def", ".cfg", ".clo"}
LABEL_RE = re.compile(r"\\label\s*\{([^}]+)\}")
TEX_CONDITIONAL_LABEL_RE = re.compile(
    r"\\(?P<conditional>if[A-Za-z@]*)\b"
    r"|\\(?P<unless>unless)\b"
    r"|\\(?P<branch>else)\b"
    r"|\\(?P<end>fi)\b"
    r"|\\label\s*\{(?P<label>[^}]+)\}"
)
TEX_INLINE_VERB_RE = re.compile(
    r"\\(?:verb|Verb)\*?(?P<delimiter>[^\sA-Za-z])"
)
TEX_VERBATIM_BEGIN_RE = re.compile(
    r"\\begin\s*\{(?P<environment>"
    r"verbatim\*?|Verbatim\*?|BVerbatim|LVerbatim|SaveVerbatim|"
    r"lstlisting\*?|minted\*?|comment)\}"
)
TEX_DEFINITION_COMMAND_RE = re.compile(
    r"\\(?P<command>"
    r"newcommand|renewcommand|providecommand|DeclareRobustCommand|"
    r"newenvironment|renewenvironment|provideenvironment|"
    r"NewDocumentCommand|RenewDocumentCommand|ProvideDocumentCommand|"
    r"DeclareDocumentCommand|NewExpandableDocumentCommand|"
    r"RenewExpandableDocumentCommand|ProvideExpandableDocumentCommand|"
    r"DeclareExpandableDocumentCommand|NewDocumentEnvironment|"
    r"RenewDocumentEnvironment|ProvideDocumentEnvironment|"
    r"DeclareDocumentEnvironment|DeclareMathOperator|"
    r"DeclarePairedDelimiter|DeclarePairedDelimiterX|"
    r"DeclarePairedDelimiterXPP|newtheorem|renewtheorem|"
    r"cs_(?:new|set|gset)(?:_protected)?:[Nc]p?[nx]|"
    r"def|gdef|edef|xdef)\b\*?"
)
TEX_NEW_COMMAND_DEFINITIONS = {
    "newcommand",
    "renewcommand",
    "providecommand",
    "DeclareRobustCommand",
    "DeclareMathOperator",
}
TEX_NEW_ENVIRONMENT_DEFINITIONS = {
    "newenvironment",
    "renewenvironment",
    "provideenvironment",
}
TEX_DOCUMENT_COMMAND_DEFINITIONS = {
    "NewDocumentCommand",
    "RenewDocumentCommand",
    "ProvideDocumentCommand",
    "DeclareDocumentCommand",
    "NewExpandableDocumentCommand",
    "RenewExpandableDocumentCommand",
    "ProvideExpandableDocumentCommand",
    "DeclareExpandableDocumentCommand",
}
TEX_DOCUMENT_ENVIRONMENT_DEFINITIONS = {
    "NewDocumentEnvironment",
    "RenewDocumentEnvironment",
    "ProvideDocumentEnvironment",
    "DeclareDocumentEnvironment",
}
TEX_PAIRED_DELIMITER_DEFINITIONS = {
    "DeclarePairedDelimiter": 2,
    "DeclarePairedDelimiterX": 3,
    "DeclarePairedDelimiterXPP": 5,
}
TEX_THEOREM_DEFINITIONS = {"newtheorem", "renewtheorem"}
TEX_PRIMITIVE_DEFINITIONS = {"def", "gdef", "edef", "xdef"}
REF_RE = re.compile(
    r"\\(?:ref|eqref|autoref|pageref|cref|Cref)\*?\s*\{([^}]+)\}"
)
REFERENCE_COMMAND_RE = re.compile(
    r"\\(?P<command>ref|eqref|autoref|pageref|cref|Cref)\*?"
)
HYPERREF_COMMAND_RE = re.compile(r"\\(?P<command>hyperref)\*?")
SECTION_COMMAND_RE = re.compile(
    r"\\(?P<command>part|chapter|section|subsection|subsubsection)"
    r"\*?\s*\{(?P<title>[^}]*)\}"
)
DISPLAY_MATH_ENVIRONMENTS = {
    "align",
    "alignat",
    "displaymath",
    "dmath",
    "equation",
    "eqnarray",
    "flalign",
    "gather",
    "IEEEeqnarray",
    "multline",
    "subequations",
    "xalignat",
    "xxalignat",
}
CITE_RE = re.compile(
    r"\\(?:cite|citep|citet|citealp|citealt|parencite|textcite|autocite|footcite|smartcite|supercite)\*?(?:\[[^]]*\]){0,2}\s*\{([^}]+)\}"
)
CITATION_COMMAND_RE = re.compile(r"\\[A-Za-z]*cite[A-Za-z]*\*?")
STEP_ID_RE = re.compile(r"S[0-9]{3}(?:\.[0-9]+)?$")
PREMISE_ID_RE = re.compile(r"P[0-9]{3}$")
MOVE_ID_RE = re.compile(r"M[0-9]{3}$")
SIDE_CONDITION_ID_RE = re.compile(r"SC[0-9]{3}$")
CONCLUSION_ID_RE = re.compile(r"C[0-9]{3}$")
DEPENDENCY_USE_ID_RE = re.compile(r"D[0-9]{3}$")
ISSUE_ID_RE = re.compile(r"I-[0-9]{3}$")
INTERFACE_ID_RE = re.compile(r"MI-[0-9]{3}$")

STEP_STATUSES = {
    "verified",
    "conditionally_verified",
    "gap",
    "incorrect",
    "unclear",
    "not_checked",
    "non_substantive",
}
DEPENDENCY_STATUSES = {
    "verified",
    "conditional",
    "unchecked",
    "not_applicable",
    "gap",
    "incorrect",
    "unclear",
}
UNIT_STATUSES = {
    "verified",
    "conditionally_verified",
    "gap",
    "incorrect",
    "unclear",
    "not_checked",
}
ISSUE_SEVERITIES = {"S0", "S1", "S2", "S3"}
ISSUE_CONFIDENCES = {"high", "medium", "low"}
ISSUE_STATUSES = {"open", "resolved", "deferred"}
INTERFACE_KINDS = {
    "density_ratio",
    "regression",
    "conditional_expectation",
    "propensity",
    "weight",
    "operator",
    "optimization",
    "other",
}
INTERFACE_SPECIFICATION_STATUSES = {"clear", "ambiguous", "incomplete", "not_checked"}
TARGET_RELATION_VERDICTS = {
    "match",
    "conditional_match",
    "mismatch",
    "not_assessable",
    "not_checked",
}
IMPLEMENTATION_INSPECTION_STATUSES = {
    "inspected",
    "available_not_checked",
    "unavailable",
    "out_of_scope",
    "not_applicable",
}
IMPLEMENTATION_COMPARISON_VERDICTS = {
    "consistent",
    "inconsistent",
    "not_assessable",
    "not_checked",
    "not_applicable",
}
IMPLEMENTATION_INSPECTION_MODES = {"static", "executed", "both", "not_applicable"}
EXECUTION_PROVENANCE_STATUSES = {
    "matched",
    "not_matched",
    "not_checked",
    "not_applicable",
}
INTERFACE_FINDING_CLASSES = {
    "exposition_ambiguity",
    "estimator_target_mismatch",
    "implementation_mismatch",
    "reproducibility_gap",
    "scope_boundary",
}
INTERFACE_AFFECTED_LAYERS = {
    "specification",
    "derivation",
    "estimator_target",
    "implementation",
    "execution_provenance",
    "reproducibility",
}
STEP_KINDS = {
    "statement",
    "setup",
    "definition",
    "logic",
    "algebra",
    "inequality",
    "probability",
    "limit",
    "dependency",
    "conclusion",
    "other",
}
DEPENDENCY_KINDS = {"step", "internal_result", "external_result"}
ARGUMENT_STATUSES = {"valid", "conditional", "gap", "invalid", "unclear", "not_checked"}
PREMISE_ROLES = {"fact", "assumption", "definition"}
QUANTIFIER_KINDS = {"forall", "exists", "fixed"}
PREMISE_ORIGIN_KINDS = {
    "obligation",
    "prior_step",
    "internal_result",
    "external_result",
}
ATOMICITY_STATUSES = {
    "non_inferential",
    "single_move",
    "source_indivisible_chain",
}
RISK_ASPECTS = (
    "domain",
    "dimension",
    "sign",
    "constant",
    "rate",
    "probability",
    "quantifier",
    "limit",
)
RISK_STATUSES = {"passed", "not_applicable", "open", "failed", "unclear"}
NORMALIZATION_ASPECTS = (
    "quantifiers_and_domains",
    "probability_model",
    "hypotheses",
    "definitions",
    "conclusion",
    "uniformity",
    "regime",
    "constant_dependencies",
)
NORMALIZATION_STATUSES = {"checked", "not_applicable", "unclear"}
CONDITION_KINDS = {"side_condition", "dependency", "risk_check"}
DISCHARGE_KINDS = {"premise", "inference_move"}
REFUTATION_FAILURE_KINDS = {"counterexample", "contradiction"}
MOVE_FAILURE_KINDS = {
    "missing_premise",
    "unsupported_assertion",
    "invalid_rule",
    "source_ambiguity",
    *REFUTATION_FAILURE_KINDS,
}
ZERO_INPUT_FAILURE_KINDS = MOVE_FAILURE_KINDS - {"invalid_rule"}
MOVE_FAILURE_STEP_STATUSES = {
    "missing_premise": "gap",
    "unsupported_assertion": "gap",
    "invalid_rule": "incorrect",
    "source_ambiguity": "unclear",
    "counterexample": "incorrect",
    "contradiction": "incorrect",
}
FAILED_STEP_STATUSES = {"gap", "incorrect", "unclear"}
OBLIGATION_PREMISE_ROOTS = {
    "quantified_variables",
    "quantifier_scope",
    "probability_model",
    "hypotheses",
    "definitions",
    "uniformity",
    "regime",
    "constant_dependencies",
}
STEP_TO_DEPENDENCY_STATUS = {
    "verified": "verified",
    "conditionally_verified": "conditional",
    "gap": "gap",
    "incorrect": "incorrect",
    "unclear": "unclear",
    "not_checked": "unchecked",
    "non_substantive": "not_applicable",
}
STATEMENT_STATUSES = {
    "established",
    "conditional",
    "refuted",
    "not_established",
    "unclear",
    "not_assessed",
}
USE_STATUSES = {
    "sufficient",
    "conditional",
    "insufficient",
    "unclear",
    "not_checked",
    "not_applicable",
}
INDEPENDENT_CHECK_STATUSES = {"not_required", "pending", "agreed", "disagreed", "resolved"}
INDEPENDENCE_LEVELS = {
    "none",
    "fresh_context_same_model",
    "different_model",
    "independent_human",
}
PASS_STATUSES = {"not_checked", "completed", "completed_with_findings", "not_applicable"}
NON_PROOF_ENVIRONMENTS = {"definition", "assumption", "remark"}
COMPATIBILITY_STATUSES = {
    "passed",
    "not_applicable",
    "conditional",
    "gap",
    "incorrect",
    "unclear",
    "unchecked",
}
GLOBAL_CONSISTENCY_ASPECTS = (
    "source_resolution",
    "assumption_and_definition_propagation",
    "notation_domain_and_dimension",
    "constants_and_rates",
    "probability_events_and_conditioning",
    "quantifiers_uniformity_and_regime",
    "use_site_sufficiency",
    "issue_propagation",
)
GLOBAL_CONSISTENCY_STATUSES = {
    "passed",
    "not_applicable",
    "defect",
    "inconclusive",
}
CROSS_REFERENCE_REVIEW_STATUSES = {
    "passed",
    "defect",
    "inconclusive",
}
ISSUE_FINDING_STATUSES = {"defect", "inconclusive", "resolved"}


def configure_console_errors() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            continue
        try:
            reconfigure(errors="backslashreplace")
        except OSError:
            pass

def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def protocol_identity() -> dict[str, Any]:
    return {
        "skill_name": SKILL_NAME,
        "skill_version": SKILL_VERSION,
        "evidence_contract_version": EVIDENCE_CONTRACT_VERSION,
        "artifact_schema_version": SCHEMA_VERSION,
        "method_interface_schema_version": METHOD_INTERFACE_SCHEMA_VERSION,
        "closure_contract_version": CLOSURE_CONTRACT_VERSION,
        "validator_sha256": sha256_file(Path(__file__).resolve()),
    }



def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_sha256(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return sha256_text(payload)


def audit_state_manifest(root: Path, excluded: Path | None = None) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        if excluded is not None and path.resolve() == excluded.resolve():
            continue
        rows.append(
            {
                "file": path.relative_to(root).as_posix(),
                "sha256": sha256_file(path),
            }
        )
    return rows


def audit_state_sha256(root: Path, excluded: Path | None = None) -> str:
    return canonical_sha256(audit_state_manifest(root, excluded))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def read_lines(path: Path) -> list[str]:
    return read_text(path).splitlines()


def strip_latex_comment(line: str) -> str:
    for index, char in enumerate(line):
        if char != "%":
            continue
        backslashes = 0
        cursor = index - 1
        while cursor >= 0 and line[cursor] == "\\":
            backslashes += 1
            cursor -= 1
        if backslashes % 2 == 0:
            return line[:index]
    return line


def mask_tex_range(characters: list[str], start: int, end: int) -> None:
    for index in range(max(0, start), min(len(characters), end)):
        if characters[index] != "\n":
            characters[index] = " "


def skip_tex_whitespace(text: str, start: int) -> int:
    cursor = start
    while cursor < len(text) and text[cursor].isspace():
        cursor += 1
    return cursor


def consume_tex_control_sequence(text: str, start: int) -> int | None:
    if start >= len(text) or text[start] != "\\":
        return None
    cursor = start + 1
    if cursor >= len(text):
        return None
    if text[cursor].isalnum() or text[cursor] in "@_:":
        while cursor < len(text) and (
            text[cursor].isalnum() or text[cursor] in "@_:"
        ):
            cursor += 1
        return cursor
    return cursor + 1


def consume_balanced_tex_group(
    text: str, start: int, opening: str, closing: str
) -> int | None:
    if start >= len(text) or text[start] != opening:
        return None
    depth = 0
    cursor = start
    while cursor < len(text):
        char = text[cursor]
        if (
            char == "\\"
            and cursor + 1 < len(text)
            and text[cursor + 1] in {opening, closing}
        ):
            cursor += 2
            continue
        if char == opening:
            depth += 1
        elif char == closing:
            depth -= 1
            if depth == 0:
                return cursor + 1
        cursor += 1
    return None


def consume_tex_definition_target(text: str, start: int) -> int | None:
    cursor = skip_tex_whitespace(text, start)
    if cursor < len(text) and text[cursor] == "{":
        return consume_balanced_tex_group(text, cursor, "{", "}")
    return consume_tex_control_sequence(text, cursor)


def consume_tex_optional_arguments(text: str, start: int) -> int | None:
    cursor = skip_tex_whitespace(text, start)
    while cursor < len(text) and text[cursor] == "[":
        group_end = consume_balanced_tex_group(text, cursor, "[", "]")
        if group_end is None:
            return None
        cursor = skip_tex_whitespace(text, group_end)
    return cursor


def consume_tex_required_groups(
    text: str, start: int, count: int
) -> int | None:
    cursor = skip_tex_whitespace(text, start)
    for _ in range(count):
        group_end = consume_balanced_tex_group(text, cursor, "{", "}")
        if group_end is None:
            return None
        cursor = skip_tex_whitespace(text, group_end)
    return cursor


def tex_definition_end(text: str, match: re.Match[str]) -> int | None:
    command = match.group("command")
    cursor = match.end()
    if command in TEX_PRIMITIVE_DEFINITIONS or command.startswith("cs_"):
        cursor = skip_tex_whitespace(text, cursor)
        target_end = consume_tex_control_sequence(text, cursor)
        if target_end is None:
            return None
        cursor = target_end
        while cursor < len(text):
            if text[cursor] == "{":
                return consume_balanced_tex_group(text, cursor, "{", "}")
            cursor += 1
        return None

    target_end = consume_tex_definition_target(text, cursor)
    if target_end is None:
        return None
    cursor = target_end
    if command in TEX_NEW_COMMAND_DEFINITIONS:
        cursor = consume_tex_optional_arguments(text, cursor)
        if cursor is None:
            return None
        return consume_balanced_tex_group(text, cursor, "{", "}")
    if command in TEX_NEW_ENVIRONMENT_DEFINITIONS:
        cursor = consume_tex_optional_arguments(text, cursor)
        if cursor is None:
            return None
        begin_end = consume_balanced_tex_group(text, cursor, "{", "}")
        if begin_end is None:
            return None
        cursor = skip_tex_whitespace(text, begin_end)
        return consume_balanced_tex_group(text, cursor, "{", "}")
    if command in TEX_DOCUMENT_COMMAND_DEFINITIONS:
        cursor = skip_tex_whitespace(text, cursor)
        argument_spec_end = consume_balanced_tex_group(text, cursor, "{", "}")
        if argument_spec_end is None:
            return None
        cursor = skip_tex_whitespace(text, argument_spec_end)
        return consume_balanced_tex_group(text, cursor, "{", "}")
    if command in TEX_DOCUMENT_ENVIRONMENT_DEFINITIONS:
        cursor = skip_tex_whitespace(text, cursor)
        argument_spec_end = consume_balanced_tex_group(text, cursor, "{", "}")
        if argument_spec_end is None:
            return None
        return consume_tex_required_groups(text, argument_spec_end, 2)
    paired_group_count = TEX_PAIRED_DELIMITER_DEFINITIONS.get(command)
    if paired_group_count is not None:
        cursor = consume_tex_optional_arguments(text, cursor)
        if cursor is None:
            return None
        return consume_tex_required_groups(text, cursor, paired_group_count)
    if command in TEX_THEOREM_DEFINITIONS:
        cursor = consume_tex_optional_arguments(text, cursor)
        if cursor is None:
            return None
        title_end = consume_balanced_tex_group(text, cursor, "{", "}")
        if title_end is None:
            return None
        return consume_tex_optional_arguments(text, title_end)
    return None


def mask_nonexecuting_tex(text: str) -> str:
    characters = list(text)
    search_text = text
    cursor = 0
    while match := TEX_VERBATIM_BEGIN_RE.search(search_text, cursor):
        environment = match.group("environment")
        end_re = re.compile(rf"\\end\s*\{{{re.escape(environment)}\}}")
        end_match = end_re.search(search_text, match.end())
        end = end_match.end() if end_match is not None else len(search_text)
        mask_tex_range(characters, match.start(), end)
        cursor = end

    search_text = "".join(characters)
    cursor = 0
    while match := TEX_INLINE_VERB_RE.search(search_text, cursor):
        delimiter = match.group("delimiter")
        line_end = search_text.find("\n", match.end())
        if line_end < 0:
            line_end = len(search_text)
        closing = search_text.find(delimiter, match.end(), line_end)
        end = closing + 1 if closing >= 0 else line_end
        mask_tex_range(characters, match.start(), end)
        cursor = end

    search_text = "".join(characters)
    cursor = 0
    while match := TEX_DEFINITION_COMMAND_RE.search(search_text, cursor):
        end = tex_definition_end(search_text, match)
        if end is None:
            end = len(search_text)
        mask_tex_range(characters, match.start(), end)
        search_text = "".join(characters)
        cursor = end
    return "".join(characters)


def relative_or_absolute(path: Path, base: Path) -> str:
    try:
        return os.path.relpath(path.resolve(), base.resolve())
    except ValueError:
        return str(path.resolve())


def resolve_stored_path(value: str, base: Path) -> Path:
    candidate = Path(value)
    if candidate.is_absolute():
        return candidate.resolve()
    return (base / candidate).resolve()


def is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def is_enum_value(value: Any, allowed: Iterable[str]) -> bool:
    return isinstance(value, str) and value in allowed


def is_ignorable_marker_character(value: str) -> bool:
    codepoint = ord(value)
    return (
        unicodedata.category(value) == "Cf"
        or codepoint == 0x034F
        or 0x115F <= codepoint <= 0x1160
        or 0x17B4 <= codepoint <= 0x17B5
        or 0x180B <= codepoint <= 0x180F
        or codepoint in {0x2800, 0x3164, 0xFFA0}
        or 0xFE00 <= codepoint <= 0xFE0F
        or 0xE0100 <= codepoint <= 0xE01EF
    )


def normalized_marker(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    text = unicodedata.normalize("NFKC", value)
    text = "".join(
        char for char in text if not is_ignorable_marker_character(char)
    )
    text = text.strip().lower()
    previous: str | None = None
    while text != previous:
        previous = text
        wrapper = re.fullmatch(r"\\[a-z@]+\*?\s*\{(.*)\}", text, re.DOTALL)
        if wrapper is not None:
            text = wrapper.group(1).strip()
            continue
        while text and text[0] not in "\\{}" and (
            text[0].isspace() or unicodedata.category(text[0])[0] in {"P", "S"}
        ):
            text = text[1:]
        while text and text[-1] not in "\\{}" and (
            text[-1].isspace() or unicodedata.category(text[-1])[0] in {"P", "S"}
        ):
            text = text[:-1]
    return text


def is_explicit_absence(value: Any) -> bool:
    markers = {
        "none",
        "n/a",
        "not applicable",
        "not-applicable",
        "not_applicable",
    }
    if isinstance(value, str):
        return normalized_marker(value) in markers
    if isinstance(value, list) and value:
        return all(
            normalized_marker(item) in markers
            for item in value
        )
    return False


def is_unresolved_placeholder(value: Any) -> bool:
    unresolved_markers = {
        "unclear",
        "unknown",
        "unresolved",
        "tbd",
        "todo",
        "pending",
        "not checked",
        "not_checked",
    }
    marker = normalized_marker(value)
    return marker in unresolved_markers or bool(
        marker and re.match(r"^(?:todo|tbd)\b", marker)
    )


def is_forbidden_contract_placeholder(value: Any) -> bool:
    marker = normalized_marker(value)
    exact_unclear = (
        isinstance(value, str) and value.strip().lower() == "unclear"
    )
    prefix_match = (
        re.match(
            r"^(?:unclear|unknown|unresolved|pending|not[\s_-]*checked)",
            marker,
        )
        if marker
        else None
    )
    remainder = marker[prefix_match.end():].lstrip() if prefix_match else ""
    separator = remainder[:1]
    separator_name = unicodedata.name(separator, "") if separator else ""
    unresolved_prefix = bool(
        separator
        and (
            separator == ":"
            or "COLON" in separator_name
            or separator_name == "RATIO"
        )
    )
    return not exact_unclear and (
        is_unresolved_placeholder(value) or unresolved_prefix
    )


def is_substantive_string(value: Any) -> bool:
    return (
        is_nonempty_string(value)
        and not is_explicit_absence(value)
        and not is_unresolved_placeholder(value)
    )


def validate_string_list(
    value: Any,
    field: str,
    errors: list[str],
    *,
    substantive: bool = False,
    allow_empty: bool = False,
) -> list[str]:
    if not isinstance(value, list):
        errors.append(f"{field} must be a list")
        return []
    if not all(is_nonempty_string(item) for item in value):
        errors.append(f"{field} must contain only nonempty strings")
        return []
    if substantive and not all(is_substantive_string(item) for item in value):
        errors.append(
            f"{field} must contain substantive strings, not reserved placeholders"
        )
        return []
    if not allow_empty and not value:
        errors.append(f"{field} must not be empty")
    return value


def resolve_json_pointer(document: Any, pointer: Any) -> tuple[bool, Any]:
    if not isinstance(pointer, str) or not pointer.startswith("/"):
        return False, None
    current = document
    for raw_token in pointer[1:].split("/"):
        token = raw_token.replace("~1", "/").replace("~0", "~")
        if isinstance(current, dict):
            if token not in current:
                return False, None
            current = current[token]
        elif isinstance(current, list):
            if not token.isdigit():
                return False, None
            index = int(token)
            if index < 0 or index >= len(current):
                return False, None
            current = current[index]
        else:
            return False, None
    return True, current


def validate_aspect_matrix(
    value: Any,
    field: str,
    required_aspects: Iterable[str],
    allowed_statuses: set[str],
    final: bool,
    errors: list[str],
) -> dict[str, str]:
    required = tuple(required_aspects)
    required_set = set(required)
    if not isinstance(value, list):
        errors.append(f"{field} must be a list")
        return {}

    statuses: dict[str, str] = {}
    duplicates: set[str] = set()
    unexpected: set[str] = set()
    for index, record in enumerate(value, 1):
        prefix = f"{field}[{index}]"
        if not isinstance(record, dict):
            errors.append(f"{prefix} must be an object")
            continue
        aspect = record.get("aspect")
        status = record.get("status")
        if not is_nonempty_string(aspect):
            errors.append(f"{prefix}.aspect must be a nonempty string")
            continue
        if aspect not in required_set:
            unexpected.add(aspect)
            errors.append(f"{prefix}.aspect is invalid: {aspect!r}")
        elif aspect in statuses:
            duplicates.add(aspect)
        else:
            statuses[aspect] = status
        if not is_enum_value(status, allowed_statuses):
            errors.append(f"{prefix}.status is invalid: {status!r}")
        if not is_substantive_string(record.get("evidence")):
            errors.append(
                f"{prefix}.evidence must be a nonempty string and substantive, "
                "not a reserved placeholder"
            )

    missing = required_set - set(statuses)
    if final and (missing or duplicates or unexpected):
        details: list[str] = []
        if missing:
            details.append("missing " + ", ".join(sorted(missing)))
        if duplicates:
            details.append("duplicate " + ", ".join(sorted(duplicates)))
        if unexpected:
            details.append("unexpected " + ", ".join(sorted(unexpected)))
        errors.append(
            f"{field} must contain each required aspect exactly once"
            + (": " + "; ".join(details) if details else "")
        )
    return statuses


def load_json_object(path: Path, description: str) -> tuple[dict[str, Any], list[str]]:
    try:
        data = json.loads(read_text(path))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return {}, [f"Cannot read {description} {path}: {exc}"]
    if not isinstance(data, dict):
        return {}, [f"{description} must be a JSON object: {path}"]
    return data, []


def locked_span(
    source: Path, start: int, end: int, base: Path, *, role: str | None = None
) -> dict[str, Any]:
    lines = read_lines(source)
    selected = lines[start - 1 : end]
    record: dict[str, Any] = {
        "file": relative_or_absolute(source, base),
        "start_line": start,
        "end_line": end,
        "sha256": sha256_text("\n".join(selected)),
    }
    if role is not None:
        record["role"] = role
    return record


def validate_locked_span(
    span: Any,
    base: Path,
    prefix: str,
    errors: list[str],
    *,
    require_role: bool = False,
) -> None:
    if not isinstance(span, dict):
        errors.append(f"{prefix} must be an object")
        return
    if require_role and not is_nonempty_string(span.get("role")):
        errors.append(f"{prefix}.role must be a nonempty string")
    file_value = span.get("file")
    start = span.get("start_line")
    end = span.get("end_line")
    digest = span.get("sha256")
    if not is_nonempty_string(file_value) or not is_int(start) or not is_int(end):
        errors.append(f"{prefix} needs file, integer start_line, and integer end_line")
        return
    if start < 1 or end < start or end - start + 1 > MAX_UNIT_LINES:
        errors.append(f"{prefix} has invalid range {start}-{end}")
        return
    source = resolve_stored_path(file_value, base)
    if not source.is_file():
        errors.append(f"{prefix} source file not found: {source}")
        return
    lines = read_lines(source)
    if end > len(lines):
        errors.append(f"{prefix} ends at {end}, but source has {len(lines)} lines")
        return
    current = sha256_text("\n".join(lines[start - 1 : end]))
    if not is_nonempty_string(digest) or digest != current:
        errors.append(f"{prefix} source drift: SHA-256 does not match")


def resolved_span_metadata(span: Any, base: Path) -> dict[str, Any] | None:
    if not isinstance(span, dict):
        return None
    if not is_nonempty_string(span.get("file")):
        return None
    if not is_int(span.get("start_line")) or not is_int(span.get("end_line")):
        return None
    return {
        "file": str(resolve_stored_path(span["file"], base)),
        "start_line": span["start_line"],
        "end_line": span["end_line"],
        "role": span.get("role"),
    }


def locked_span_contains_label(span: Any, base: Path, label: str) -> bool:
    metadata = resolved_span_metadata(span, base)
    if metadata is None:
        return False
    source = Path(metadata["file"])
    start = metadata["start_line"]
    end = metadata["end_line"]
    if not source.is_file() or start < 1 or end < start:
        return False
    lines = read_lines(source)
    if end > len(lines):
        return False
    labels: set[str] = set()
    conditional_stack: list[bool | None] = []
    unless_pending = False
    clean_text = mask_nonexecuting_tex(
        "\n".join(strip_latex_comment(line) for line in lines[:end])
    )
    for line_number, clean in enumerate(clean_text.split("\n"), 1):
        for token in TEX_CONDITIONAL_LABEL_RE.finditer(clean):
            conditional = token.group("conditional")
            if conditional is not None:
                if unless_pending:
                    conditional_stack.append(None)
                elif conditional == "iftrue":
                    conditional_stack.append(True)
                elif conditional == "iffalse":
                    conditional_stack.append(False)
                else:
                    conditional_stack.append(None)
                unless_pending = False
            elif token.group("unless") is not None:
                unless_pending = True
            elif token.group("branch") is not None and conditional_stack:
                state = conditional_stack[-1]
                conditional_stack[-1] = None if state is None else not state
            elif token.group("end") is not None and conditional_stack:
                conditional_stack.pop()
            elif (
                token.group("label") is not None
                and start <= line_number <= end
                and not unless_pending
                and all(state is True for state in conditional_stack)
            ):
                labels.add(token.group("label"))
    return label in labels


def find_cycle(graph: dict[str, set[str]]) -> list[str] | None:
    state: dict[str, int] = {}
    stack: list[str] = []

    def visit(node: str) -> list[str] | None:
        state[node] = 1
        stack.append(node)
        for dependency in sorted(graph.get(node, set())):
            if dependency not in graph:
                continue
            if state.get(dependency, 0) == 0:
                cycle = visit(dependency)
                if cycle:
                    return cycle
            elif state.get(dependency) == 1:
                index = stack.index(dependency)
                return stack[index:] + [dependency]
        stack.pop()
        state[node] = 2
        return None

    for node in sorted(graph):
        if state.get(node, 0) == 0:
            cycle = visit(node)
            if cycle:
                return cycle
    return None


def split_reference_keys(raw: str) -> list[str]:
    return [item.strip() for item in raw.split(",") if item.strip()]


def mask_latex_comments(text: str) -> str:
    """Mask comments while preserving offsets and line endings."""
    characters = list(text)
    offset = 0
    for line in text.splitlines(keepends=True):
        clean = strip_latex_comment(line)
        if len(clean) < len(line):
            mask_tex_range(characters, offset + len(clean), offset + len(line))
        offset += len(line)
    return "".join(characters)


def source_line_column(text: str, offset: int, start_line: int = 1) -> tuple[int, int]:
    line = start_line + text.count("\n", 0, offset)
    last_newline = text.rfind("\n", 0, offset)
    column = offset + 1 if last_newline < 0 else offset - last_newline
    return line, column


def scan_reference_occurrences(
    text: str,
    path: Path,
    base: Path,
    *,
    start_line: int = 1,
    structural_context: str = "source",
) -> tuple[list[dict[str, Any]], list[str]]:
    """Return exact static reference occurrences, including bracket hyperrefs."""
    masked = mask_nonexecuting_tex(mask_latex_comments(text))
    matches = sorted(
        [*REFERENCE_COMMAND_RE.finditer(masked), *HYPERREF_COMMAND_RE.finditer(masked)],
        key=lambda match: match.start(),
    )
    relative_file = relative_or_absolute(path, base)
    occurrences: list[dict[str, Any]] = []
    warnings: list[str] = []
    for match in matches:
        command = match.group("command")
        cursor = skip_tex_whitespace(masked, match.end())
        opening, closing = ("[", "]") if command == "hyperref" else ("{", "}")
        group_end = consume_balanced_tex_group(masked, cursor, opening, closing)
        line, column = source_line_column(text, match.start(), start_line)
        if group_end is None:
            warnings.append(
                f"Malformed or dynamic \\{command} requires manual review: "
                f"{relative_file}:{line}:{column}"
            )
            continue
        raw_targets = text[cursor + 1 : group_end - 1]
        targets = split_reference_keys(raw_targets)
        if command == "hyperref":
            display_cursor = skip_tex_whitespace(masked, group_end)
            if consume_balanced_tex_group(masked, display_cursor, "{", "}") is None:
                warnings.append(
                    "Malformed or dynamic \\hyperref display text requires manual "
                    f"review: {relative_file}:{line}:{column}"
                )
        if not targets:
            warnings.append(
                f"Empty \\{command} target requires manual review: "
                f"{relative_file}:{line}:{column}"
            )
        for key_index, target in enumerate(targets, 1):
            dynamic = '\\' in target or '#' in target
            if dynamic:
                warnings.append(
                    f"Dynamic \\{command} target requires manual review: "
                    f"{relative_file}:{line}:{column}: {target}"
                )
            identity = {
                "file": relative_file,
                "line": line,
                "column": column,
                "command": command,
                "target": target,
                "key_index": key_index,
            }
            occurrences.append(
                {
                    "occurrence_id": "R-" + canonical_sha256(identity)[:16],
                    "command": command,
                    "target": target,
                    "file": relative_file,
                    "line": line,
                    "column": column,
                    "structural_context": structural_context,
                    "resolution_status": "dynamic" if dynamic else "unresolved",
                    "owner_unit_id": None,
                    "owner_region": None,
                }
            )
    return occurrences, warnings


def scan_label_occurrences(
    text: str,
    path: Path,
    base: Path,
    *,
    start_line: int = 1,
) -> list[dict[str, Any]]:
    masked = mask_nonexecuting_tex(mask_latex_comments(text))
    relative_file = relative_or_absolute(path, base)
    result: list[dict[str, Any]] = []
    for match in LABEL_RE.finditer(masked):
        line, column = source_line_column(text, match.start(), start_line)
        result.append(
            {
                "target": match.group(1).strip(),
                "file": relative_file,
                "line": line,
                "column": column,
            }
        )
    return result


def proof_optional_title_span(
    block: list[str], start_line: int = 1
) -> dict[str, Any] | None:
    text = "\n".join(block)
    masked = mask_latex_comments(text)
    begin = re.search(r"\\begin\s*\{proof\}", masked)
    if begin is None:
        return None
    cursor = skip_tex_whitespace(masked, begin.end())
    end = consume_balanced_tex_group(masked, cursor, "[", "]")
    if end is None:
        return None
    first_line, first_column = source_line_column(
        text, cursor + 1, start_line
    )
    last_offset = max(cursor + 1, end - 2)
    last_line, last_column = source_line_column(
        text, last_offset, start_line
    )
    return {
        "text": text[cursor + 1 : end - 1],
        "start_line": first_line,
        "start_column": first_column,
        "end_line": last_line,
        "end_column": last_column,
    }


def proof_optional_title(block: list[str]) -> str | None:
    span = proof_optional_title_span(block)
    return span.get("text") if isinstance(span, dict) else None


def occurrence_in_title(
    occurrence: dict[str, Any], title_span: dict[str, Any] | None
) -> bool:
    if not isinstance(title_span, dict):
        return False
    line = occurrence.get("line")
    column = occurrence.get("column")
    if not is_int(line) or not is_int(column):
        return False
    start = (title_span["start_line"], title_span["start_column"])
    end = (title_span["end_line"], title_span["end_column"])
    return start <= (line, column) <= end


def scan_span_evidence(
    path: Path,
    start_line: int,
    end_line: int,
    base: Path,
    *,
    structural_context: str = "proof_body",
) -> dict[str, Any]:
    lines = read_lines(path)
    if not (1 <= start_line <= end_line <= len(lines)):
        raise ValueError(f"Invalid source span {path}:{start_line}-{end_line}")
    selected = lines[start_line - 1 : end_line]
    text = "\n".join(selected)
    occurrences, warnings = scan_reference_occurrences(
        text,
        path,
        base,
        start_line=start_line,
        structural_context=structural_context,
    )
    citations: list[str] = []
    for line_number, line in enumerate(selected, start_line):
        clean = strip_latex_comment(line)
        handled_citations: set[int] = set()
        for match in CITE_RE.finditer(clean):
            handled_citations.add(match.start())
            citations.extend(split_reference_keys(match.group(1)))
        for match in CITATION_COMMAND_RE.finditer(clean):
            if match.start() not in handled_citations:
                warnings.append(
                    "Unsupported citation command requires manual review: "
                    f"{relative_or_absolute(path, base)}:{line_number}: "
                    f"{match.group(0)}"
                )
    return {
        "reference_occurrences": occurrences,
        "dependencies": sorted({row["target"] for row in occurrences}),
        "citations": sorted(set(citations)),
        "warnings": warnings,
    }


def scan_unit_statement_evidence(
    unit: dict[str, Any], base: Path
) -> dict[str, Any]:
    statement = unit.get("statement")
    if not isinstance(statement, dict):
        raise ValueError("Invalid reviewed statement range")
    path = resolve_stored_path(str(statement.get("file")), base)
    start_line = statement.get("start_line")
    end_line = statement.get("end_line")
    if not is_int(start_line) or not is_int(end_line):
        raise ValueError("Invalid reviewed statement range")
    return scan_span_evidence(
        path,
        start_line,
        end_line,
        base,
        structural_context="formal_statement",
    )


def display_math_spans(lines: list[str]) -> list[dict[str, Any]]:
    text = "\n".join(lines)
    masked = mask_nonexecuting_tex(mask_latex_comments(text))
    stack: list[dict[str, Any]] = []
    spans: list[dict[str, Any]] = []
    for token in TOKEN_RE.finditer(masked):
        action, environment = token.group(1), token.group(2)
        if environment.rstrip("*") not in DISPLAY_MATH_ENVIRONMENTS:
            continue
        if action == "begin":
            stack.append({"environment": environment, "offset": token.start()})
            continue
        match_index = next(
            (
                index
                for index in range(len(stack) - 1, -1, -1)
                if stack[index]["environment"] == environment
            ),
            None,
        )
        if match_index is None:
            continue
        opened = stack.pop(match_index)
        start_line, start_column = source_line_column(text, opened["offset"])
        end_offset = max(token.start(), token.end() - 1)
        end_line, end_column = source_line_column(text, end_offset)
        spans.append(
            {
                "environment": environment,
                "start_line": start_line,
                "start_column": start_column,
                "end_line": end_line,
                "end_column": end_column,
                "length": token.end() - opened["offset"],
            }
        )
    return spans


def proof_heading_gaps(
    source_lines: dict[Path, list[str]],
    units: Iterable[dict[str, Any]],
    base: Path,
) -> list[dict[str, Any]]:
    resolved_source_lines = {
        path.resolve(): lines for path, lines in source_lines.items()
    }
    barriers: dict[Path, list[tuple[int, int]]] = defaultdict(list)
    for unit in units:
        for region_name in ("statement", "proof"):
            region = unit.get(region_name)
            if not isinstance(region, dict):
                continue
            file_value = region.get("file")
            start_line = region.get("start_line")
            end_line = region.get("end_line")
            if (
                not is_nonempty_string(file_value)
                or not is_int(start_line)
                or not is_int(end_line)
            ):
                continue
            path = resolve_stored_path(file_value, base).resolve()
            if path in resolved_source_lines:
                barriers[path].append((start_line, end_line))

    gaps: list[dict[str, Any]] = []
    for path, lines in resolved_source_lines.items():
        barriers[path].extend(proof_environment_spans(path))
        merged_barriers: list[list[int]] = []
        for start_line, end_line in sorted(barriers[path]):
            if start_line > end_line:
                continue
            if merged_barriers and start_line <= merged_barriers[-1][1] + 1:
                merged_barriers[-1][1] = max(
                    merged_barriers[-1][1], end_line
                )
            else:
                merged_barriers.append([start_line, end_line])

        headings: list[dict[str, Any]] = []
        text = "\n".join(lines)
        masked = mask_nonexecuting_tex(mask_latex_comments(text))
        for match in SECTION_COMMAND_RE.finditer(masked):
            line_number, _ = source_line_column(text, match.start())
            headings.append(
                {
                    "line": line_number,
                    "title": match.group("title"),
                }
            )
        for heading_index, heading in enumerate(headings):
            if not re.search(r"\bproofs?\b", heading["title"], re.IGNORECASE):
                continue
            next_heading = (
                headings[heading_index + 1]
                if heading_index + 1 < len(headings)
                else None
            )
            section_end = (
                next_heading["line"] - 1
                if next_heading is not None
                else len(lines)
            )
            cursor = heading["line"] + 1
            for barrier_start, barrier_end in merged_barriers:
                if barrier_end < cursor:
                    continue
                if barrier_start > section_end:
                    break
                if cursor < barrier_start:
                    gaps.append(
                        {
                            "file": relative_or_absolute(path, base),
                            "start_line": cursor,
                            "end_line": min(barrier_start - 1, section_end),
                            "heading_line": heading["line"],
                        }
                    )
                cursor = max(cursor, barrier_end + 1)
                if cursor > section_end:
                    break
            if cursor <= section_end:
                gaps.append(
                    {
                        "file": relative_or_absolute(path, base),
                        "start_line": cursor,
                        "end_line": section_end,
                        "heading_line": heading["line"],
                    }
                )
    return gaps


def build_unowned_label_support_index(
    source_lines: dict[Path, list[str]],
    units: Iterable[dict[str, Any]],
    label_owners: dict[str, dict[str, Any]],
    base: Path,
) -> dict[str, dict[str, Any]]:
    resolved_source_lines = {
        path.resolve(): lines for path, lines in source_lines.items()
    }
    gaps_by_file: dict[Path, list[dict[str, Any]]] = defaultdict(list)
    for gap in proof_heading_gaps(resolved_source_lines, units, base):
        path = resolve_stored_path(gap["file"], base).resolve()
        gaps_by_file[path].append(gap)
    math_spans = {
        path: display_math_spans(lines)
        for path, lines in resolved_source_lines.items()
    }

    result: dict[str, dict[str, Any]] = {}
    for target, owner in sorted(label_owners.items()):
        locations = owner.get("locations")
        if owner.get("status") != "unowned" or not isinstance(locations, list):
            continue
        if len(locations) != 1 or not isinstance(locations[0], dict):
            continue
        location = locations[0]
        file_value = location.get("file")
        line = location.get("line")
        column = location.get("column")
        if (
            not is_nonempty_string(file_value)
            or not is_int(line)
            or not is_int(column)
        ):
            continue
        path = resolve_stored_path(file_value, base).resolve()
        if path not in resolved_source_lines:
            continue
        containing_blocks = [
            block
            for block in math_spans.get(path, [])
            if (block["start_line"], block["start_column"])
            <= (line, column)
            <= (block["end_line"], block["end_column"])
        ]
        if not containing_blocks:
            continue
        block = min(containing_blocks, key=lambda item: item["length"])
        containing_gaps = [
            gap
            for gap in gaps_by_file.get(path, [])
            if gap["start_line"] <= block["start_line"]
            and block["end_line"] <= gap["end_line"]
        ]
        if not containing_gaps:
            continue
        gap = max(
            containing_gaps,
            key=lambda item: (item["heading_line"], item["start_line"]),
        )
        selected = resolved_source_lines[path][
            gap["start_line"] - 1 : block["end_line"]
        ]
        occurrences, _ = scan_reference_occurrences(
            "\n".join(selected),
            path,
            base,
            start_line=gap["start_line"],
            structural_context="unowned_support_region",
        )
        occurrences = [
            occurrence
            for occurrence in occurrences
            if (occurrence["line"], occurrence["column"])
            <= (block["end_line"], block["end_column"])
        ]
        result[target] = {
            "reference_occurrences": occurrences,
            "region": {
                "file": relative_or_absolute(path, base),
                "start_line": gap["start_line"],
                "end_line": block["end_line"],
            },
        }
    return result


def resolve_candidate_internal_dependencies(
    unit_id: str,
    occurrences: Iterable[dict[str, Any]],
    label_owners: dict[str, dict[str, Any]],
    support_index: dict[str, dict[str, Any]],
) -> list[str]:
    pending = [
        occurrence.get("target")
        for occurrence in occurrences
        if isinstance(occurrence, dict)
        and is_nonempty_string(occurrence.get("target"))
    ]
    visited_labels: set[str] = set()
    dependencies: set[str] = set()
    while pending:
        target = pending.pop()
        if target in visited_labels:
            continue
        visited_labels.add(target)
        owner = label_owners.get(target)
        if not isinstance(owner, dict):
            continue
        owner_unit_id = owner.get("owner_unit_id")
        if owner.get("status") == "unique" and is_nonempty_string(owner_unit_id):
            if owner_unit_id != unit_id:
                dependencies.add(owner_unit_id)
            continue
        if owner.get("status") != "unowned":
            continue
        support = support_index.get(target)
        if not isinstance(support, dict):
            continue
        for occurrence in support.get("reference_occurrences", []):
            if isinstance(occurrence, dict) and is_nonempty_string(
                occurrence.get("target")
            ):
                pending.append(occurrence["target"])
    return sorted(dependencies)


def bounded_proof_region(
    path: Path, anchor_line: int, *, max_heading_distance: int = 4
) -> dict[str, Any] | None:
    """Conservatively bound an appendix proof headed immediately after an anchor."""
    lines = read_lines(path)
    levels = {
        "part": 0,
        "chapter": 1,
        "section": 2,
        "subsection": 3,
        "subsubsection": 4,
    }
    headings: list[dict[str, Any]] = []
    for line_number, raw_line in enumerate(lines, 1):
        match = SECTION_COMMAND_RE.search(strip_latex_comment(raw_line))
        if match is not None:
            headings.append(
                {
                    "line": line_number,
                    "level": levels[match.group("command")],
                    "title": match.group("title"),
                }
            )
    candidates = [
        heading
        for heading in headings
        if anchor_line <= heading["line"] <= anchor_line + max_heading_distance
        and re.search(r"\bproof\b", heading["title"], re.IGNORECASE)
    ]
    if len(candidates) != 1:
        return None
    heading = candidates[0]
    later_boundary = next(
        (
            other
            for other in headings
            if other["line"] > heading["line"]
            and other["level"] <= heading["level"]
        ),
        None,
    )
    end_line = later_boundary["line"] - 1 if later_boundary else len(lines)
    if later_boundary is not None:
        while end_line > anchor_line and (
            not lines[end_line - 1].strip()
            or re.fullmatch(
                r"\s*\\(?:phantomsection|label\s*\{[^}]+\})\s*",
                strip_latex_comment(lines[end_line - 1]),
            )
        ):
            end_line -= 1
    else:
        while end_line > anchor_line and not lines[end_line - 1].strip():
            end_line -= 1
    if end_line < heading["line"]:
        return None
    return {
        "start_line": anchor_line,
        "end_line": end_line,
        "heading_line": heading["line"],
        "heading_title": heading["title"],
    }


def canonical_location(value: Any) -> dict[str, Any] | None:
    if value is None:
        return None
    if not isinstance(value, dict):
        return {}
    return {
        "file": value.get("file"),
        "start_line": value.get("start_line"),
        "end_line": value.get("end_line"),
    }


def source_span_sha256(path: Path, start_line: int, end_line: int) -> str:
    lines = read_lines(path)
    if not (1 <= start_line <= end_line <= len(lines)):
        raise ValueError(f"Invalid source span {path}:{start_line}-{end_line}")
    return sha256_text("\n".join(lines[start_line - 1 : end_line]))


def proof_environment_spans(path: Path) -> set[tuple[int, int]]:
    spans: set[tuple[int, int]] = set()
    stack: list[int] = []
    for line_number, raw_line in enumerate(read_lines(path), 1):
        clean = strip_latex_comment(raw_line)
        for token in TOKEN_RE.finditer(clean):
            action, environment = token.group(1), token.group(2)
            if environment != "proof":
                continue
            if action == "begin":
                stack.append(line_number)
            elif stack:
                spans.add((stack.pop(), line_number))
    return spans


def proof_span_has_safe_boundary(
    path: Path, start_line: int, end_line: int
) -> bool:
    if (start_line, end_line) in proof_environment_spans(path):
        return True
    region = bounded_proof_region(path, start_line)
    return bool(
        isinstance(region, dict)
        and region.get("start_line") == start_line
        and region.get("end_line") == end_line
    )


def span_contains_location(
    span: Any,
    file_value: Any,
    line_value: Any,
    base: Path | None = None,
) -> bool:
    same_file = bool(
        isinstance(span, dict) and span.get("file") == file_value
    )
    if (
        base is not None
        and isinstance(span, dict)
        and is_nonempty_string(span.get("file"))
        and is_nonempty_string(file_value)
    ):
        same_file = (
            resolve_stored_path(span["file"], base)
            == resolve_stored_path(file_value, base)
        )
    return bool(
        isinstance(span, dict)
        and same_file
        and is_int(span.get("start_line"))
        and is_int(span.get("end_line"))
        and is_int(line_value)
        and span["start_line"] <= line_value <= span["end_line"]
    )


def reviewed_label_owners(
    cross_references: dict[str, Any],
    unit_inventory: dict[str, dict[str, Any]],
    base: Path,
) -> dict[str, dict[str, Any]]:
    owners: dict[str, dict[str, Any]] = {}
    labels = cross_references.get("labels")
    if not isinstance(labels, dict):
        return owners
    for target, raw_locations in sorted(labels.items()):
        locations = (
            raw_locations
            if isinstance(raw_locations, list)
            else []
        )
        if len(locations) != 1:
            owners[target] = {
                "status": "duplicate",
                "owner_unit_id": None,
                "owner_region": None,
                "locations": locations,
            }
            continue
        location = locations[0] if isinstance(locations[0], dict) else {}
        candidates: list[tuple[str, str]] = []
        for unit_id, unit in unit_inventory.items():
            for region in ("statement", "proof"):
                if span_contains_location(
                    unit.get(region),
                    location.get("file"),
                    location.get("line"),
                    base,
                ):
                    candidates.append((unit_id, region))
        unique_candidates = sorted(set(candidates))
        if len(unique_candidates) == 1:
            owner_unit_id, owner_region = unique_candidates[0]
            status = "unique"
        elif unique_candidates:
            owner_unit_id, owner_region, status = None, None, "ambiguous"
        else:
            owner_unit_id, owner_region, status = None, None, "unowned"
        owners[target] = {
            "status": status,
            "owner_unit_id": owner_unit_id,
            "owner_region": owner_region,
            "locations": locations,
        }
    return owners


def reviewed_span_evidence(
    unit_id: str,
    unit: dict[str, Any],
    base: Path,
    label_owners: dict[str, dict[str, Any]],
    support_index: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    statement_evidence = scan_unit_statement_evidence(unit, base)
    proof = unit.get("proof")
    if not isinstance(proof, dict):
        evidence = {
            "reference_occurrences": [],
            "dependencies": [],
            "citations": [],
            "warnings": [],
        }
        title_span = None
    else:
        path = resolve_stored_path(str(proof.get("file")), base)
        start_line = proof.get("start_line")
        end_line = proof.get("end_line")
        if not is_int(start_line) or not is_int(end_line):
            raise ValueError(f"Invalid reviewed proof range for {unit_id}")
        evidence = scan_span_evidence(path, start_line, end_line, base)
        lines = read_lines(path)[start_line - 1 : end_line]
        title_span = (
            proof_optional_title_span(lines, start_line)
            if (start_line, end_line) in proof_environment_spans(path)
            else None
        )
        title = (
            title_span.get("text")
            if isinstance(title_span, dict)
            else None
        )
        if title is not None:
            _, title_warnings = scan_reference_occurrences(
                title,
                path,
                base,
                start_line=title_span["start_line"],
                structural_context="proof_header",
            )
            evidence["warnings"].extend(title_warnings)
    for occurrence in evidence["reference_occurrences"]:
        if occurrence_in_title(occurrence, title_span):
            occurrence["structural_context"] = "proof_header"
        owner = label_owners.get(occurrence.get("target"))
        if owner is None:
            occurrence["resolution_status"] = "missing"
            continue
        occurrence["resolution_status"] = owner.get("status")
        occurrence["owner_unit_id"] = owner.get("owner_unit_id")
        occurrence["owner_region"] = owner.get("owner_region")
    evidence["candidate_internal_dependencies"] = (
        resolve_candidate_internal_dependencies(
            unit_id,
            [
                *statement_evidence["reference_occurrences"],
                *evidence["reference_occurrences"],
            ],
            label_owners,
            support_index or {},
        )
    )
    evidence["warnings"].extend(statement_evidence["warnings"])
    evidence["warnings"] = sorted(set(evidence["warnings"]))
    return evidence


def last_substantive_line(path: Path, start_line: int, end_line: int) -> int:
    lines = read_lines(path)
    for line_number in range(min(end_line, len(lines)), start_line - 1, -1):
        clean = strip_latex_comment(lines[line_number - 1]).strip()
        if clean and not re.fullmatch(r"\\end\s*\{proof\}", clean):
            return line_number
    return start_line


def discover_source_closure(
    root: Path,
    *,
    additional_files: Iterable[Path] | None = None,
    fls_file: Path | None = None,
    project_root: Path | None = None,
) -> dict[str, Any]:
    root = root.resolve()
    project_root = (project_root or root.parent).resolve()
    ordered: list[Path] = []
    visited: set[Path] = set()
    active: set[Path] = set()
    warnings: list[str] = []
    outside_project_inputs: set[str] = set()

    def local_candidates(
        requested: str, suffix: str, source: Path, line_number: int
    ) -> list[Path]:
        raw = requested.strip()
        if "\\" in raw or "#" in raw:
            warnings.append(
                "Dynamic class or package requires manual review: "
                f"{source}:{line_number}: {raw}"
            )
            return []
        requested_path = Path(raw)
        explicit_local_reference = (
            requested_path.is_absolute()
            or raw.startswith("./")
            or requested_path.parent != Path(".")
            or requested_path.suffix != ""
        )
        value = requested_path
        if value.suffix == "":
            value = value.with_suffix(suffix)
        if value.is_absolute():
            candidates = [value.resolve()] if value.is_file() else []
        else:
            search_roots = [source.parent.resolve()]
            if project_root not in search_roots:
                search_roots.append(project_root)
            candidates = []
            for search_root in search_roots:
                candidate = (search_root / value).resolve()
                if candidate.is_file() and candidate not in candidates:
                    candidates.append(candidate)
        if len(candidates) > 1:
            warnings.append(
                "Ambiguous local class or package resolution requires manual review: "
                f"{source}:{line_number}: {raw}: "
                + ", ".join(str(item) for item in candidates)
            )
        if not candidates and explicit_local_reference:
            warnings.append(
                f"Explicit local class or package not found: {source}:{line_number}: {raw}"
            )
        return candidates

    def visit(path: Path) -> None:
        path = path.resolve()
        if path in active:
            warnings.append(f"Include cycle detected at {path}")
            return
        if path in visited:
            return
        if not path.is_file():
            warnings.append(f"Included file not found: {path}")
            return

        visited.add(path)
        active.add(path)
        ordered.append(path)
        try:
            lines = read_lines(path)
        except UnicodeError as exc:
            warnings.append(f"Cannot decode {path} as UTF-8: {exc}")
            active.remove(path)
            return

        for line_number, line in enumerate(lines, 1):
            clean = strip_latex_comment(line)
            handled_positions: set[int] = set()

            def include(raw: str, position: int) -> None:
                handled_positions.add(position)
                raw = raw.strip()
                if "\\" in raw or "#" in raw:
                    warnings.append(
                        f"Dynamic include requires manual review: {path}:{line_number}: {raw}"
                    )
                    return
                include_path = Path(raw)
                if include_path.suffix == "":
                    include_path = include_path.with_suffix(".tex")
                if include_path.is_absolute():
                    candidates = (
                        [include_path.resolve()] if include_path.is_file() else []
                    )
                else:
                    search_roots = [path.parent.resolve()]
                    if project_root not in search_roots:
                        search_roots.append(project_root)
                    candidates = []
                    for search_root in search_roots:
                        candidate = (search_root / include_path).resolve()
                        if candidate.is_file() and candidate not in candidates:
                            candidates.append(candidate)
                if len(candidates) > 1:
                    warnings.append(
                        "Ambiguous include resolution requires manual review: "
                        f"{path}:{line_number}: {raw}: "
                        + ", ".join(str(item) for item in candidates)
                    )
                if not candidates:
                    warnings.append(
                        f"Included file not found: {path}:{line_number}: {raw}"
                    )
                for candidate in candidates:
                    visit(candidate)

            for match in INCLUDE_RE.finditer(clean):
                include(match.group(1), match.start())
            for match in UNBRACED_INPUT_RE.finditer(clean):
                include(match.group(1), match.start())
            for match in SUBFILE_RE.finditer(clean):
                include(match.group(1), match.start())
            for match in IMPORT_RE.finditer(clean):
                handled_positions.add(match.start())
                directory, filename = match.group(1).strip(), match.group(2).strip()
                include(str(Path(directory) / filename), match.start())
            for match in CLASS_RE.finditer(clean):
                handled_positions.add(match.start())
                for candidate in local_candidates(
                    match.group(1), ".cls", path, line_number
                ):
                    visit(candidate)
            for match in PACKAGE_RE.finditer(clean):
                handled_positions.add(match.start())
                for package in split_reference_keys(match.group(1)):
                    for candidate in local_candidates(
                        package, ".sty", path, line_number
                    ):
                        visit(candidate)
            for match in INCLUSION_COMMAND_RE.finditer(clean):
                if match.start() not in handled_positions:
                    warnings.append(
                        "Unresolved inclusion command requires manual review: "
                        f"{path}:{line_number}: {truncate(clean)}"
                    )

        active.remove(path)

    visit(root)
    for additional in additional_files or []:
        additional_path = additional.resolve()
        if not additional_path.is_file():
            warnings.append(f"Additional source file not found: {additional_path}")
            continue
        visit(additional_path)

    if fls_file is not None:
        fls_path = fls_file.resolve()
        if not fls_path.is_file():
            warnings.append(f"Recorder file not found: {fls_path}")
        else:
            working_directory = project_root
            fls_input_paths: set[Path] = set()
            try:
                fls_lines = read_lines(fls_path)
            except UnicodeError as exc:
                warnings.append(
                    f"Cannot decode recorder file {fls_path} as UTF-8: {exc}"
                )
                fls_lines = []
            for raw_line in fls_lines:
                if raw_line.startswith("PWD "):
                    candidate = Path(raw_line[4:].strip().strip("'\""))
                    if not candidate.is_absolute():
                        candidate = fls_path.parent / candidate
                    working_directory = candidate.resolve()
                    continue
                if not raw_line.startswith("INPUT "):
                    continue
                raw_input = raw_line[6:].strip().strip("'\"")
                candidate = Path(raw_input)
                if not candidate.is_absolute():
                    candidate = working_directory / candidate
                candidate = candidate.resolve()
                fls_input_paths.add(candidate)
                if candidate.suffix.lower() not in FLS_SOURCE_SUFFIXES:
                    continue
                if not candidate.is_relative_to(project_root):
                    outside_project_inputs.add(str(candidate))
                    warnings.append(
                        "Recorder source input outside project root requires manual "
                        f"review and explicit promotion if load-bearing: {candidate}"
                    )
                    continue
                if candidate.is_file():
                    visit(candidate)
                else:
                    warnings.append(f"Recorder input not found: {candidate}")
            if root not in fls_input_paths:
                warnings.append(
                    f"Recorder trace does not include the main paper: {root}"
                )

    return {
        "files": ordered,
        "warnings": sorted(set(warnings)),
        "outside_project_inputs": sorted(outside_project_inputs),
    }


def collect_tex_files(
    root: Path,
    *,
    additional_files: Iterable[Path] | None = None,
    fls_file: Path | None = None,
    project_root: Path | None = None,
) -> tuple[list[Path], list[str]]:
    closure = discover_source_closure(
        root,
        additional_files=additional_files,
        fls_file=fls_file,
        project_root=project_root,
    )
    return closure["files"], closure["warnings"]


def parse_manifest_source_discovery(
    manifest: dict[str, Any], root: Path, errors: list[str]
) -> tuple[list[Path], Path | None, Path | None, list[str]]:
    discovery = manifest.get("source_discovery")
    if discovery is None:
        discovery = {"additional_files": [], "fls": None}
    if not isinstance(discovery, dict):
        errors.append("manifest.source_discovery must be an object")
        discovery = {"additional_files": [], "fls": None}

    additional_files: list[Path] = []
    additional_records = discovery.get("additional_files", [])
    if not isinstance(additional_records, list):
        errors.append("source_discovery.additional_files must be a list")
        additional_records = []
    seen_additional: set[Path] = set()
    for index, record in enumerate(additional_records, 1):
        prefix = f"source_discovery.additional_files[{index}]"
        if not isinstance(record, dict):
            errors.append(f"{prefix} must be an object")
            continue
        file_value = record.get("file")
        if not is_nonempty_string(file_value):
            errors.append(f"{prefix}.file must be a nonempty string")
            continue
        path = resolve_stored_path(file_value, root)
        if path in seen_additional:
            errors.append(f"Duplicate additional source file: {path}")
        seen_additional.add(path)
        additional_files.append(path)
        if not path.is_file():
            errors.append(f"Additional source file not found: {path}")
        for field in ("reason", "evidence"):
            if not is_nonempty_string(record.get(field)):
                errors.append(f"{prefix}.{field} must be a nonempty string")

    fls_path: Path | None = None
    project_root: Path | None = None
    recorded_outside: list[str] = []
    fls_record = discovery.get("fls")
    if fls_record is not None:
        if not isinstance(fls_record, dict):
            errors.append("source_discovery.fls must be null or an object")
        else:
            fls_value = fls_record.get("file")
            project_value = fls_record.get("project_root")
            digest = fls_record.get("sha256")
            if not is_nonempty_string(fls_value):
                errors.append("source_discovery.fls.file must be a nonempty string")
            else:
                fls_path = resolve_stored_path(fls_value, root)
                if not fls_path.is_file():
                    errors.append(f"Recorder file not found: {fls_path}")
                elif not is_nonempty_string(digest) or sha256_file(fls_path) != digest:
                    errors.append("Recorder file drift: SHA-256 does not match")
            if not is_nonempty_string(project_value):
                errors.append(
                    "source_discovery.fls.project_root must be a nonempty string"
                )
            else:
                project_root = resolve_stored_path(project_value, root)
                if not project_root.is_dir():
                    errors.append(
                        f"Recorder project root is not a directory: {project_root}"
                    )
            outside = fls_record.get("outside_project_inputs")
            if not isinstance(outside, list) or not all(
                is_nonempty_string(item) for item in outside
            ):
                errors.append(
                    "source_discovery.fls.outside_project_inputs must be a string list"
                )
            else:
                recorded_outside = outside
                if len(recorded_outside) != len(set(recorded_outside)):
                    errors.append(
                        "source_discovery.fls.outside_project_inputs contains duplicates"
                    )

    return additional_files, fls_path, project_root, recorded_outside



def location(path: Path, line: int, base: Path) -> dict[str, Any]:
    return {"file": relative_or_absolute(path, base), "line": line}


def truncate(text: str, limit: int = 300) -> str:
    compact = " ".join(text.split())
    return compact if len(compact) <= limit else compact[: limit - 3] + "..."


def readable_source_lines(
    files: Iterable[Path], warnings: list[str]
) -> dict[Path, list[str]]:
    result: dict[Path, list[str]] = {}
    for path in files:
        try:
            result[path] = read_lines(path)
        except UnicodeError as exc:
            warning = f"Cannot decode {path} as UTF-8: {exc}"
            if warning not in warnings:
                warnings.append(warning)
    return result


def scan_formal_units(
    root: Path,
    *,
    source_files: Iterable[Path] | None = None,
    source_warnings: Iterable[str] | None = None,
) -> dict[str, Any]:
    if source_files is None:
        files, warnings = collect_tex_files(root)
    else:
        files, warnings = list(source_files), list(source_warnings or [])
    base = root.resolve().parent
    environments = set(FORMAL_ENVIRONMENTS)
    source_lines = readable_source_lines(files, warnings)
    for path, lines in source_lines.items():
        for line in lines:
            environments.update(NEW_THEOREM_RE.findall(strip_latex_comment(line)))

    units: list[dict[str, Any]] = []
    proofs: list[dict[str, Any]] = []
    label_occurrences: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for path, lines in source_lines.items():
        for row in scan_label_occurrences("\n".join(lines), path, base):
            if is_nonempty_string(row.get("target")):
                label_occurrences[row["target"]].append(row)

    for path, lines in source_lines.items():
        formal_stack: list[dict[str, Any]] = []
        proof_stack: list[int] = []

        for line_number, raw_line in enumerate(lines, 1):
            clean = strip_latex_comment(raw_line)
            for token in TOKEN_RE.finditer(clean):
                action, environment = token.group(1), token.group(2)
                if environment in environments:
                    if action == "begin":
                        formal_stack.append(
                            {"environment": environment, "start": line_number}
                        )
                    else:
                        match_index = next(
                            (
                                index
                                for index in range(len(formal_stack) - 1, -1, -1)
                                if formal_stack[index]["environment"] == environment
                            ),
                            None,
                        )
                        if match_index is None:
                            warnings.append(
                                f"Unmatched \\end{{{environment}}}: {path}:{line_number}"
                            )
                            continue
                        opened = formal_stack.pop(match_index)
                        block = lines[opened["start"] - 1 : line_number]
                        labels = [
                            key
                            for block_line in block
                            for key in LABEL_RE.findall(strip_latex_comment(block_line))
                        ]
                        label = labels[0] if labels else None
                        units.append(
                            {
                                "id": label
                                or f"{environment}:{path.name}:{opened['start']}",
                                "environment": environment,
                                "proof_required": environment
                                not in NON_PROOF_ENVIRONMENTS,
                                "label": label,
                                "statement": {
                                    "file": relative_or_absolute(path, base),
                                    "start_line": opened["start"],
                                    "end_line": line_number,
                                },
                                "statement_excerpt": truncate("\n".join(block)),
                                "proof": None,
                                "proof_redirects": [],
                                "proof_association": {
                                    "status": "unassociated",
                                    "method": "none",
                                    "target": None,
                                    "evidence_occurrence_ids": [],
                                },
                                "reference_occurrences": [],
                                "dependencies": [],
                                "candidate_internal_dependencies": [],
                                "citations": [],
                            }
                        )

                if environment == "proof":
                    if action == "begin":
                        proof_stack.append(line_number)
                    elif proof_stack:
                        proof_start = proof_stack.pop()
                        block = lines[proof_start - 1 : line_number]
                        title_span = proof_optional_title_span(
                            block, proof_start
                        )
                        title = (
                            title_span.get("text")
                            if isinstance(title_span, dict)
                            else None
                        )
                        title_occurrences: list[dict[str, Any]] = []
                        title_warnings: list[str] = []
                        if title is not None:
                            title_occurrences, title_warnings = (
                                scan_reference_occurrences(
                                    title,
                                    path,
                                    base,
                                    start_line=title_span["start_line"],
                                    structural_context="proof_header",
                                )
                            )
                            warnings.extend(title_warnings)
                        evidence = scan_span_evidence(
                            path,
                            proof_start,
                            line_number,
                            base,
                        )
                        warnings.extend(evidence["warnings"])
                        title_targets = sorted(
                            {
                                row["target"]
                                for row in title_occurrences
                                if is_nonempty_string(row.get("target"))
                            }
                        )
                        for occurrence in evidence["reference_occurrences"]:
                            if occurrence_in_title(occurrence, title_span):
                                occurrence["structural_context"] = "proof_header"
                        proofs.append(
                            {
                                "file_path": path,
                                "start_line": proof_start,
                                "end_line": line_number,
                                "title": title,
                                "title_targets": title_targets,
                                "evidence": evidence,
                                "assigned": False,
                            }
                        )
                    else:
                        warnings.append(
                            f"Unmatched \\end{{proof}}: {path}:{line_number}"
                        )

        for opened in formal_stack:
            warnings.append(
                f"Unclosed \\begin{{{opened['environment']}}}: {path}:{opened['start']}"
            )
        for proof_start in proof_stack:
            warnings.append(f"Unclosed \\begin{{proof}}: {path}:{proof_start}")

    units.sort(
        key=lambda item: (
            item["statement"]["file"],
            item["statement"]["start_line"],
        )
    )

    units_by_id = {unit["id"]: unit for unit in units}

    def proof_location(proof: dict[str, Any]) -> dict[str, Any]:
        return {
            "file": relative_or_absolute(proof["file_path"], base),
            "start_line": proof["start_line"],
            "end_line": proof["end_line"],
        }

    def attach_proof(
        unit: dict[str, Any],
        proof: dict[str, Any],
        *,
        method: str,
        status: str = "associated",
        evidence_occurrence_ids: Iterable[str] = (),
    ) -> None:
        evidence = proof["evidence"]
        unit["proof"] = proof_location(proof)
        unit["proof_association"] = {
            "status": status,
            "method": method,
            "target": unit["id"],
            "evidence_occurrence_ids": sorted(set(evidence_occurrence_ids)),
        }
        unit["reference_occurrences"] = [
            dict(row) for row in evidence["reference_occurrences"]
        ]
        unit["dependencies"] = list(evidence["dependencies"])
        unit["citations"] = list(evidence["citations"])
        proof["assigned"] = True

    def adjacent_unit(proof: dict[str, Any]) -> dict[str, Any] | None:
        proof_file = relative_or_absolute(proof["file_path"], base)
        candidates = [
            unit
            for unit in units
            if unit["statement"]["file"] == proof_file
            and unit.get("proof_required") is True
            and unit["statement"]["end_line"] <= proof["start_line"]
        ]
        if not candidates:
            return None
        candidate = max(candidates, key=lambda item: item["statement"]["end_line"])
        intervening = [
            other
            for other in units
            if other["statement"]["file"] == proof_file
            and candidate["statement"]["end_line"]
            < other["statement"]["start_line"]
            < proof["start_line"]
        ]
        if intervening:
            return None
        candidate_path = proof["file_path"]
        separation = source_lines[candidate_path][
            candidate["statement"]["end_line"] : proof["start_line"] - 1
        ]
        if any(strip_latex_comment(line).strip() for line in separation):
            return None
        return candidate

    ordered_proofs = sorted(
        proofs, key=lambda item: (str(item["file_path"]), item["start_line"])
    )

    # Explicit proof titles take precedence over physical adjacency.
    for proof in ordered_proofs:
        if proof.get("title") is None:
            continue
        targets = sorted(
            {
                target
                for target in proof.get("title_targets", [])
                if target in units_by_id
            }
        )
        proof_file = relative_or_absolute(proof["file_path"], base)
        if len(targets) != 1:
            warnings.append(
                "Named proof header does not resolve to exactly one formal result: "
                f"{proof_file}:{proof['start_line']}"
            )
            continue
        unit = units_by_id[targets[0]]
        if unit.get("proof") is not None:
            warnings.append(
                f"Multiple named proofs target {unit['id']}: "
                f"{proof_file}:{proof['start_line']}"
            )
            continue
        evidence_ids = [
            row["occurrence_id"]
            for row in proof["evidence"]["reference_occurrences"]
            if row.get("target") == unit["id"]
            and row.get("structural_context") == "proof_header"
        ]
        attach_proof(
            unit,
            proof,
            method="named_environment",
            evidence_occurrence_ids=evidence_ids,
        )

    # Recognize only strict navigation-only forwarding proofs.
    for proof in ordered_proofs:
        if proof.get("assigned") or proof.get("title") is not None:
            continue
        unit = adjacent_unit(proof)
        if unit is None:
            continue
        evidence = proof["evidence"]
        occurrences = evidence["reference_occurrences"]
        hyper_occurrences = [
            row for row in occurrences if row.get("command") == "hyperref"
        ]
        result_targets = {
            row["target"]
            for row in occurrences
            if row.get("target") in units_by_id
        }
        block = source_lines[proof["file_path"]][
            proof["start_line"] - 1 : proof["end_line"]
        ]
        compact = " ".join(
            line.strip()
            for line in block[1:-1]
            if strip_latex_comment(line).strip()
        )
        has_math_signal = bool(
            re.search(
                r"\$|\\\(|\\\[|\\begin\s*\{(?:align|equation|gather|multline)",
                compact,
            )
            or "=" in compact
        )
        strict_redirect = (
            len({row["target"] for row in hyper_occurrences}) == 1
            and result_targets == {unit["id"]}
            and not evidence["citations"]
            and bool(re.match(r"^\s*See\b", compact, re.IGNORECASE))
            and not has_math_signal
        )
        if not strict_redirect:
            continue
        anchor = hyper_occurrences[0]["target"]
        anchors = label_occurrences.get(anchor, [])
        if len(anchors) != 1:
            warnings.append(
                f"Forwarding proof target {anchor} is missing or nonunique for "
                f"{unit['id']}"
            )
            continue
        anchor_path = resolve_stored_path(anchors[0]["file"], base)
        region = bounded_proof_region(anchor_path, anchors[0]["line"])
        if region is None:
            warnings.append(
                f"Forwarding proof target {anchor} has no uniquely bounded proof "
                f"region for {unit['id']}"
            )
            continue
        conflicting_named = [
            other
            for other in ordered_proofs
            if other["file_path"].resolve() == anchor_path.resolve()
            and region["start_line"] <= other["start_line"] <= region["end_line"]
            and any(
                target != unit["id"] and target in units_by_id
                for target in other.get("title_targets", [])
            )
        ]
        if conflicting_named:
            warnings.append(
                f"Forwarding proof target {anchor} encloses a named proof for "
                f"another result"
            )
            continue
        redirect = {
            **proof_location(proof),
            "target_anchor": anchor,
            "occurrence_id": hyper_occurrences[0]["occurrence_id"],
        }
        unit["proof_redirects"].append(redirect)
        proof["assigned"] = True
        if unit.get("proof") is None:
            redirected_proof = {
                "file_path": anchor_path,
                "start_line": region["start_line"],
                "end_line": region["end_line"],
                "evidence": scan_span_evidence(
                    anchor_path,
                    region["start_line"],
                    region["end_line"],
                    base,
                ),
                "assigned": False,
            }
            warnings.extend(redirected_proof["evidence"]["warnings"])
            attach_proof(
                unit,
                redirected_proof,
                method="redirect_anchor",
                status="review_required",
                evidence_occurrence_ids=[
                    hyper_occurrences[0]["occurrence_id"]
                ],
            )
            warnings.append(
                f"Redirected proof association requires rendered-source review: "
                f"{unit['id']} -> {anchor}"
            )

    # Remaining proof environments use conservative physical adjacency.
    for proof in ordered_proofs:
        if proof.get("assigned") or proof.get("title") is not None:
            continue
        proof_file = relative_or_absolute(proof["file_path"], base)
        unit = adjacent_unit(proof)
        if unit is None:
            warnings.append(
                f"Proof could not be associated with a formal statement: "
                f"{proof_file}:{proof['start_line']}"
            )
            continue
        if unit.get("proof") is not None:
            warnings.append(
                f"Additional proof could not be associated uniquely with {unit['id']}: "
                f"{proof_file}:{proof['start_line']}"
            )
            continue
        attach_proof(unit, proof, method="adjacent_environment")

    label_owners: dict[str, dict[str, Any]] = {}
    for target, locations in sorted(label_occurrences.items()):
        if len(locations) != 1:
            label_owners[target] = {
                "status": "duplicate",
                "owner_unit_id": None,
                "owner_region": None,
                "locations": locations,
            }
            continue
        row = locations[0]
        owners: list[tuple[str, str]] = []
        for unit in units:
            for region_name in ("statement", "proof"):
                span = unit.get(region_name)
                if (
                    isinstance(span, dict)
                    and span.get("file") == row["file"]
                    and is_int(span.get("start_line"))
                    and is_int(span.get("end_line"))
                    and span["start_line"] <= row["line"] <= span["end_line"]
                ):
                    owners.append((unit["id"], region_name))
        unique_owners = sorted(set(owners))
        if len(unique_owners) == 1:
            owner_unit_id, owner_region = unique_owners[0]
            status = "unique"
        elif unique_owners:
            owner_unit_id, owner_region, status = None, None, "ambiguous"
        else:
            owner_unit_id, owner_region, status = None, None, "unowned"
        label_owners[target] = {
            "status": status,
            "owner_unit_id": owner_unit_id,
            "owner_region": owner_region,
            "locations": locations,
        }

    support_index = build_unowned_label_support_index(
        source_lines, units, label_owners, base
    )
    for unit in units:
        statement_evidence = scan_unit_statement_evidence(unit, base)
        warnings.extend(statement_evidence["warnings"])
        for occurrence in unit["reference_occurrences"]:
            owner = label_owners.get(occurrence["target"])
            if owner is None:
                occurrence["resolution_status"] = "missing"
            else:
                occurrence["resolution_status"] = owner["status"]
                occurrence["owner_unit_id"] = owner["owner_unit_id"]
                occurrence["owner_region"] = owner["owner_region"]
        unit["candidate_internal_dependencies"] = (
            resolve_candidate_internal_dependencies(
                unit["id"],
                [
                    *statement_evidence["reference_occurrences"],
                    *unit["reference_occurrences"],
                ],
                label_owners,
                support_index,
            )
        )

    for unit in units:
        if (
            unit.get("proof_required") is True
            and unit.get("proof") is None
        ):
            statement = unit["statement"]
            warnings.append(
                f"Proof-required result has no associated proof: {unit['id']} at "
                f"{statement['file']}:{statement['start_line']}"
            )

    return {
        "schema_version": SCHEMA_VERSION,
        "root_file": str(root.resolve()),
        "files": [relative_or_absolute(path, base) for path in files],
        "formal_environments": sorted(environments),
        "units": units,
        "label_owners": label_owners,
        "warnings": warnings,
    }


def scan_cross_references(
    root: Path,
    *,
    source_files: Iterable[Path] | None = None,
    source_warnings: Iterable[str] | None = None,
) -> dict[str, Any]:
    if source_files is None:
        files, warnings = collect_tex_files(root)
    else:
        files, warnings = list(source_files), list(source_warnings or [])
    base = root.resolve().parent
    labels: dict[str, list[dict[str, Any]]] = defaultdict(list)
    references: dict[str, list[dict[str, Any]]] = defaultdict(list)
    occurrences: list[dict[str, Any]] = []

    source_lines = readable_source_lines(files, warnings)
    for path, lines in source_lines.items():
        text = "\n".join(lines)
        for row in scan_label_occurrences(text, path, base):
            labels[row["target"]].append(
                {
                    "file": row["file"],
                    "line": row["line"],
                    "column": row["column"],
                }
            )
        file_occurrences, file_warnings = scan_reference_occurrences(
            text, path, base
        )
        warnings.extend(file_warnings)
        for row in file_occurrences:
            occurrences.append(row)
            references[row["target"]].append(
                {
                    "file": row["file"],
                    "line": row["line"],
                    "column": row["column"],
                    "command": row["command"],
                    "occurrence_id": row["occurrence_id"],
                }
            )

    label_keys = set(labels)
    reference_keys = set(references)
    return {
        "schema_version": SCHEMA_VERSION,
        "root_file": str(root.resolve()),
        "files": [relative_or_absolute(path, base) for path in files],
        "counts": {
            "unique_labels": len(label_keys),
            "unique_references": len(reference_keys),
            "broken_references": len(reference_keys - label_keys),
            "orphan_labels": len(label_keys - reference_keys),
            "duplicate_labels": sum(1 for value in labels.values() if len(value) > 1),
        },
        "broken_references": {
            key: references[key] for key in sorted(reference_keys - label_keys)
        },
        "orphan_labels": {
            key: labels[key] for key in sorted(label_keys - reference_keys)
        },
        "duplicate_labels": {
            key: value for key, value in sorted(labels.items()) if len(value) > 1
        },
        "labels": dict(sorted(labels.items())),
        "references": dict(sorted(references.items())),
        "occurrences": occurrences,
        "warnings": warnings,
    }


def cross_reference_anomalies(data: dict[str, Any]) -> list[dict[str, Any]]:
    """Return the exact parser-detected anomalies that require human review."""
    anomalies: list[dict[str, Any]] = []
    for kind, field in (
        ("broken_reference", "broken_references"),
        ("duplicate_label", "duplicate_labels"),
    ):
        records = data.get(field)
        if not isinstance(records, dict):
            continue
        for key, locations in sorted(records.items()):
            anomalies.append(
                {
                    "kind": kind,
                    "key": key,
                    "locations": locations if isinstance(locations, list) else [],
                }
            )
    return anomalies


def validate_cross_reference_reviews(
    value: Any,
    cross_references: dict[str, Any],
    in_scope: list[str],
    errors: list[str],
) -> dict[str, Any]:
    expected = {
        (row["kind"], row["key"]): row
        for row in cross_reference_anomalies(cross_references)
    }
    if not isinstance(value, list):
        errors.append("manifest.cross_reference_reviews must be a list")
        value = []
    seen: set[tuple[str, str]] = set()
    issue_ids: set[str] = set()
    affected_units: set[str] = set()
    statuses: list[str] = []
    for index, review in enumerate(value, 1):
        prefix = f"cross_reference_reviews[{index}]"
        if not isinstance(review, dict):
            errors.append(f"{prefix} must be an object")
            continue
        kind = review.get("kind")
        key = review.get("key")
        identity = (kind, key)
        if not is_nonempty_string(kind) or not is_nonempty_string(key):
            errors.append(f"{prefix}.kind and .key must be nonempty strings")
            continue
        if identity in seen:
            errors.append(f"Duplicate cross-reference review: {kind}/{key}")
        seen.add(identity)
        expected_row = expected.get(identity)
        if expected_row is None:
            errors.append(f"{prefix}: stale cross-reference anomaly review")
        elif review.get("locations") != expected_row.get("locations"):
            errors.append(f"{prefix}.locations do not match the current anomaly")
        status = review.get("status")
        if not is_enum_value(status, CROSS_REFERENCE_REVIEW_STATUSES):
            errors.append(f"{prefix}.status is invalid")
        else:
            statuses.append(status)
        if not is_substantive_string(review.get("evidence")):
            errors.append(f"{prefix}.evidence must be nonempty and substantive")
        affected = review.get("affected_units")
        if not isinstance(affected, list) or not all(
            is_nonempty_string(item) for item in affected
        ):
            errors.append(f"{prefix}.affected_units must be a string list")
            affected = []
        elif len(affected) != len(set(affected)):
            errors.append(f"{prefix}.affected_units contains duplicates")
        unknown = set(affected) - set(in_scope)
        if unknown:
            errors.append(
                f"{prefix}.affected_units names results outside scope: "
                + ", ".join(sorted(unknown))
            )
        row_issues = validate_issue_id_list(
            review.get("issue_ids"), f"{prefix}.issue_ids", errors
        )
        issue_ids.update(row_issues)
        if is_enum_value(status, {"defect", "inconclusive"}):
            affected_units.update(affected)
        if status == "passed" and (affected or row_issues):
            errors.append(f"{prefix}: a passed anomaly review must be clean")
        if is_enum_value(status, {"defect", "inconclusive"}) and not row_issues:
            errors.append(f"{prefix}: {status} requires canonical issue_ids")
    missing = set(expected) - seen
    if missing:
        errors.append(
            "manifest.cross_reference_reviews is missing current anomalies: "
            + ", ".join(f"{kind}/{key}" for kind, key in sorted(missing))
        )
    return {
        "defect": "defect" in statuses,
        "inconclusive": "inconclusive" in statuses,
        "issue_ids": issue_ids,
        "affected_units": affected_units,
    }


def escape_markdown(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def index_markdown(data: dict[str, Any]) -> str:
    rows = [
        "# Formal Proof-Unit Inventory",
        "",
        "| ID | Type | Proof required | Statement | Proof | Direct references | Citations |",
        "|---|---|---|---|---|---|---|",
    ]
    for unit in data["units"]:
        statement = unit["statement"]
        statement_location = (
            f"{statement['file']}:{statement['start_line']}-{statement['end_line']}"
        )
        if unit["proof"]:
            proof = unit["proof"]
            proof_location = f"{proof['file']}:{proof['start_line']}-{proof['end_line']}"
        else:
            proof_location = "not associated"
        rows.append(
            "| "
            + " | ".join(
                escape_markdown(value)
                for value in (
                    unit["id"],
                    unit["environment"],
                    unit.get("proof_required"),
                    statement_location,
                    proof_location,
                    ", ".join(unit["dependencies"]) or "none found",
                    ", ".join(unit.get("citations", [])) or "none found",
                )
            )
            + " |"
        )
    rows.extend(["", f"**Units found:** {len(data['units'])}", ""])
    if data["warnings"]:
        rows.extend(["## Parser warnings", ""])
        rows.extend(f"- {warning}" for warning in data["warnings"])
        rows.append("")
    return "\n".join(rows)


def locations_text(values: Iterable[dict[str, Any]]) -> str:
    return ", ".join(f"{item['file']}:{item['line']}" for item in values)


def crossref_markdown(data: dict[str, Any]) -> str:
    rows = ["# Cross-Reference Audit", ""]
    sections = (
        ("Broken references", "broken_references"),
        ("Duplicate labels", "duplicate_labels"),
        ("Orphan labels", "orphan_labels"),
    )
    for title, key in sections:
        rows.extend([f"## {title}", "", "| Key | Locations |", "|---|---|"])
        values = data[key]
        if values:
            rows.extend(
                f"| {escape_markdown(name)} | {escape_markdown(locations_text(items))} |"
                for name, items in values.items()
            )
        else:
            rows.append("| None | None found |")
        rows.append("")
    rows.extend(["## Counts", "", "| Metric | Count |", "|---|---|"])
    rows.extend(
        f"| {escape_markdown(name)} | {value} |"
        for name, value in data["counts"].items()
    )
    rows.append("")
    if data["warnings"]:
        rows.extend(["## Parser warnings", ""])
        rows.extend(f"- {warning}" for warning in data["warnings"])
        rows.append("")
    return "\n".join(rows)


def serialize(data: dict[str, Any], output_format: str) -> str:
    if output_format == "json":
        return json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    raise ValueError(f"Unsupported format: {output_format}")


def write_or_print(text: str, output: Path | None, force: bool = False) -> None:
    if output is None:
        print(text, end="")
        return
    output = output.resolve()
    if output.exists() and not force:
        raise FileExistsError(f"Output exists; use --force to replace it: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text, encoding="utf-8", newline="\n")


def copy_template(skill_root: Path, name: str, destination: Path) -> None:
    source = skill_root / "assets" / "templates" / name
    if not source.is_file():
        raise FileNotFoundError(f"Bundled template not found: {source}")
    shutil.copy2(source, destination)


def cmd_scaffold(args: argparse.Namespace) -> int:
    paper = args.paper.resolve()
    output = args.output.resolve()
    if not paper.is_file():
        raise FileNotFoundError(f"Paper source not found: {paper}")
    if output.exists():
        raise FileExistsError(f"Refusing to overwrite existing audit root: {output}")

    project_root_arg = getattr(args, "project_root", None)
    project_root = (
        project_root_arg.resolve() if isinstance(project_root_arg, Path) else paper.parent
    )
    if not project_root.is_dir():
        raise FileNotFoundError(f"Project root not found: {project_root}")
    if not paper.is_relative_to(project_root):
        raise ValueError("Project root must contain the main paper")

    additional_records: list[dict[str, str]] = []
    additional_paths: list[Path] = []
    seen_additional: set[Path] = set()
    for index, (raw_path, reason, evidence) in enumerate(
        getattr(args, "additional_source", None) or [], 1
    ):
        reason = reason.strip()
        evidence = evidence.strip()
        if not reason or not evidence:
            raise ValueError(
                f"Additional source {index} requires nonempty reason and evidence"
            )
        candidate = Path(raw_path)
        if not candidate.is_absolute():
            candidate = paper.parent / candidate
        candidate = candidate.resolve()
        if not candidate.is_file():
            raise FileNotFoundError(f"Additional source file not found: {candidate}")
        if candidate in seen_additional:
            raise ValueError(f"Duplicate additional source file: {candidate}")
        seen_additional.add(candidate)
        additional_paths.append(candidate)
        additional_records.append(
            {
                "file": relative_or_absolute(candidate, output),
                "reason": reason,
                "evidence": evidence,
            }
        )
    fls_arg = getattr(args, "fls", None)
    fls_path = fls_arg.resolve() if isinstance(fls_arg, Path) else None
    if fls_path is not None and not fls_path.is_file():
        raise FileNotFoundError(f"Recorder file not found: {fls_path}")

    directories = [
        output / "audit" / "01_index",
        output / "audit" / "02_ledgers",
        output / "audit" / "03_dependencies",
        output / "audit" / "04_local_checks",
        output / "audit" / "05_adversarial",
        output / "audit" / "06_reports",
    ]
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=False)

    skill_root = Path(__file__).resolve().parent.parent
    copy_template(skill_root, "CHECK_PLAN.md", output / "CHECK_PLAN.md")
    copy_template(skill_root, "EXECUTION_ORDER.md", output / "EXECUTION_ORDER.md")
    copy_template(
        skill_root,
        "DEPENDENCY_GRAPH.md",
        output / "audit" / "03_dependencies" / "dependency_graph.md",
    )
    copy_template(
        skill_root,
        "FINAL_REPORT.md",
        output / "audit" / "06_reports" / "FINAL_REPORT.md",
    )
    closure = discover_source_closure(
        paper,
        additional_files=additional_paths,
        fls_file=fls_path,
        project_root=project_root,
    )
    source_files = closure["files"]
    source_warnings = closure["warnings"]
    inventory = scan_formal_units(
        paper,
        source_files=source_files,
        source_warnings=source_warnings,
    )
    cross_references = scan_cross_references(
        paper,
        source_files=source_files,
        source_warnings=source_warnings,
    )
    paper_value = relative_or_absolute(paper, output)
    parser_warnings = sorted(
        set(inventory.get("warnings", []))
        | set(cross_references.get("warnings", []))
        | set(source_warnings)
    )
    source_snapshot_files = [
        {
            "file": relative_or_absolute(path, output),
            "sha256": sha256_file(path),
        }
        for path in source_files
    ]
    fls_record = None
    if fls_path is not None:
        fls_record = {
            "file": relative_or_absolute(fls_path, output),
            "sha256": sha256_file(fls_path) if fls_path.is_file() else None,
            "project_root": relative_or_absolute(project_root, output),
            "outside_project_inputs": closure["outside_project_inputs"],
        }
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "protocol": protocol_identity(),
        "paper_file": paper_value,
        "created_utc": utc_now(),
        "inventory_file": "audit/01_index/theorem_inventory.json",
        "dependency_registry": "audit/03_dependencies/DEPENDENCY_REGISTRY.json",
        "method_interface_registry": (
            "audit/03_dependencies/METHOD_INTERFACE_REGISTRY.json"
        ),
        "finalization_record": "audit/06_reports/FINALIZATION.json",
        "source_snapshot": {
            "files": source_snapshot_files,
            "sha256": canonical_sha256(source_snapshot_files),
        },
        "source_discovery": {
            "additional_files": additional_records,
            "fls": fls_record,
        },
        "parser_warnings": parser_warnings,
        "parser_warning_reviews": [
            {
                "warning": warning,
                "disposition": "unreviewed",
                "affected_units": [],
                "evidence": "",
            }
            for warning in parser_warnings
        ],
        "cross_reference_reviews": [
            {
                **anomaly,
                "status": "not_reviewed",
                "evidence": "",
                "affected_units": [],
                "issue_ids": [],
            }
            for anomaly in cross_reference_anomalies(cross_references)
        ],
        "audit_scope": {
            "status": "not_set",
            "depth": "not_set",
            "overall_assessment": "not_set",
            "target_units": [],
            "in_scope_units": [],
            "critical_units": [],
            "in_scope_interfaces": [],
            "excluded_units": [],
            "inventory_overrides": [],
            "source_or_parser_limits": [],
        },
        "completion": {
            "inventory_reviewed": False,
            "parser_warnings_reviewed": False,
            "dependency_registry_reviewed": False,
            "method_interface_registry_reviewed": False,
            "global_consistency_pass": {
                "status": "not_checked",
                "checks": [
                    {
                        "aspect": aspect,
                        "status": "not_checked",
                        "evidence": "",
                        "affected_units": [],
                        "issue_ids": [],
                    }
                    for aspect in GLOBAL_CONSISTENCY_ASPECTS
                ],
            },
            "adversarial_pass": {
                "status": "not_checked",
                "evidence": [],
            },
            "final_report_ready": False,
        },
        "notes": [],
    }
    progress = {
        "schema_version": SCHEMA_VERSION,
        "paper_file": paper_value,
        "source_snapshot_sha256": manifest["source_snapshot"]["sha256"],
        "status": "bootstrap",
        "current_pass": 0,
        "active_unit": None,
        "completed_units": [],
        "conditional_units": [],
        "blocked_units": {},
        "not_started_units": [unit["id"] for unit in inventory["units"]],
        "open_high_priority_issues": [],
        "source_or_parser_limits": [],
        "next_action": "Review CHECK_PLAN.md and build the proof-unit inventory.",
        "updated_utc": utc_now(),
    }
    issue_log = {"schema_version": SCHEMA_VERSION, "issues": []}
    dependency_registry = {
        "schema_version": SCHEMA_VERSION,
        "closure_contract_version": CLOSURE_CONTRACT_VERSION,
        "review": {
            "status": "not_reviewed",
            "source_snapshot_sha256": "",
            "inventory_sha256": "",
            "in_scope_units": [],
            "evidence": [],
        },
        "internal_uses": [],
        "external_results": [],
    }
    method_interface_registry = {
        "schema_version": METHOD_INTERFACE_SCHEMA_VERSION,
        "scope": {
            "status": "not_set",
            "trigger": "not_set",
            "reason": "",
        },
        "interfaces": [],
    }
    (output / "AUDIT_MANIFEST.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    (output / "PROGRESS.json").write_text(
        json.dumps(progress, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    (output / "audit" / "06_reports" / "ISSUE_LOG.json").write_text(
        json.dumps(issue_log, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    (output / "audit" / "06_reports" / "ISSUE_SUMMARY.md").write_text(
        render_issue_summary([]), encoding="utf-8", newline="\n"
    )
    (output / "audit" / "01_index" / "theorem_inventory.json").write_text(
        serialize(inventory, "json"), encoding="utf-8", newline="\n"
    )
    (output / "audit" / "01_index" / "theorem_inventory.md").write_text(
        index_markdown(inventory), encoding="utf-8", newline="\n"
    )
    (output / "audit" / "01_index" / "cross_reference_audit.json").write_text(
        serialize(cross_references, "json"), encoding="utf-8", newline="\n"
    )
    (output / "audit" / "01_index" / "cross_reference_audit.md").write_text(
        crossref_markdown(cross_references), encoding="utf-8", newline="\n"
    )
    (output / "audit" / "03_dependencies" / "DEPENDENCY_REGISTRY.json").write_text(
        json.dumps(dependency_registry, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    (
        output / "audit" / "03_dependencies" / "METHOD_INTERFACE_REGISTRY.json"
    ).write_text(
        json.dumps(method_interface_registry, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    print(
        json.dumps(
            {
                "audit_root": str(output),
                "paper_file": paper_value,
                "source_files": len(source_files),
                "proof_units": len(inventory["units"]),
                "parser_warnings": len(parser_warnings),
            },
            indent=2,
        )
    )
    return 0


def cmd_index(args: argparse.Namespace) -> int:
    if not args.file.is_file():
        raise FileNotFoundError(f"LaTeX source not found: {args.file}")
    data = scan_formal_units(args.file)
    text = index_markdown(data) if args.format == "markdown" else serialize(data, "json")
    write_or_print(text, args.output, args.force)
    return 0


def cmd_crossref(args: argparse.Namespace) -> int:
    if not args.file.is_file():
        raise FileNotFoundError(f"LaTeX source not found: {args.file}")
    data = scan_cross_references(args.file)
    text = (
        crossref_markdown(data)
        if args.format == "markdown"
        else serialize(data, "json")
    )
    write_or_print(text, args.output, args.force)
    return 0


def cmd_extract(args: argparse.Namespace) -> int:
    source = args.file.resolve()
    output = args.output.resolve()
    if not source.is_file():
        raise FileNotFoundError(f"Source file not found: {source}")
    if output == source:
        raise ValueError("Ledger output must not overwrite the source file")
    if output.exists() and not args.force:
        raise FileExistsError(f"Ledger exists; use --force to replace it: {output}")
    lines = read_lines(source)
    if args.start < 1 or args.end < args.start or args.end > len(lines):
        raise ValueError(
            f"Invalid inclusive range {args.start}-{args.end}; source has {len(lines)} lines"
        )
    statement_start = getattr(args, "statement_start", None)
    statement_end = getattr(args, "statement_end", None)
    statement_file_value = getattr(args, "statement_file", None)
    if (statement_start is None) != (statement_end is None):
        raise ValueError("Provide both --statement-start and --statement-end")
    statement_source = (
        statement_file_value.resolve() if statement_file_value is not None else source
    )
    if statement_start is not None:
        if not statement_source.is_file():
            raise FileNotFoundError(f"Statement source not found: {statement_source}")
        statement_lines = read_lines(statement_source)
        if not (
            1 <= statement_start <= statement_end <= len(statement_lines)
        ):
            raise ValueError(
                "The statement range must be valid in its declared source file"
            )
    statement_is_covered = (
        statement_start is not None
        and statement_source == source
        and args.start <= statement_start <= statement_end <= args.end
    )
    coverage_mode = (
        "statement_and_proof"
        if statement_is_covered
        else "proof_with_separate_statement"
    )
    separate_statement_reason = getattr(args, "separate_statement_reason", None) or ""
    selected = lines[args.start - 1 : args.end]
    output.parent.mkdir(parents=True, exist_ok=True)
    ledger = {
        "schema_version": SCHEMA_VERSION,
        "evidence_contract_version": EVIDENCE_CONTRACT_VERSION,
        "unit_id": args.unit_id,
        "source": {
            "file": relative_or_absolute(source, output.parent),
            "start_line": args.start,
            "end_line": args.end,
            "unit_sha256": sha256_text("\n".join(selected)),
            "coverage_mode": coverage_mode,
            "separate_statement_reason": separate_statement_reason,
        },
        "source_lines": [
            {
                "line": line_number,
                "sha256": sha256_text(text),
                "text": text,
            }
            for line_number, text in enumerate(selected, args.start)
        ],
        "obligation": {
            "statement_spans": (
                [
                    locked_span(
                        statement_source,
                        statement_start,
                        statement_end,
                        output.parent,
                    )
                ]
                if statement_start is not None
                else []
            ),
            "quantified_variables": [],
            "quantifier_scope": "",
            "probability_model": "",
            "hypotheses": [],
            "definitions": [],
            "conclusion": "",
            "conclusions": [],
            "uniformity": "",
            "regime": "",
            "constant_dependencies": [],
            "context_spans": [],
            "normalization_checks": [],
        },
        "review": {
            "unit_status": "not_checked",
            "conclusion_step_id": "",
            "conclusion_results": [],
            "contract_fidelity": "not_checked",
            "argument_status": "not_checked",
            "statement_status": "not_assessed",
            "dependency_closure": "not_checked",
            "use_site_sufficiency": "not_checked",
            "explicit_assumptions": [],
            "inherited_assumptions": [],
            "direct_dependencies": [],
            "source_reference_dispositions": [],
            "citation_dispositions": [],
            "use_sites": [],
            "verification_basis": [],
            "reviewer_notes": [],
        },
        "independent_check": {
            "required": False,
            "status": "not_required",
            "independence_level": "none",
            "challenger_verdict": "not_checked",
            "reconciled_verdict": "not_checked",
            "artifact": "",
            "disagreements": [],
            "resolution": "",
        },
        "steps": [],
    }
    output.write_text(
        json.dumps(ledger, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {
                "ledger": str(output),
                "unit_id": args.unit_id,
                "source_range": f"{args.start}-{args.end}",
                "physical_lines": len(selected),
            },
            indent=2,
        )
    )
    return 0


def is_non_substantive(text: str) -> bool:
    stripped = text.strip()
    if not stripped or stripped.startswith("%"):
        return True
    return bool(
        re.fullmatch(
            r"\\(?:begin|end)\{proof\}(?:\[[^]]*\])?|\\qed(?:here)?",
            stripped,
        )
    )


def expected_unit_status(statuses: list[str]) -> str:
    substantive = [status for status in statuses if status != "non_substantive"]
    if not substantive or "not_checked" in substantive:
        return "not_checked"
    if "incorrect" in substantive:
        return "incorrect"
    if "gap" in substantive:
        return "gap"
    if "unclear" in substantive:
        return "unclear"
    if "conditionally_verified" in substantive:
        return "conditionally_verified"
    if all(status == "verified" for status in substantive):
        return "verified"
    return "not_checked"


def conclusion_contract_payload(
    obligation: dict[str, Any], conclusion_id: str
) -> dict[str, Any] | None:
    conclusions = obligation.get("conclusions")
    if not isinstance(conclusions, list):
        return None
    record = next(
        (
            item
            for item in conclusions
            if isinstance(item, dict) and item.get("id") == conclusion_id
        ),
        None,
    )
    if record is None:
        return None
    applicability: list[dict[str, Any]] = []
    pointers = record.get("applies_under")
    if isinstance(pointers, list):
        for pointer in pointers:
            found, value = resolve_json_pointer(obligation, pointer)
            applicability.append(
                {
                    "pointer": pointer,
                    "resolved": value if found else None,
                }
            )
    return {
        "id": record.get("id"),
        "claim": record.get("claim"),
        "source_spans": record.get("source_spans"),
        "applicability": applicability,
    }


def validate_conclusion_records(
    obligation: dict[str, Any],
    ledger_path: Path,
    final: bool,
    errors: list[str],
) -> list[dict[str, Any]]:
    value = obligation.get("conclusions")
    if value is None and not final:
        return []
    if not isinstance(value, list):
        errors.append("obligation.conclusions must be an ordered list")
        return []
    if final and not value:
        errors.append("obligation.conclusions must contain at least one conclusion")
    statement_metadata = [
        metadata
        for span in obligation.get("statement_spans", [])
        if (metadata := resolved_span_metadata(span, ledger_path.parent)) is not None
    ] if isinstance(obligation.get("statement_spans"), list) else []
    seen: set[str] = set()
    records: list[dict[str, Any]] = []
    for index, record in enumerate(value, 1):
        prefix = f"obligation.conclusions[{index}]"
        if not isinstance(record, dict):
            errors.append(f"{prefix} must be an object")
            continue
        conclusion_id = record.get("id")
        if (
            not isinstance(conclusion_id, str)
            or not CONCLUSION_ID_RE.fullmatch(conclusion_id)
        ):
            errors.append(f"{prefix}.id must match C001")
        elif conclusion_id in seen:
            errors.append(f"duplicate conclusion id {conclusion_id}")
        else:
            seen.add(conclusion_id)
        claim = record.get("claim")
        if not is_substantive_string(claim):
            errors.append(f"{prefix}.claim must be substantive")
        spans = record.get("source_spans")
        if not isinstance(spans, list) or (final and not spans):
            errors.append(f"{prefix}.source_spans must be a nonempty list")
            spans = []
        for span_index, span in enumerate(spans, 1):
            validate_locked_span(
                span,
                ledger_path.parent,
                f"{prefix}.source_spans[{span_index}]",
                errors,
            )
            metadata = resolved_span_metadata(span, ledger_path.parent)
            if metadata is not None and statement_metadata and not any(
                Path(parent["file"]).resolve() == Path(metadata["file"]).resolve()
                and parent["start_line"] <= metadata["start_line"]
                and metadata["end_line"] <= parent["end_line"]
                for parent in statement_metadata
            ):
                errors.append(
                    f"{prefix}.source_spans[{span_index}] is outside the locked "
                    "statement spans"
                )
        pointers = record.get("applies_under")
        if not isinstance(pointers, list) or not all(
            is_nonempty_string(pointer) for pointer in pointers
        ):
            errors.append(f"{prefix}.applies_under must be a JSON Pointer list")
            pointers = []
        if len(pointers) != len(set(pointers)):
            errors.append(f"{prefix}.applies_under contains duplicates")
        for pointer in pointers:
            root_name = (
                pointer[1:].split("/", 1)[0]
                if isinstance(pointer, str) and pointer.startswith("/")
                else ""
            )
            found, resolved = resolve_json_pointer(obligation, pointer)
            if (
                root_name not in OBLIGATION_PREMISE_ROOTS
                or not found
                or isinstance(resolved, (list, dict))
                or resolved in (None, "")
            ):
                errors.append(
                    f"{prefix}.applies_under has unresolved scalar pointer {pointer}"
                )
        normalization = record.get("normalization")
        if not isinstance(normalization, dict):
            errors.append(f"{prefix}.normalization must be an object")
        else:
            if not is_enum_value(
                normalization.get("status"), {"checked", "unclear"}
            ):
                errors.append(f"{prefix}.normalization.status is invalid")
            if not is_substantive_string(normalization.get("evidence")):
                errors.append(
                    f"{prefix}.normalization.evidence must be substantive"
                )
        records.append(record)
    if (
        final
        and len(records) == 1
        and is_substantive_string(records[0].get("claim"))
        and obligation.get("conclusion") != records[0].get("claim")
    ):
        errors.append(
            "For one conclusion, obligation.conclusion must exactly match "
            "obligation.conclusions[1].claim"
        )
    return records


def validate_obligation(
    obligation: Any, ledger_path: Path, final: bool, errors: list[str]
) -> dict[str, str]:
    if not isinstance(obligation, dict):
        errors.append("obligation must be an object")
        return {}

    spans = obligation.get("statement_spans")
    if not isinstance(spans, list):
        errors.append("obligation.statement_spans must be a list")
        spans = []
    if final and not spans:
        errors.append("obligation.statement_spans must identify the exact theorem statement")
    for index, span in enumerate(spans, 1):
        validate_locked_span(
            span,
            ledger_path.parent,
            f"obligation.statement_spans[{index}]",
            errors,
        )

    variables = obligation.get("quantified_variables")
    if not isinstance(variables, list):
        errors.append("obligation.quantified_variables must be an ordered list")
    else:
        seen_symbols: set[str] = set()
        for index, variable in enumerate(variables, 1):
            prefix = f"obligation.quantified_variables[{index}]"
            if not isinstance(variable, dict):
                errors.append(f"{prefix} must be an object")
                continue
            for field in ("symbol", "type", "domain"):
                field_value = variable.get(field)
                if not is_nonempty_string(field_value):
                    errors.append(f"{prefix}.{field} must be a nonempty string")
                elif final and is_explicit_absence(field_value):
                    errors.append(
                        f"{prefix}.{field} cannot use an absence marker"
                    )
                elif final and is_forbidden_contract_placeholder(field_value):
                    errors.append(
                        f"{prefix}.{field} cannot use an unresolved placeholder"
                    )
            symbol = variable.get("symbol")
            if is_nonempty_string(symbol):
                if symbol in seen_symbols:
                    errors.append(f"duplicate quantified variable symbol {symbol}")
                seen_symbols.add(symbol)
            if (
                final or "quantifier" in variable
            ) and not is_enum_value(variable.get("quantifier"), QUANTIFIER_KINDS):
                errors.append(
                    f"{prefix}.quantifier must be one of {sorted(QUANTIFIER_KINDS)}"
                )

    contexts = obligation.get("context_spans")
    if not isinstance(contexts, list):
        errors.append("obligation.context_spans must be a list")
        contexts = []
    for index, span in enumerate(contexts, 1):
        validate_locked_span(
            span,
            ledger_path.parent,
            f"obligation.context_spans[{index}]",
            errors,
            require_role=True,
        )

    validate_conclusion_records(obligation, ledger_path, final, errors)

    if not final and "normalization_checks" not in obligation:
        normalization: dict[str, str] = {}
    else:
        normalization = validate_aspect_matrix(
            obligation.get("normalization_checks"),
            "obligation.normalization_checks",
            NORMALIZATION_ASPECTS,
            NORMALIZATION_STATUSES,
            final,
            errors,
        )

    if not final:
        return normalization
    for field in ("quantifier_scope", "probability_model", "conclusion"):
        field_value = obligation.get(field)
        if not is_nonempty_string(field_value):
            errors.append(f"obligation.{field} must be a nonempty string")
        elif is_forbidden_contract_placeholder(field_value):
            errors.append(
                f"obligation.{field} cannot use an unresolved placeholder"
            )
    for field in ("quantifier_scope", "conclusion"):
        if is_explicit_absence(obligation.get(field)):
            errors.append(f"obligation.{field} cannot use an absence marker")
    for field in ("hypotheses", "definitions", "constant_dependencies"):
        values = validate_string_list(
            obligation.get(field), f"obligation.{field}", errors
        )
        for index, item in enumerate(values, 1):
            if is_forbidden_contract_placeholder(item):
                errors.append(
                    f"obligation.{field}[{index}] cannot use an unresolved "
                    "placeholder"
                )
            if (
                is_explicit_absence(item)
                and normalization.get(field) != "not_applicable"
            ):
                errors.append(
                    f"obligation.{field}[{index}] cannot use an absence marker "
                    "unless the field is not_applicable"
                )
    if not is_enum_value(obligation.get("uniformity"), {
        "pointwise",
        "uniform",
        "mixed",
        "not_applicable",
        "unclear",
    }):
        errors.append("obligation.uniformity has an invalid or missing value")
    if not is_enum_value(obligation.get("regime"), {
        "finite_sample",
        "asymptotic",
        "both",
        "not_applicable",
        "unclear",
    }):
        errors.append("obligation.regime has an invalid or missing value")
    for aspect in ("uniformity", "regime"):
        if (
            obligation.get(aspect) == "unclear"
            and normalization.get(aspect) != "unclear"
        ):
            errors.append(
                f"obligation.{aspect} is unclear but its normalization check is not"
            )
    for aspect in ("quantifiers_and_domains", "conclusion"):
        if normalization.get(aspect) == "not_applicable":
            errors.append(
                f"obligation.normalization_checks[{aspect}] cannot be "
                "not_applicable"
            )

    normalization_fields = {
        "probability_model": "probability_model",
        "hypotheses": "hypotheses",
        "definitions": "definitions",
        "uniformity": "uniformity",
        "regime": "regime",
        "constant_dependencies": "constant_dependencies",
    }
    for aspect, field in normalization_fields.items():
        normalization_status = normalization.get(aspect)
        field_is_absent = is_explicit_absence(obligation.get(field))
        if normalization_status == "not_applicable" and not field_is_absent:
            errors.append(
                f"obligation.normalization_checks[{aspect}] is not_applicable "
                f"but obligation.{field} is substantive"
            )
        elif normalization_status != "not_applicable" and field_is_absent:
            errors.append(
                f"obligation.normalization_checks[{aspect}] is "
                f"{normalization_status!r} but obligation.{field} records only "
                "absence"
            )

    unclear_fields = {
        "quantifier_scope": "quantifiers_and_domains",
        "probability_model": "probability_model",
        "conclusion": "conclusion",
        "uniformity": "uniformity",
        "regime": "regime",
    }
    for field, aspect in unclear_fields.items():
        field_value = obligation.get(field)
        if (
            isinstance(field_value, str)
            and field_value.strip().lower() == "unclear"
            and normalization.get(aspect) != "unclear"
        ):
            errors.append(
                f"obligation.{field} is unclear but its normalization check is not"
            )
    for field in ("hypotheses", "definitions", "constant_dependencies"):
        values = obligation.get(field)
        if (
            isinstance(values, list)
            and any(
                isinstance(item, str) and item.strip().lower() == "unclear"
                for item in values
            )
            and normalization.get(field) != "unclear"
        ):
            errors.append(
                f"obligation.{field} contains an unclear item but its "
                "normalization check is not"
            )
    if isinstance(variables, list):
        variable_is_unclear = any(
            isinstance(variable, dict)
            and any(
                isinstance(variable.get(field), str)
                and variable[field].strip().lower() == "unclear"
                for field in ("symbol", "type", "domain", "quantifier")
            )
            for variable in variables
        )
        if (
            variable_is_unclear
            and normalization.get("quantifiers_and_domains") != "unclear"
        ):
            errors.append(
                "obligation.quantified_variables contains an unclear item but its "
                "normalization check is not"
            )
    return normalization


def validate_dependency_record(
    dependency: Any,
    prefix: str,
    final: bool,
    errors: list[str],
) -> dict[str, Any] | None:
    if not isinstance(dependency, dict):
        errors.append(f"{prefix} must be an object")
        return None
    dependency_id = dependency.get("id")
    kind = dependency.get("kind")
    status = dependency.get("status")
    if not is_nonempty_string(dependency_id):
        errors.append(f"{prefix}.id must be a nonempty string")
    if not is_enum_value(kind, DEPENDENCY_KINDS):
        errors.append(f"{prefix}.kind must be one of {sorted(DEPENDENCY_KINDS)}")
    if not is_enum_value(status, DEPENDENCY_STATUSES):
        errors.append(f"{prefix}.status is invalid: {status!r}")
    use_id = dependency.get("use_id")
    if is_enum_value(kind, {"internal_result", "external_result"}):
        if (
            not isinstance(use_id, str)
            or not DEPENDENCY_USE_ID_RE.fullmatch(use_id)
        ):
            errors.append(f"{prefix}.use_id must match D001 for a result use")
    elif kind == "step" and use_id is not None:
        errors.append(f"{prefix}.use_id is not allowed for a step dependency")
    if kind == "internal_result":
        conclusion_id = dependency.get("conclusion_id")
        if (
            not isinstance(conclusion_id, str)
            or not CONCLUSION_ID_RE.fullmatch(conclusion_id)
        ):
            errors.append(
                f"{prefix}.conclusion_id must identify the exact dependency "
                "conclusion"
            )
    elif kind == "external_result" and dependency.get("conclusion_id") is not None:
        errors.append(
            f"{prefix}.conclusion_id is reserved for internal result conclusions"
        )
    if final and is_enum_value(kind, DEPENDENCY_KINDS):
        if not is_substantive_string(dependency.get("needed_form")):
            errors.append(
                f"{prefix}.needed_form must state the exact form used and cannot "
                "be a reserved placeholder"
            )
        if not is_substantive_string(dependency.get("compatibility_check")):
            errors.append(
                f"{prefix}.compatibility_check must map the result to this use "
                "and cannot be a reserved placeholder"
            )
    return dependency


def validate_independent_check(
    value: Any, final: bool, errors: list[str]
) -> dict[str, Any]:
    if not isinstance(value, dict):
        errors.append("independent_check must be an object")
        return {}
    if not isinstance(value.get("required"), bool):
        errors.append("independent_check.required must be true or false")
    if not is_enum_value(value.get("status"), INDEPENDENT_CHECK_STATUSES):
        errors.append("independent_check.status is invalid")
    if not is_enum_value(value.get("independence_level"), INDEPENDENCE_LEVELS):
        errors.append("independent_check.independence_level is invalid")
    if not is_enum_value(value.get("challenger_verdict"), UNIT_STATUSES):
        errors.append("independent_check.challenger_verdict is invalid")
    reconciled_verdict = value.get("reconciled_verdict")
    if not is_enum_value(reconciled_verdict, UNIT_STATUSES):
        errors.append("independent_check.reconciled_verdict is invalid")
    disagreements = value.get("disagreements")
    if not isinstance(disagreements, list) or not all(
        is_substantive_string(item) for item in disagreements
    ):
        errors.append("independent_check.disagreements must contain substantive strings")
    if final and value.get("required"):
        if not is_enum_value(value.get("status"), {"agreed", "resolved"}):
            errors.append("required independent check must be agreed or resolved")
        if not is_enum_value(
            value.get("independence_level"), INDEPENDENCE_LEVELS - {"none"}
        ):
            errors.append("required independent check needs a genuine independence level")
        if not is_substantive_string(value.get("artifact")):
            errors.append("required independent check needs an artifact reference")
        if value.get("challenger_verdict") == "not_checked":
            errors.append("required independent check needs a checked challenger verdict")
        if value.get("reconciled_verdict") == "not_checked":
            errors.append("required independent check needs a reconciled verdict")
        if value.get("status") == "agreed" and disagreements:
            errors.append("agreed independent check must have no disagreements")
        if value.get("status") == "resolved" and not is_substantive_string(
            value.get("resolution")
        ):
            errors.append("resolved independent disagreement needs a resolution record")
    return value


def validate_premise_uses(
    value: Any,
    prefix: str,
    obligation: Any,
    ledger_dir: Path,
    dependencies_by_id: dict[str, dict[str, Any]],
    prior_step_statuses: dict[str, str],
    prior_step_kinds: dict[str, str],
    prior_step_claims: dict[str, str],
    prior_step_ranges: dict[str, tuple[int, int]],
    source_path: Path,
    final: bool,
    errors: list[str],
) -> tuple[dict[str, dict[str, Any]], set[str]]:
    if value is None and not final:
        return {}, set()
    if not isinstance(value, list):
        errors.append(f"{prefix}.premise_uses must be a list")
        return {}, set()

    premises: dict[str, dict[str, Any]] = {}
    used_dependencies: set[str] = set()
    for index, premise in enumerate(value, 1):
        item_prefix = f"{prefix}.premise_uses[{index}]"
        if not isinstance(premise, dict):
            errors.append(f"{item_prefix} must be an object")
            continue
        premise_id = premise.get("id")
        if not isinstance(premise_id, str) or not PREMISE_ID_RE.fullmatch(premise_id):
            errors.append(f"{item_prefix}.id must match P001")
            continue
        if premise_id in premises:
            errors.append(f"{prefix}: duplicate premise id {premise_id}")
            continue
        premises[premise_id] = premise
        if not is_enum_value(premise.get("role"), PREMISE_ROLES):
            errors.append(f"{item_prefix}.role is invalid")
        if not is_substantive_string(premise.get("claim")):
            errors.append(
                f"{item_prefix}.claim must be a nonempty string and cannot be a "
                "reserved placeholder"
            )
        if not is_substantive_string(premise.get("evidence")):
            errors.append(
                f"{item_prefix}.evidence must be a nonempty string and cannot be "
                "a reserved placeholder"
            )
        source_reference_id = premise.get("source_reference_id")
        source_occurrence_id = premise.get("source_reference_occurrence_id")
        if (
            "source_reference_id" in premise
            and not is_nonempty_string(source_reference_id)
        ):
            errors.append(f"{item_prefix}.source_reference_id must be nonempty")
        if (
            "source_reference_occurrence_id" in premise
            and not is_nonempty_string(source_occurrence_id)
        ):
            errors.append(
                f"{item_prefix}.source_reference_occurrence_id must be nonempty"
            )
        if final and bool(is_nonempty_string(source_reference_id)) != bool(
            is_nonempty_string(source_occurrence_id)
        ):
            errors.append(
                f"{item_prefix} source reference anchoring requires both target "
                "and occurrence IDs"
            )

        origin = premise.get("origin")
        if not isinstance(origin, dict):
            errors.append(f"{item_prefix}.origin must be an object")
            continue
        kind = origin.get("kind")
        reference = origin.get("reference")
        if not is_enum_value(kind, PREMISE_ORIGIN_KINDS):
            errors.append(f"{item_prefix}.origin.kind is invalid")
            continue
        if not is_nonempty_string(reference):
            errors.append(f"{item_prefix}.origin.reference must be a nonempty string")
            continue

        if is_nonempty_string(source_reference_id) and kind not in {
            "obligation",
            "prior_step",
        }:
            errors.append(
                f"{item_prefix}.source_reference_id requires an obligation or "
                "prior-step origin with an exact locked anchor"
            )

        if kind == "obligation":
            root_name = reference[1:].split("/", 1)[0] if reference.startswith("/") else ""
            found, resolved = resolve_json_pointer(obligation, reference)
            if root_name not in OBLIGATION_PREMISE_ROOTS or not found:
                errors.append(
                    f"{item_prefix} has unresolved obligation premise {reference}"
                )
            elif isinstance(resolved, (list, dict)) or resolved in (None, ""):
                errors.append(
                    f"{item_prefix} obligation premise must resolve to one concrete item"
                )
            elif isinstance(resolved, str) and (
                is_explicit_absence(resolved)
                or resolved.strip().lower() == "unclear"
            ):
                errors.append(
                    f"{item_prefix} cannot use an absence or unresolved marker "
                    "as a premise"
                )
            elif isinstance(resolved, str) and premise.get("claim") != resolved:
                errors.append(
                    f"{item_prefix}.claim must exactly match its string-valued "
                    "obligation premise"
                )

            anchor = origin.get("anchor")
            if not isinstance(anchor, dict):
                errors.append(f"{item_prefix}.origin.anchor must be an object")
                continue
            anchor_kind = anchor.get("kind")
            anchor_index = anchor.get("index")
            anchor_field = (
                {
                    "statement_span": "statement_spans",
                    "context_span": "context_spans",
                }.get(anchor_kind)
                if isinstance(anchor_kind, str)
                else None
            )
            if anchor_field is None or not is_int(anchor_index) or anchor_index < 1:
                errors.append(
                    f"{item_prefix}.origin.anchor needs statement_span or "
                    "context_span and a one-based index"
                )
                continue
            anchor_values = (
                obligation.get(anchor_field, []) if isinstance(obligation, dict) else []
            )
            if not isinstance(anchor_values, list) or anchor_index > len(anchor_values):
                errors.append(f"{item_prefix}.origin.anchor is out of range")
            elif (
                is_nonempty_string(source_reference_id)
                and not locked_span_contains_label(
                    anchor_values[anchor_index - 1],
                    ledger_dir,
                    source_reference_id,
                )
            ):
                errors.append(
                    f"{item_prefix}.source_reference_id {source_reference_id} "
                    "is not contained in its locked anchor"
                )
        elif kind == "prior_step":
            dependency = dependencies_by_id.get(reference)
            if dependency is None or dependency.get("kind") != "step":
                errors.append(
                    f"{item_prefix} premise step {reference} is not declared "
                    "by this step"
                )
            else:
                used_dependencies.add(reference)
                if final and premise.get("claim") != dependency.get("needed_form"):
                    errors.append(
                        f"{item_prefix}.claim must exactly match dependency "
                        f"{reference} needed_form"
                    )
                prior_claim = prior_step_claims.get(reference)
                if final and not is_nonempty_string(prior_claim):
                    errors.append(
                        f"{item_prefix} premise step {reference} has no exact "
                        "prior claim"
                    )
                elif final and dependency.get("needed_form") != prior_claim:
                    errors.append(
                        f"{item_prefix} dependency {reference} needed_form must "
                        "exactly match the prior step restatement"
                    )
            if reference not in prior_step_statuses:
                errors.append(
                    f"{item_prefix} premise step {reference} is not established "
                    "before use"
                )
            elif prior_step_statuses[reference] == "non_substantive":
                errors.append(
                    f"{item_prefix} cannot use non_substantive step {reference} "
                    "as a premise"
                )
            elif prior_step_kinds.get(reference) == "statement":
                errors.append(
                    f"{item_prefix} cannot use the theorem statement step "
                    f"{reference} as a premise"
                )
            if is_nonempty_string(source_reference_id):
                prior_range = prior_step_ranges.get(reference)
                if prior_range is None or not locked_span_contains_label(
                    {
                        "file": relative_or_absolute(source_path, ledger_dir),
                        "start_line": prior_range[0],
                        "end_line": prior_range[1],
                    },
                    ledger_dir,
                    source_reference_id,
                ):
                    errors.append(
                        f"{item_prefix}.source_reference_id {source_reference_id} "
                        f"is not active inside earlier step {reference}"
                    )
        else:
            dependency = dependencies_by_id.get(reference)
            if dependency is None or dependency.get("kind") != kind:
                errors.append(
                    f"{item_prefix} premise dependency {reference} is not declared "
                    "by this step"
                )
            else:
                used_dependencies.add(reference)
                if final and premise.get("claim") != dependency.get("needed_form"):
                    errors.append(
                        f"{item_prefix}.claim must exactly match dependency "
                        f"{reference} needed_form"
                    )

    return premises, used_dependencies


def validate_inference_record(
    value: Any,
    prefix: str,
    restatement: Any,
    premises: dict[str, dict[str, Any]],
    atomicity_status: Any,
    step_status: Any,
    step_issue_ids: set[str],
    covered_lines: list[int],
    final: bool,
    errors: list[str],
) -> tuple[dict[str, int], set[str], set[str]]:
    if value is None and not final:
        return {}, set(), set()
    if not isinstance(value, dict):
        errors.append(f"{prefix}.inference must be an object")
        return {}, set(), set()
    moves = value.get("moves")
    if not isinstance(moves, list):
        errors.append(f"{prefix}.inference.moves must be a list")
        moves = []

    move_ids: dict[str, int] = {}
    failed_move_ids: set[str] = set()
    ordered_move_ids: list[str] = []
    used_premises: set[str] = set()
    for index, move in enumerate(moves, 1):
        move_prefix = f"{prefix}.inference.moves[{index}]"
        if not isinstance(move, dict):
            errors.append(f"{move_prefix} must be an object")
            continue
        move_id = move.get("id")
        if not isinstance(move_id, str) or not MOVE_ID_RE.fullmatch(move_id):
            errors.append(f"{move_prefix}.id must match M001")
            continue
        if move_id in move_ids:
            errors.append(f"{prefix}: duplicate inference move id {move_id}")
            continue
        move_ids[move_id] = index
        ordered_move_ids.append(move_id)
        if (
            final
            and atomicity_status == "source_indivisible_chain"
            and len(covered_lines) > 1
        ):
            source_range = move.get("source_line_range")
            if (
                not isinstance(source_range, list)
                or len(source_range) != 2
                or not all(is_int(item) for item in source_range)
            ):
                errors.append(
                    f"{move_prefix}.source_line_range must be [start, end] "
                    "for a multiline indivisible source unit"
                )
            elif (
                source_range[0] > source_range[1]
                or source_range[0] < covered_lines[0]
                or source_range[1] > covered_lines[-1]
            ):
                errors.append(
                    f"{move_prefix}.source_line_range lies outside the step"
                )
        for field in ("claim", "rule", "justification"):
            if not is_substantive_string(move.get(field)):
                errors.append(
                    f"{move_prefix}.{field} must be a nonempty string and cannot "
                    "be a reserved placeholder"
                )

        failure = move.get("failure")
        failure_supports_zero_input = False
        if failure is not None:
            failed_move_ids.add(move_id)
            if not is_enum_value(step_status, FAILED_STEP_STATUSES):
                errors.append(
                    f"{move_prefix}.failure is allowed only on a failed or "
                    "unclear step"
                )
            if not isinstance(failure, dict):
                errors.append(f"{move_prefix}.failure must be an object")
            else:
                failure_kind = failure.get("kind")
                failure_issue_id = failure.get("issue_id")
                failure_evidence = failure.get("evidence")
                valid_failure_kind = (
                    isinstance(failure_kind, str)
                    and failure_kind in MOVE_FAILURE_KINDS
                )
                if not valid_failure_kind:
                    errors.append(f"{move_prefix}.failure.kind is invalid")
                elif step_status != MOVE_FAILURE_STEP_STATUSES[failure_kind]:
                    errors.append(
                        f"{move_prefix}.failure.kind {failure_kind} requires "
                        f"step status {MOVE_FAILURE_STEP_STATUSES[failure_kind]}"
                    )
                valid_failure_issue = (
                    isinstance(failure_issue_id, str)
                    and bool(ISSUE_ID_RE.fullmatch(failure_issue_id))
                    and failure_issue_id in step_issue_ids
                )
                if not valid_failure_issue:
                    errors.append(
                        f"{move_prefix}.failure.issue_id must reference a "
                        "step issue_id"
                    )
                if not is_substantive_string(failure_evidence):
                    errors.append(
                        f"{move_prefix}.failure.evidence must be nonempty and substantive"
                    )
                failure_supports_zero_input = (
                    valid_failure_kind
                    and failure_kind in ZERO_INPUT_FAILURE_KINDS
                    and step_status == MOVE_FAILURE_STEP_STATUSES[failure_kind]
                    and valid_failure_issue
                    and is_substantive_string(failure_evidence)
                )

        premise_ids = move.get("premise_ids")
        if not isinstance(premise_ids, list) or not all(
            isinstance(item, str) for item in premise_ids
        ):
            errors.append(f"{move_prefix}.premise_ids must be a list of premise IDs")
            premise_ids = []
        if len(premise_ids) != len(set(premise_ids)):
            errors.append(f"{move_prefix}.premise_ids contains duplicates")
        for premise_id in premise_ids:
            if premise_id not in premises:
                errors.append(f"{move_prefix} uses unknown premise {premise_id}")
            else:
                used_premises.add(premise_id)

        prior_move_ids = move.get("prior_move_ids")
        if not isinstance(prior_move_ids, list) or not all(
            isinstance(item, str) for item in prior_move_ids
        ):
            errors.append(
                f"{move_prefix}.prior_move_ids must be a list of earlier move IDs"
            )
            prior_move_ids = []
        if len(prior_move_ids) != len(set(prior_move_ids)):
            errors.append(f"{move_prefix}.prior_move_ids contains duplicates")
        for prior_id in prior_move_ids:
            if prior_id not in set(ordered_move_ids[:-1]):
                errors.append(
                    f"{move_prefix} inference move {prior_id} is not established "
                    "before use"
                )
        if final and not premise_ids and not prior_move_ids:
            if is_enum_value(step_status, FAILED_STEP_STATUSES):
                if not failure_supports_zero_input:
                    errors.append(
                        f"{move_prefix} zero-input failed move requires a "
                        "zero-input-compatible failure kind, evidence, and "
                        "step issue link"
                    )
            else:
                errors.append(
                    f"{move_prefix} must use at least one premise or earlier move"
                )

    conclusion_move = value.get("conclusion_move")
    if atomicity_status == "non_inferential":
        if moves:
            errors.append(f"{prefix}: non_inferential step cannot contain inference moves")
        if premises:
            errors.append(f"{prefix}: non_inferential step cannot declare premise uses")
        if conclusion_move is not None:
            errors.append(f"{prefix}: non_inferential step needs null conclusion_move")
    else:
        if atomicity_status == "single_move" and len(moves) != 1:
            errors.append(f"{prefix}: single_move step must contain exactly one move")
        if atomicity_status == "source_indivisible_chain" and len(moves) < 2:
            errors.append(
                f"{prefix}: source_indivisible_chain must contain at least two moves"
            )
        if (
            atomicity_status == "source_indivisible_chain"
            and len(covered_lines) > 1
            and moves
        ):
            ranges = [
                move.get("source_line_range")
                for move in moves
                if isinstance(move, dict)
                and isinstance(move.get("source_line_range"), list)
                and len(move["source_line_range"]) == 2
                and all(is_int(item) for item in move["source_line_range"])
            ]
            if len(ranges) == len(moves):
                if any(
                    current[0] < previous[0] or current[1] < previous[1]
                    for previous, current in zip(ranges, ranges[1:])
                ):
                    errors.append(
                        f"{prefix}: source_line_range records must follow source order"
                    )
                represented = {
                    line
                    for source_range in ranges
                    for line in range(source_range[0], source_range[1] + 1)
                }
                if represented != set(covered_lines):
                    errors.append(
                        f"{prefix}: multiline indivisible moves do not represent "
                        "every covered source line"
                    )
        if ordered_move_ids:
            if conclusion_move != ordered_move_ids[-1]:
                errors.append(
                    f"{prefix}.inference.conclusion_move must be the final move"
                )
            final_move = moves[-1] if isinstance(moves[-1], dict) else {}
            if final_move.get("claim") != restatement:
                errors.append(
                    f"{prefix}: final inference claim must exactly match restatement"
                )
        elif final:
            errors.append(f"{prefix}: inferential step needs at least one move")
    return move_ids, used_premises, failed_move_ids


def validate_move_reachability(
    inference: Any,
    side_conditions: Any,
    extra_roots: Iterable[str],
    prefix: str,
    final: bool,
    errors: list[str],
) -> None:
    if not final or not isinstance(inference, dict):
        return
    moves = inference.get("moves")
    if not isinstance(moves, list):
        return

    graph: dict[str, set[str]] = {}
    for move in moves:
        if not isinstance(move, dict):
            continue
        move_id = move.get("id")
        if not isinstance(move_id, str) or not MOVE_ID_RE.fullmatch(move_id):
            continue
        prior_move_ids = move.get("prior_move_ids")
        graph[move_id] = (
            {
                prior_id
                for prior_id in prior_move_ids
                if isinstance(prior_id, str) and prior_id in graph
            }
            if isinstance(prior_move_ids, list)
            else set()
        )

    if isinstance(side_conditions, list):
        for condition in side_conditions:
            if (
                not isinstance(condition, dict)
                or condition.get("status") != "discharged"
            ):
                continue
            generated_by = condition.get("generated_by")
            discharge = condition.get("discharge")
            if not isinstance(discharge, dict):
                continue
            sources = discharge.get("sources")
            if not isinstance(sources, list):
                continue
            for source in sources:
                if (
                    not isinstance(source, dict)
                    or source.get("kind") != "inference_move"
                ):
                    continue
                reference = source.get("reference")
                if (
                    isinstance(generated_by, str)
                    and isinstance(reference, str)
                    and generated_by in graph
                    and reference in graph
                ):
                    graph[generated_by].add(reference)

    conclusion_move = inference.get("conclusion_move")
    roots = {
        root
        for root in [conclusion_move, *extra_roots]
        if isinstance(root, str) and root in graph
    }
    if not roots:
        return
    reachable: set[str] = set()
    pending = list(roots)
    while pending:
        move_id = pending.pop()
        if move_id in reachable:
            continue
        reachable.add(move_id)
        pending.extend(graph.get(move_id, set()) - reachable)
    orphaned = sorted(set(graph) - reachable)
    if orphaned:
        errors.append(
            f"{prefix}: inference moves are not load-bearing for the conclusion: "
            + ", ".join(orphaned)
        )


def validate_side_conditions(
    value: Any,
    prefix: str,
    premises: dict[str, dict[str, Any]],
    move_ids: dict[str, int],
    failed_move_ids: set[str],
    final: bool,
    errors: list[str],
) -> tuple[set[str], set[str]]:
    if value is None and not final:
        return set(), set()
    if not isinstance(value, list):
        errors.append(f"{prefix}.side_conditions must be a list")
        return set(), set()
    seen: set[str] = set()
    open_ids: set[str] = set()
    discharge_premises: set[str] = set()
    for index, condition in enumerate(value, 1):
        item_prefix = f"{prefix}.side_conditions[{index}]"
        if not isinstance(condition, dict):
            errors.append(f"{item_prefix} must be an object")
            continue
        condition_id = condition.get("id")
        if (
            not isinstance(condition_id, str)
            or not SIDE_CONDITION_ID_RE.fullmatch(condition_id)
        ):
            errors.append(f"{item_prefix}.id must match SC001")
            continue
        if condition_id in seen:
            errors.append(f"{prefix}: duplicate side-condition id {condition_id}")
            continue
        seen.add(condition_id)
        if not is_substantive_string(condition.get("condition")):
            errors.append(
                f"{item_prefix}.condition must be a nonempty string and cannot be "
                "a reserved placeholder"
            )
        generated_by = condition.get("generated_by")
        if not is_nonempty_string(generated_by) or generated_by not in move_ids:
            errors.append(
                f"{item_prefix}.generated_by must name an inference move in this step"
            )
        status = condition.get("status")
        if not is_enum_value(status, {"discharged", "open"}):
            errors.append(f"{item_prefix}.status is invalid")
            continue
        if status == "open":
            open_ids.add(condition_id)
            if condition.get("discharge") not in (None, {}):
                errors.append(f"{item_prefix}: open condition cannot have a discharge")
            continue

        discharge = condition.get("discharge")
        if not isinstance(discharge, dict):
            errors.append(f"{item_prefix}.discharge must be an object")
            continue
        sources = discharge.get("sources")
        if not isinstance(sources, list) or not sources:
            errors.append(
                f"{item_prefix}.discharge.sources must be a nonempty list"
            )
            sources = []
        seen_sources: set[tuple[str, str]] = set()
        for source_index, source in enumerate(sources, 1):
            source_prefix = (
                f"{item_prefix}.discharge.sources[{source_index}]"
            )
            if not isinstance(source, dict):
                errors.append(f"{source_prefix} must be an object")
                continue
            kind = source.get("kind")
            reference = source.get("reference")
            if not is_enum_value(kind, DISCHARGE_KINDS):
                errors.append(f"{source_prefix}.kind is invalid")
                continue
            if not is_nonempty_string(reference):
                errors.append(f"{source_prefix}.reference must be nonempty")
                continue
            key = (kind, reference)
            if key in seen_sources:
                errors.append(
                    f"{item_prefix}.discharge contains duplicate source "
                    f"{kind}:{reference}"
                )
            seen_sources.add(key)
            if not is_substantive_string(source.get("contribution")):
                errors.append(
                    f"{source_prefix}.contribution must be substantive"
                )
            if kind == "premise":
                if reference not in premises:
                    errors.append(
                        f"{condition_id} has unknown discharge premise {reference}"
                    )
                else:
                    discharge_premises.add(reference)
            elif reference not in move_ids:
                errors.append(
                    f"{condition_id} has unknown discharge move {reference}"
                )
            elif reference in failed_move_ids:
                errors.append(
                    f"{condition_id} cannot use failed move {reference} as "
                    "discharge evidence"
                )
            elif (
                isinstance(generated_by, str)
                and generated_by in move_ids
                and move_ids[reference] >= move_ids[generated_by]
            ):
                errors.append(
                    f"{condition_id} discharge move {reference} is not established "
                    f"before generating move {generated_by}"
                )
        if not is_substantive_string(discharge.get("rule")):
            errors.append(
                f"{condition_id} discharge rule must be nonempty and substantive"
            )
        if not is_substantive_string(discharge.get("evidence")):
            errors.append(
                f"{condition_id} discharge evidence must be nonempty and substantive"
            )
    return open_ids, discharge_premises


def validate_condition_records(
    value: Any,
    prefix: str,
    unresolved: set[tuple[str, str]],
    status: Any,
    final: bool,
    errors: list[str],
) -> None:
    if value is None:
        value = []
    if not isinstance(value, list):
        errors.append(f"{prefix}.conditions must be a list")
        return
    seen: set[tuple[str, str]] = set()
    for index, condition in enumerate(value, 1):
        item_prefix = f"{prefix}.conditions[{index}]"
        if not isinstance(condition, dict):
            errors.append(f"{item_prefix} must be an object")
            continue
        kind = condition.get("kind")
        reference = condition.get("reference")
        if not is_enum_value(kind, CONDITION_KINDS):
            errors.append(f"{item_prefix}.kind is invalid")
            continue
        if not is_nonempty_string(reference):
            errors.append(f"{item_prefix}.reference must be nonempty")
            continue
        key = (kind, reference)
        if key in seen:
            errors.append(f"{prefix}: duplicate condition reference {kind}:{reference}")
        seen.add(key)
        if not is_substantive_string(condition.get("condition")):
            errors.append(
                f"{item_prefix}.condition must be a nonempty string and cannot be "
                "a reserved placeholder"
            )

    if not final:
        return
    if status == "conditionally_verified":
        missing = unresolved - seen
        extra = seen - unresolved
        if missing or extra or not unresolved:
            details: list[str] = []
            if missing:
                details.append(
                    "missing " + ", ".join(f"{kind}:{ref}" for kind, ref in sorted(missing))
                )
            if extra:
                details.append(
                    "unresolved target absent for "
                    + ", ".join(f"{kind}:{ref}" for kind, ref in sorted(extra))
                )
            if not unresolved:
                details.append("no unresolved cause exists")
            errors.append(
                f"{prefix}.conditions must match every unresolved conditional cause"
                + (": " + "; ".join(details) if details else "")
            )
    elif seen:
        errors.append(f"{prefix}: conditions are only allowed on conditionally_verified steps")


def check_ledger_data(
    ledger_path: Path, final: bool = False
) -> tuple[list[str], dict[str, Any]]:
    errors: list[str] = []
    try:
        ledger = json.loads(read_text(ledger_path))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return [f"Cannot read ledger {ledger_path}: {exc}"], {}
    if not isinstance(ledger, dict):
        return [f"Ledger root must be an object: {ledger_path}"], {}

    if ledger.get("schema_version") != SCHEMA_VERSION:
        errors.append(
            f"Unsupported ledger schema_version {ledger.get('schema_version')!r}; "
            f"expected {SCHEMA_VERSION}"
        )
    evidence_contract_version = ledger.get("evidence_contract_version")
    if (
        evidence_contract_version is not None
        and evidence_contract_version != EVIDENCE_CONTRACT_VERSION
    ):
        errors.append(
            "Unsupported evidence_contract_version "
            f"{evidence_contract_version!r}; expected {EVIDENCE_CONTRACT_VERSION}"
        )
    elif final and evidence_contract_version != EVIDENCE_CONTRACT_VERSION:
        errors.append(
            "Final ledger requires evidence_contract_version "
            f"{EVIDENCE_CONTRACT_VERSION}; legacy free-text evidence is inspection-only"
        )
    unit_id = ledger.get("unit_id")
    if not is_nonempty_string(unit_id):
        errors.append("unit_id must be a nonempty string")
        unit_id = None

    source_info = ledger.get("source")
    if not isinstance(source_info, dict):
        return ["Missing source object"], {}
    try:
        start_value = source_info["start_line"]
        end_value = source_info["end_line"]
        file_value = source_info["file"]
        if not is_int(start_value) or not is_int(end_value):
            raise TypeError("start_line and end_line must be integers")
        if not is_nonempty_string(file_value):
            raise TypeError("file must be a nonempty string")
        start = start_value
        end = end_value
        source = resolve_stored_path(file_value, ledger_path.parent)
    except (KeyError, TypeError, ValueError) as exc:
        return [f"Invalid source specification: {exc}"], {}
    coverage_mode = source_info.get("coverage_mode")
    if not is_enum_value(coverage_mode, {
        "statement_and_proof",
        "proof_with_separate_statement",
    }):
        errors.append("source.coverage_mode is invalid or missing")
    if (
        final
        and coverage_mode == "proof_with_separate_statement"
        and not is_substantive_string(source_info.get("separate_statement_reason"))
    ):
        errors.append(
            "source.separate_statement_reason is required when the statement is outside "
            "the ledger range"
        )

    valid_range = True
    if start < 1 or end < start:
        errors.append(f"Invalid source range: {start}-{end}")
        valid_range = False
    elif end - start + 1 > MAX_UNIT_LINES:
        errors.append(
            f"Source range contains more than {MAX_UNIT_LINES} physical lines; "
            "split the audit unit or inspect the range"
        )
        valid_range = False
    source_lines = ledger.get("source_lines")
    if not isinstance(source_lines, list):
        errors.append("source_lines must be a list")
        source_lines = []

    current_selected: list[str] = []
    if not source.is_file():
        errors.append(f"Source file not found: {source}")
    elif valid_range:
        current = read_lines(source)
        if end > len(current):
            errors.append(f"Source now has only {len(current)} lines; ledger ends at {end}")
        else:
            current_selected = current[start - 1 : end]
            current_hash = sha256_text("\n".join(current_selected))
            if current_hash != source_info.get("unit_sha256"):
                errors.append("Source drift: unit SHA-256 no longer matches the ledger")
    if valid_range:
        expected_count = end - start + 1
        if len(source_lines) != expected_count:
            errors.append(
                f"source_lines must contain exactly {expected_count} ordered records"
            )
        for offset, item in enumerate(source_lines):
            line_number = start + offset
            if not isinstance(item, dict):
                errors.append(f"source_lines[{offset + 1}] must be an object")
                continue
            if item.get("line") != line_number:
                errors.append(
                    f"source_lines[{offset + 1}].line must be {line_number}"
                )
            text = item.get("text")
            if not isinstance(text, str) or item.get("sha256") != sha256_text(text):
                errors.append(f"Invalid locked text or hash at source line {line_number}")
            if current_selected and offset < len(current_selected):
                current_text = current_selected[offset]
                if text != current_text:
                    errors.append(f"Locked source mismatch at line {line_number}")

    obligation = ledger.get("obligation")
    normalization_statuses = validate_obligation(obligation, ledger_path, final, errors)
    obligation_statement_spans: list[dict[str, Any]] = []
    obligation_context_spans: list[dict[str, Any]] = []
    if isinstance(obligation, dict):
        statement_spans = obligation.get("statement_spans")
        if isinstance(statement_spans, list):
            for span in statement_spans:
                metadata = resolved_span_metadata(span, ledger_path.parent)
                if metadata:
                    obligation_statement_spans.append(metadata)
        context_spans = obligation.get("context_spans")
        if isinstance(context_spans, list):
            for span in context_spans:
                metadata = resolved_span_metadata(span, ledger_path.parent)
                if metadata:
                    obligation_context_spans.append(metadata)

    steps = ledger.get("steps")
    if not isinstance(steps, list):
        errors.append("steps must be a list")
        steps = []
    coverage: dict[int, list[str]] = defaultdict(list)
    step_ids: set[str] = set()
    step_status_by_id: dict[str, str] = {}
    step_kind_by_id: dict[str, str] = {}
    step_claim_by_id: dict[str, str] = {}
    premise_records_by_step: dict[str, dict[str, dict[str, Any]]] = {}
    step_ranges_by_id: dict[str, tuple[int, int]] = {}
    step_dependency_claims: list[tuple[str, str, str]] = []
    result_dependency_claims: list[dict[str, Any]] = []
    statuses: list[str] = []
    issue_references: set[str] = set()
    issue_links: list[dict[str, str]] = []
    previous_step_end = start - 1

    for index, step in enumerate(steps, 1):
        prefix = f"Step {index}"
        if not isinstance(step, dict):
            errors.append(f"{prefix} must be an object")
            continue
        step_id = step.get("id")
        if not isinstance(step_id, str) or not STEP_ID_RE.fullmatch(step_id):
            errors.append(f"{prefix} has invalid id; expected S001 or S001.1")
            step_id = f"invalid-{index}"
        elif step_id in step_ids:
            errors.append(f"Duplicate step id: {step_id}")
        step_ids.add(step_id)
        prefix = step_id

        line_range = step.get("lines")
        covered_lines: list[int] = []
        if (
            not isinstance(line_range, list)
            or len(line_range) != 2
            or not all(is_int(value) for value in line_range)
        ):
            errors.append(f"{prefix}: lines must be [start, end]")
        else:
            step_start, step_end = line_range
            if step_start > step_end:
                errors.append(f"{prefix}: line range is reversed")
            elif step_start < start or step_end > end:
                errors.append(
                    f"{prefix}: line range {step_start}-{step_end} is outside {start}-{end}"
                )
            else:
                covered_lines = list(range(step_start, step_end + 1))
                for line_number in covered_lines:
                    coverage[line_number].append(step_id)
                if step_start <= previous_step_end:
                    errors.append(f"{prefix}: steps must appear in source order")
                previous_step_end = max(previous_step_end, step_end)
                step_ranges_by_id[step_id] = (step_start, step_end)

        kind = step.get("kind")
        if not is_enum_value(kind, STEP_KINDS):
            errors.append(f"{prefix}: invalid or missing kind {kind!r}")
        else:
            step_kind_by_id[step_id] = kind

        status = step.get("status")
        if not is_enum_value(status, STEP_STATUSES):
            errors.append(f"{prefix}: invalid status {status!r}")
        else:
            statuses.append(status)
            step_status_by_id[step_id] = status

        issue_ids = step.get("issue_ids", [])
        if not isinstance(issue_ids, list) or not all(
            isinstance(issue_id, str) and ISSUE_ID_RE.fullmatch(issue_id)
            for issue_id in issue_ids
        ):
            errors.append(f"{prefix}: issue_ids must contain IDs such as I-001")
            issue_ids = []
        issue_references.update(issue_ids)
        issue_links.extend(
            {"issue_id": issue_id, "step_id": step_id, "step_status": str(status)}
            for issue_id in issue_ids
        )

        if is_enum_value(status, {"gap", "incorrect", "unclear"}) and not issue_ids:
            errors.append(f"{prefix}: status {status} requires at least one issue ID")
        if final and status == "not_checked":
            errors.append(f"{prefix}: not_checked is not allowed with --final")

        if status == "non_substantive":
            if current_selected and covered_lines:
                texts = [current_selected[number - start] for number in covered_lines]
                if not all(is_non_substantive(text) for text in texts):
                    errors.append(
                        f"{prefix}: non_substantive covers prose or mathematical content"
                    )
            continue

        if final and status != "not_checked":
            restatement = step.get("restatement")
            if not is_substantive_string(restatement):
                errors.append(
                    f"{prefix}: substantive step needs a restatement that is not "
                    "a reserved placeholder"
                )
            if not is_substantive_string(step.get("goal")):
                errors.append(
                    f"{prefix}: substantive step needs its current goal, not a "
                    "reserved placeholder"
                )
        if is_substantive_string(step.get("restatement")):
            step_claim_by_id[step_id] = step["restatement"]


        if final and evidence_contract_version == EVIDENCE_CONTRACT_VERSION:
            legacy_fields = [
                field for field in ("required_facts", "assumptions") if field in step
            ]
            if legacy_fields:
                errors.append(
                    f"{prefix}: legacy free-text fields are not allowed by evidence "
                    f"contract {EVIDENCE_CONTRACT_VERSION}: "
                    + ", ".join(legacy_fields)
                )

        dependencies = step.get("dependencies", [])
        if not isinstance(dependencies, list):
            errors.append(f"{prefix}: dependencies must be a list")
            dependencies = []
        dependencies_by_id: dict[str, dict[str, Any]] = {}
        dependency_statuses: list[str] = []
        for dependency_index, dependency in enumerate(dependencies, 1):
            record = validate_dependency_record(
                dependency,
                f"{prefix}.dependencies[{dependency_index}]",
                final,
                errors,
            )
            if record is None:
                continue
            dependency_id = record.get("id")
            dependency_key = (
                dependency_id
                if record.get("kind") == "step"
                else record.get("use_id")
            )
            dependency_status = record.get("status")
            if is_nonempty_string(dependency_key):
                if dependency_key in dependencies_by_id:
                    errors.append(f"{prefix}: duplicate dependency use {dependency_key}")
                else:
                    dependencies_by_id[dependency_key] = record
            if is_enum_value(dependency_status, DEPENDENCY_STATUSES):
                dependency_statuses.append(dependency_status)
                if dependency_status == "not_applicable":
                    errors.append(
                        f"{prefix}: declared dependency {dependency_id} cannot be "
                        "not_applicable; omit it instead"
                    )
            if (
                is_nonempty_string(dependency_id)
                and is_enum_value(dependency_status, DEPENDENCY_STATUSES)
            ):
                if record.get("kind") == "step":
                    step_dependency_claims.append(
                        (prefix, dependency_id, dependency_status)
                    )
                elif is_enum_value(
                    record.get("kind"), {"internal_result", "external_result"}
                ):
                    result_dependency_claims.append(
                        {
                            "owner_step": prefix,
                            "use_id": record.get("use_id"),
                            "id": dependency_id,
                            "kind": record.get("kind"),
                            "conclusion_id": record.get("conclusion_id"),
                            "status": dependency_status,
                            "needed_form": record.get("needed_form"),
                            "compatibility_check": record.get("compatibility_check"),
                        }
                    )

        checks = step.get("checks")
        atomicity_status: str | None = None
        if final and status != "not_checked":
            if not isinstance(checks, dict):
                errors.append(f"{prefix}.checks must be an object")
            else:
                if not is_substantive_string(checks.get("literal")):
                    errors.append(f"{prefix}.checks.literal must be nonempty and substantive")
                validate_string_list(
                    checks.get("adversarial"),
                    f"{prefix}.checks.adversarial",
                    errors,
                    substantive=True,
                )
                atomicity = checks.get("atomicity")
                if not isinstance(atomicity, dict):
                    errors.append(f"{prefix}.checks.atomicity must be an object")
                else:
                    atomicity_status = atomicity.get("status")
                    if not is_enum_value(atomicity_status, ATOMICITY_STATUSES):
                        errors.append(f"{prefix}.checks.atomicity.status is invalid")
                    if not is_substantive_string(atomicity.get("evidence")):
                        errors.append(
                            f"{prefix}.checks.atomicity.evidence must be nonempty and substantive"
                        )
                    if (
                        atomicity_status == "non_inferential"
                        and not is_enum_value(
                            kind, {"statement", "setup", "definition"}
                        )
                    ):
                        errors.append(
                            f"{prefix}: {kind} step must declare at least one "
                            "inferential move"
                        )
                    if (
                        atomicity_status == "source_indivisible_chain"
                    ):
                        source_unit_kind = atomicity.get("source_unit_kind")
                        allowed_source_units = {
                            "one_line",
                            "continued_sentence",
                            "continued_display",
                        }
                        if not is_enum_value(
                            source_unit_kind, allowed_source_units
                        ):
                            errors.append(
                                f"{prefix}: source_indivisible_chain needs a valid "
                                "source_unit_kind"
                            )
                        if not is_substantive_string(
                            atomicity.get("partition_evidence")
                        ):
                            errors.append(
                                f"{prefix}: source_indivisible_chain needs "
                                "substantive partition_evidence"
                            )
                        if len(covered_lines) == 1 and source_unit_kind != "one_line":
                            errors.append(
                                f"{prefix}: one physical line requires "
                                "source_unit_kind one_line"
                            )
                        if len(covered_lines) > 1:
                            if source_unit_kind not in {
                                "continued_sentence",
                                "continued_display",
                            }:
                                errors.append(
                                    f"{prefix}: a multiline source unit must be a "
                                    "continued_sentence or continued_display"
                                )
                            texts = [
                                current_selected[line - start]
                                for line in covered_lines
                            ] if current_selected else []
                            if any(
                                not strip_latex_comment(text).strip()
                                for text in texts
                            ):
                                errors.append(
                                    f"{prefix}: a multiline indivisible source unit "
                                    "cannot cross a blank or comment-only separator"
                                )
                if "inferential" in checks:
                    errors.append(
                        f"{prefix}: checks.inferential is legacy free text; "
                        "use the structured inference record"
                    )

        prior_statuses = {
            prior_id: prior_status
            for prior_id, prior_status in step_status_by_id.items()
            if prior_id != step_id
        }
        prior_kinds = {
            prior_id: prior_kind
            for prior_id, prior_kind in step_kind_by_id.items()
            if prior_id != step_id
        }
        prior_claims = {
            prior_id: prior_claim
            for prior_id, prior_claim in step_claim_by_id.items()
            if prior_id != step_id
        }
        premises, used_dependencies = validate_premise_uses(
            step.get("premise_uses"),
            prefix,
            obligation,
            ledger_path.parent,
            dependencies_by_id,
            prior_statuses,
            prior_kinds,
            prior_claims,
            {
                prior_id: prior_range
                for prior_id, prior_range in step_ranges_by_id.items()
                if prior_id != step_id
            },
            source,
            final and status != "not_checked",
            errors,
        )
        premise_records_by_step[step_id] = premises
        move_ids, inference_premises, failed_move_ids = validate_inference_record(
            step.get("inference"),
            prefix,
            step.get("restatement"),
            premises,
            atomicity_status,
            status,
            set(issue_ids),
            covered_lines,
            final and status != "not_checked",
            errors,
        )
        open_side_condition_ids, discharge_premises = validate_side_conditions(
            step.get("side_conditions"),
            prefix,
            premises,
            move_ids,
            failed_move_ids,
            final and status != "not_checked",
            errors,
        )
        validate_move_reachability(
            step.get("inference"),
            step.get("side_conditions"),
            [
                support.get("move_id")
                for result in (
                    ledger.get("review", {}).get("conclusion_results", [])
                    if isinstance(ledger.get("review"), dict)
                    and isinstance(
                        ledger.get("review", {}).get("conclusion_results"),
                        list,
                    )
                    else []
                )
                if isinstance(result, dict)
                and isinstance(
                    support := result.get("support"), dict
                )
                and support.get("step_id") == step_id
                and is_nonempty_string(support.get("move_id"))
            ],
            prefix,
            final and status != "not_checked",
            errors,
        )
        risk_statuses = (
            validate_aspect_matrix(
                step.get("risk_checks"),
                f"{prefix}.risk_checks",
                RISK_ASPECTS,
                RISK_STATUSES,
                final and status != "not_checked",
                errors,
            )
            if final or "risk_checks" in step
            else {}
        )

        unused_premises = set(premises) - inference_premises - discharge_premises
        if final and status != "not_checked" and unused_premises:
            errors.append(
                f"{prefix}: premise uses not consumed by an inference move or "
                "side-condition discharge: "
                + ", ".join(sorted(unused_premises))
            )
        unused_dependencies = set(dependencies_by_id) - used_dependencies
        if final and status != "not_checked" and unused_dependencies:
            errors.append(
                f"{prefix}: dependencies not used by premise_uses: "
                + ", ".join(sorted(unused_dependencies))
            )

        open_risks = {
            aspect for aspect, risk_status in risk_statuses.items()
            if risk_status == "open"
        }
        failed_risks = {
            aspect for aspect, risk_status in risk_statuses.items()
            if risk_status == "failed"
        }
        unclear_risks = {
            aspect for aspect, risk_status in risk_statuses.items()
            if risk_status == "unclear"
        }
        unresolved_causes = {
            ("side_condition", condition_id)
            for condition_id in open_side_condition_ids
        }
        unresolved_causes.update(
            ("dependency", dependency_id)
            for dependency_id, dependency in dependencies_by_id.items()
            if is_enum_value(
                dependency.get("status"), {"conditional", "unchecked"}
            )
        )
        unresolved_causes.update(
            ("risk_check", aspect) for aspect in open_risks
        )
        validate_condition_records(
            step.get("conditions"),
            prefix,
            unresolved_causes,
            status,
            final and status != "not_checked",
            errors,
        )

        if status == "verified":
            invalid_dependencies = [
                value for value in dependency_statuses if value != "verified"
            ]
            if invalid_dependencies:
                errors.append(
                    f"{prefix}: verified step has nonverified dependencies: "
                    + ", ".join(invalid_dependencies)
                )
            if open_side_condition_ids:
                errors.append(f"{prefix}: verified step has an open side condition")
            unresolved_risks = open_risks | failed_risks | unclear_risks
            if unresolved_risks:
                errors.append(
                    f"{prefix}: verified step has unresolved risk checks: "
                    + ", ".join(sorted(unresolved_risks))
                )

        if status == "conditionally_verified":
            invalid_dependencies = [
                value
                for value in dependency_statuses
                if is_enum_value(
                    value, {"gap", "incorrect", "unclear", "not_applicable"}
                )
            ]
            if invalid_dependencies:
                errors.append(
                    f"{prefix}: conditionally_verified cannot hide failed "
                    "dependencies: " + ", ".join(invalid_dependencies)
                )
            invalid_risks = failed_risks | unclear_risks
            if invalid_risks:
                errors.append(
                    f"{prefix}: conditionally_verified cannot hide failed or "
                    "unclear risk checks: " + ", ".join(sorted(invalid_risks))
                )

    dependency_status_from_step = STEP_TO_DEPENDENCY_STATUS
    step_graph: dict[str, set[str]] = {step_id: set() for step_id in step_ids}
    for owner, dependency_id, declared_dependency_status in step_dependency_claims:
        if dependency_id not in step_status_by_id:
            errors.append(f"{owner}: unknown step dependency {dependency_id}")
            continue
        step_graph.setdefault(owner, set()).add(dependency_id)
        owner_range = step_ranges_by_id.get(owner)
        dependency_range = step_ranges_by_id.get(dependency_id)
        if (
            owner_range is not None
            and dependency_range is not None
            and dependency_range[1] >= owner_range[0]
        ):
            errors.append(
                f"{owner}: step dependency {dependency_id} is not established before use"
            )
        actual_dependency_status = dependency_status_from_step[
            step_status_by_id[dependency_id]
        ]
        if declared_dependency_status != actual_dependency_status:
            errors.append(
                f"{owner}: dependency {dependency_id} is declared "
                f"{declared_dependency_status}, but its step status implies "
                f"{actual_dependency_status}"
            )

    cycle = find_cycle(step_graph)
    if cycle:
        errors.append("Step dependency cycle: " + " -> ".join(cycle))

    if valid_range:
        for line_number in range(start, end + 1):
            owners = coverage.get(line_number, [])
            if not owners:
                errors.append(f"Uncovered source line: {line_number}")
            elif len(owners) > 1:
                errors.append(
                    f"Multiply covered source line {line_number}: {', '.join(owners)}"
                )

    expected_status = expected_unit_status(statuses)
    review = ledger.get("review", {})
    if not isinstance(review, dict):
        errors.append("review must be an object")
        review = {}
    declared_status = review.get("unit_status")
    if not is_enum_value(declared_status, UNIT_STATUSES):
        errors.append(f"Invalid or missing review.unit_status: {declared_status!r}")
    if final and declared_status != expected_status:
        errors.append(
            f"Unit verdict mismatch: declared {declared_status!r}, expected {expected_status!r}"
        )
    if final and expected_status == "not_checked":
        errors.append("A final ledger must contain at least one checked substantive step")

    direct_dependencies: list[dict[str, Any]] = []
    direct_value = review.get("direct_dependencies")
    if not isinstance(direct_value, list):
        errors.append("review.direct_dependencies must be a list")
        direct_value = []
    seen_direct: set[str] = set()
    for index, dependency in enumerate(direct_value, 1):
        record = validate_dependency_record(
            dependency,
            f"review.direct_dependencies[{index}]",
            final,
            errors,
        )
        if record is None:
            continue
        if record.get("kind") == "step":
            errors.append("review.direct_dependencies cannot contain step dependencies")
        dependency_id = record.get("id")
        use_id = record.get("use_id")
        if is_nonempty_string(use_id):
            if use_id in seen_direct:
                errors.append(f"Duplicate direct dependency use: {use_id}")
            seen_direct.add(use_id)
            direct_dependencies.append(record)

    source_reference_dispositions: list[dict[str, Any]] = []
    disposition_value = review.get("source_reference_dispositions")
    if not isinstance(disposition_value, list):
        errors.append("review.source_reference_dispositions must be a list")
        disposition_value = []
    seen_dispositions: set[str] = set()
    context_premise_links: set[tuple[str, str, str, str]] = set()
    for index, disposition in enumerate(disposition_value, 1):
        prefix = f"review.source_reference_dispositions[{index}]"
        if not isinstance(disposition, dict):
            errors.append(f"{prefix} must be an object")
            continue
        occurrence_id = disposition.get("occurrence_id")
        target = disposition.get("target")
        command = disposition.get("command")
        if not is_nonempty_string(occurrence_id):
            errors.append(f"{prefix}.occurrence_id must be a nonempty string")
            continue
        if not occurrence_id.startswith("R-"):
            errors.append(f"{prefix}.occurrence_id must be a parser occurrence ID")
        if not is_nonempty_string(target) or not is_nonempty_string(command):
            errors.append(f"{prefix} requires target and command")
        if occurrence_id in seen_dispositions:
            errors.append(f"Duplicate source-reference disposition: {occurrence_id}")
        seen_dispositions.add(occurrence_id)
        disposition_status = disposition.get("disposition")
        if not is_enum_value(disposition_status, {
            "internal_result",
            "obligation_context",
            "local_step",
            "own_result_identification",
            "navigation",
            "non_load_bearing",
            "unresolved",
        }):
            errors.append(f"{prefix}.disposition is invalid")
        premise_links = disposition.get("premise_links")
        premise_roles = {"internal_result", "obligation_context", "local_step"}
        if final and is_enum_value(disposition_status, premise_roles):
            if not isinstance(premise_links, list) or not premise_links:
                errors.append(
                    f"{prefix} {disposition_status} requires nonempty premise_links"
                )
            else:
                seen_links: set[tuple[str, str]] = set()
                for link_index, link in enumerate(premise_links, 1):
                    link_prefix = f"{prefix}.premise_links[{link_index}]"
                    if not isinstance(link, dict):
                        errors.append(f"{link_prefix} must be an object")
                        continue
                    linked_step_id = link.get("step_id")
                    linked_premise_id = link.get("premise_id")
                    if not is_nonempty_string(
                        linked_step_id
                    ) or not is_nonempty_string(linked_premise_id):
                        errors.append(
                            f"{link_prefix} requires step_id and premise_id"
                        )
                        continue
                    link_key = (linked_step_id, linked_premise_id)
                    if link_key in seen_links:
                        errors.append(
                            f"{prefix} contains duplicate premise link "
                            f"{linked_step_id}/{linked_premise_id}"
                        )
                        continue
                    seen_links.add(link_key)
                    linked_premise = premise_records_by_step.get(
                        linked_step_id, {}
                    ).get(linked_premise_id)
                    if linked_premise is None:
                        errors.append(
                            f"{link_prefix} does not resolve to a premise"
                        )
                    elif (
                        linked_premise.get("source_reference_id") != target
                        or linked_premise.get(
                            "source_reference_occurrence_id"
                        )
                        != occurrence_id
                    ):
                        errors.append(
                            f"{link_prefix} is not named by the linked premise"
                        )
                    else:
                        context_premise_links.add(
                            (
                                occurrence_id,
                                target,
                                linked_step_id,
                                linked_premise_id,
                            )
                        )
                        origin = linked_premise.get("origin")
                        origin_kind = (
                            origin.get("kind")
                            if isinstance(origin, dict)
                            else None
                        )
                        expected_origin = {
                            "internal_result": "internal_result",
                            "obligation_context": "obligation",
                            "local_step": "prior_step",
                        }.get(disposition_status)
                        if origin_kind != expected_origin:
                            errors.append(
                                f"{link_prefix} origin does not match "
                                f"{disposition_status}"
                            )
            if disposition_status == "internal_result":
                dependency_use_id = disposition.get("dependency_use_id")
                if not is_nonempty_string(dependency_use_id):
                    errors.append(
                        f"{prefix}.dependency_use_id is required"
                    )
                else:
                    linked_origins = {
                        origin.get("reference")
                        for link in premise_links
                        if isinstance(link, dict)
                        and isinstance(
                            (
                                origin := premise_records_by_step.get(
                                    link.get("step_id"), {}
                                ).get(link.get("premise_id"), {}).get("origin")
                            ),
                            dict,
                        )
                    }
                    if linked_origins != {dependency_use_id}:
                        errors.append(
                            f"{prefix}.dependency_use_id does not match linked "
                            "premise origins"
                        )
        elif final and premise_links not in (None, []):
            errors.append(
                f"{prefix}.premise_links are allowed only for premise-bearing roles"
            )
        if not is_substantive_string(disposition.get("evidence")):
            errors.append(
                f"{prefix}.evidence must be a nonempty string and substantive, "
                "not a reserved placeholder"
            )
        source_reference_dispositions.append(disposition)

    if final:
        recorded_source_premises = {
            (
                source_occurrence_id,
                source_reference_id,
                step_id,
                premise_id,
            )
            for step_id, premises in premise_records_by_step.items()
            for premise_id, premise in premises.items()
            if is_nonempty_string(
                source_reference_id := premise.get("source_reference_id")
            )
            and is_nonempty_string(
                source_occurrence_id := premise.get(
                    "source_reference_occurrence_id"
                )
            )
        }
        missing_source_links = sorted(
            recorded_source_premises - context_premise_links
        )
        if missing_source_links:
            errors.append(
                "Premises with source reference anchors lack an exact occurrence "
                "link: "
                + ", ".join(
                    f"{occurrence_id}:{target}@{step_id}/{premise_id}"
                    for occurrence_id, target, step_id, premise_id
                    in missing_source_links
                )
            )

    citation_dispositions: list[dict[str, Any]] = []
    citation_value = review.get("citation_dispositions")
    if not isinstance(citation_value, list):
        errors.append("review.citation_dispositions must be a list")
        citation_value = []
    seen_citations: set[str] = set()
    for index, disposition in enumerate(citation_value, 1):
        prefix = f"review.citation_dispositions[{index}]"
        if not isinstance(disposition, dict):
            errors.append(f"{prefix} must be an object")
            continue
        citation_key = disposition.get("key")
        if not is_nonempty_string(citation_key):
            errors.append(f"{prefix}.key must be a nonempty string")
            continue
        if citation_key in seen_citations:
            errors.append(f"Duplicate citation disposition: {citation_key}")
        seen_citations.add(citation_key)
        disposition_status = disposition.get("disposition")
        if not is_enum_value(disposition_status, {
            "external_result",
            "bibliographic_only",
            "unresolved",
        }):
            errors.append(f"{prefix}.disposition is invalid")
        if disposition_status == "external_result":
            if not is_nonempty_string(disposition.get("dependency_id")):
                errors.append(f"{prefix}.dependency_id is required")
            if not is_nonempty_string(disposition.get("dependency_use_id")):
                errors.append(f"{prefix}.dependency_use_id is required")
        if not is_substantive_string(disposition.get("evidence")):
            errors.append(
                f"{prefix}.evidence must be a nonempty string and substantive, "
                "not a reserved placeholder"
            )
        citation_dispositions.append(disposition)

    if final:
        result_use_ids = {
            claim["use_id"]
            for claim in result_dependency_claims
            if is_nonempty_string(claim.get("use_id"))
        }
        missing_direct = sorted(result_use_ids - seen_direct)
        if missing_direct:
            errors.append(
                "Step result dependencies missing from review.direct_dependencies: "
                + ", ".join(missing_direct)
            )
        unused_direct = sorted(seen_direct - result_use_ids)
        if unused_direct:
            errors.append(
                "review.direct_dependencies contains unused results: "
                + ", ".join(unused_direct)
            )

        direct_by_id = {
            dependency.get("use_id"): dependency
            for dependency in direct_dependencies
            if is_nonempty_string(dependency.get("use_id"))
        }
        for claim in result_dependency_claims:
            dependency_id = claim.get("id")
            use_id = claim.get("use_id")
            direct_dependency = direct_by_id.get(use_id)
            if direct_dependency is None:
                continue
            for dependency_field in (
                "id",
                "use_id",
                "kind",
                "conclusion_id",
                "status",
                "needed_form",
                "compatibility_check",
            ):
                if direct_dependency.get(dependency_field) != claim.get(
                    dependency_field
                ):
                    errors.append(
                        f"{claim.get('owner_step')}: dependency use {use_id} "
                        f"{dependency_field} differs from "
                        "review.direct_dependencies"
                    )

    for field in ("explicit_assumptions", "inherited_assumptions", "use_sites"):
        validate_string_list(
            review.get(field),
            f"review.{field}",
            errors,
            substantive=True,
            allow_empty=True,
        )
    review_use_sites = (
        review.get("use_sites") if isinstance(review.get("use_sites"), list) else []
    )
    if final and declared_status != "not_checked":
        validate_string_list(
            review.get("verification_basis"),
            "review.verification_basis",
            errors,
            substantive=True,
        )
        validate_string_list(
            review.get("reviewer_notes"),
            "review.reviewer_notes",
            errors,
            substantive=True,
            allow_empty=True,
        )

    contract_status = review.get("contract_fidelity")
    dependency_closure = review.get("dependency_closure")
    argument_status = review.get("argument_status")
    statement_status = review.get("statement_status")
    use_status = review.get("use_site_sufficiency")
    if not is_enum_value(contract_status, UNIT_STATUSES):
        errors.append("review.contract_fidelity is invalid or missing")
    if not is_enum_value(dependency_closure, UNIT_STATUSES):
        errors.append("review.dependency_closure is invalid or missing")
    if not is_enum_value(argument_status, ARGUMENT_STATUSES):
        errors.append("review.argument_status is invalid or missing")
    if not is_enum_value(statement_status, STATEMENT_STATUSES):
        errors.append("review.statement_status is invalid or missing")
    if not is_enum_value(use_status, USE_STATUSES):
        errors.append("review.use_site_sufficiency is invalid or missing")

    conclusions = (
        obligation.get("conclusions", [])
        if isinstance(obligation, dict)
        else []
    )
    conclusions_by_id = {
        record.get("id"): record
        for record in conclusions
        if isinstance(record, dict) and is_nonempty_string(record.get("id"))
    } if isinstance(conclusions, list) else {}
    steps_by_id = {
        step.get("id"): step
        for step in steps
        if isinstance(step, dict) and is_nonempty_string(step.get("id"))
    }
    direct_by_use = {
        dependency.get("use_id"): dependency
        for dependency in direct_dependencies
        if isinstance(dependency, dict)
        and is_nonempty_string(dependency.get("use_id"))
    }

    def support_closure(
        support_step_id: str, support_move_id: str
    ) -> dict[str, set[str]]:
        pending: list[tuple[str, str]] = [(support_step_id, support_move_id)]
        visited: set[tuple[str, str]] = set()
        dependency_uses: set[str] = set()
        obligation_pointers: set[str] = set()
        closure_issues: set[str] = set()

        def consume_premise(step_id: str, premise_id: str) -> None:
            premise = premise_records_by_step.get(step_id, {}).get(premise_id)
            if not isinstance(premise, dict):
                return
            origin = premise.get("origin")
            if not isinstance(origin, dict):
                return
            kind = origin.get("kind")
            reference = origin.get("reference")
            if kind == "obligation" and is_nonempty_string(reference):
                obligation_pointers.add(reference)
            elif is_enum_value(
                kind, {"internal_result", "external_result"}
            ) and is_nonempty_string(reference):
                dependency_uses.add(reference)
            elif kind == "prior_step" and is_nonempty_string(reference):
                prior_step = steps_by_id.get(reference)
                inference = (
                    prior_step.get("inference")
                    if isinstance(prior_step, dict)
                    else None
                )
                prior_move = (
                    inference.get("conclusion_move")
                    if isinstance(inference, dict)
                    else None
                )
                if is_nonempty_string(prior_move):
                    pending.append((reference, prior_move))

        while pending:
            step_id, move_id = pending.pop()
            key = (step_id, move_id)
            if key in visited:
                continue
            visited.add(key)
            step = steps_by_id.get(step_id)
            if not isinstance(step, dict):
                continue
            closure_issues.update(
                issue_id
                for issue_id in step.get("issue_ids", [])
                if is_nonempty_string(issue_id)
            )
            inference = step.get("inference")
            moves = inference.get("moves") if isinstance(inference, dict) else []
            move = next(
                (
                    row
                    for row in moves
                    if isinstance(row, dict) and row.get("id") == move_id
                ),
                None,
            ) if isinstance(moves, list) else None
            if not isinstance(move, dict):
                continue
            for prior_move_id in move.get("prior_move_ids", []):
                if is_nonempty_string(prior_move_id):
                    pending.append((step_id, prior_move_id))
            for premise_id in move.get("premise_ids", []):
                if is_nonempty_string(premise_id):
                    consume_premise(step_id, premise_id)
            side_conditions = step.get("side_conditions")
            if isinstance(side_conditions, list):
                for condition in side_conditions:
                    if (
                        not isinstance(condition, dict)
                        or condition.get("generated_by") != move_id
                        or condition.get("status") != "discharged"
                    ):
                        continue
                    discharge = condition.get("discharge")
                    sources = (
                        discharge.get("sources")
                        if isinstance(discharge, dict)
                        else []
                    )
                    if not isinstance(sources, list):
                        continue
                    for source in sources:
                        if not isinstance(source, dict):
                            continue
                        reference = source.get("reference")
                        if not is_nonempty_string(reference):
                            continue
                        if source.get("kind") == "premise":
                            consume_premise(step_id, reference)
                        elif source.get("kind") == "inference_move":
                            pending.append((step_id, reference))
        return {
            "dependency_uses": dependency_uses,
            "obligation_pointers": obligation_pointers,
            "issue_ids": closure_issues,
        }

    conclusion_results_value = review.get("conclusion_results")
    if not isinstance(conclusion_results_value, list):
        errors.append("review.conclusion_results must be an ordered list")
        conclusion_results_value = []
    seen_conclusion_results: set[str] = set()
    conclusion_result_records: list[dict[str, Any]] = []
    all_conclusion_dependency_uses: set[str] = set()
    for index, result in enumerate(conclusion_results_value, 1):
        prefix = f"review.conclusion_results[{index}]"
        if not isinstance(result, dict):
            errors.append(f"{prefix} must be an object")
            continue
        conclusion_id = result.get("conclusion_id")
        if conclusion_id not in conclusions_by_id:
            errors.append(f"{prefix}.conclusion_id is unknown")
            continue
        if conclusion_id in seen_conclusion_results:
            errors.append(f"duplicate conclusion result {conclusion_id}")
        seen_conclusion_results.add(conclusion_id)
        conclusion_result_records.append(result)
        support = result.get("support")
        if not isinstance(support, dict):
            errors.append(f"{prefix}.support must be an object")
            continue
        step_id = support.get("step_id")
        move_id = support.get("move_id")
        step = steps_by_id.get(step_id)
        inference = step.get("inference") if isinstance(step, dict) else None
        moves = inference.get("moves") if isinstance(inference, dict) else None
        matching_moves = [
            move
            for move in moves
            if isinstance(move, dict) and move.get("id") == move_id
        ] if isinstance(moves, list) else []
        if len(matching_moves) != 1:
            errors.append(
                f"{prefix}.support must name exactly one checked inference move"
            )
            continue
        move = matching_moves[0]
        step_status = step.get("status")
        result_statement_status = result.get("statement_status")
        if not is_enum_value(result_statement_status, STATEMENT_STATUSES):
            errors.append(f"{prefix}.statement_status is invalid")
        claim = conclusions_by_id[conclusion_id].get("claim")
        if (
            result_statement_status in {"established", "conditional"}
            and move.get("claim") != claim
        ):
            errors.append(
                f"{prefix} support move must exactly match conclusion {conclusion_id}"
            )
        if result_statement_status == "refuted":
            failure = move.get("failure")
            if (
                not isinstance(failure, dict)
                or failure.get("kind") not in REFUTATION_FAILURE_KINDS
            ):
                errors.append(
                    f"{prefix}: a refuted conclusion requires a counterexample "
                    "or contradiction"
                )
            elif failure.get("target") != claim:
                errors.append(
                    f"{prefix}: refutation target must exactly match {conclusion_id}"
                )
        statement_to_step_statuses = {
            "established": {"verified"},
            "conditional": {"conditionally_verified"},
            "refuted": {"incorrect"},
            "not_established": {"gap", "incorrect"},
            "unclear": {"unclear"},
            "not_assessed": {"not_checked"},
        }
        allowed_step_statuses = (
            statement_to_step_statuses.get(result_statement_status, set())
            if isinstance(result_statement_status, str)
            else set()
        )
        if not is_enum_value(step_status, allowed_step_statuses):
            errors.append(
                f"{prefix}.statement_status is inconsistent with support step "
                f"status {step_status!r}"
            )
        result_contract = result.get("contract_fidelity")
        result_argument = result.get("argument_status")
        result_closure = result.get("dependency_closure")
        result_use_status = result.get("use_site_sufficiency")
        if not is_enum_value(result_contract, UNIT_STATUSES):
            errors.append(f"{prefix}.contract_fidelity is invalid")
        if not is_enum_value(result_argument, ARGUMENT_STATUSES):
            errors.append(f"{prefix}.argument_status is invalid")
        if not is_enum_value(result_closure, UNIT_STATUSES):
            errors.append(f"{prefix}.dependency_closure is invalid")
        if not is_enum_value(result_use_status, USE_STATUSES):
            errors.append(f"{prefix}.use_site_sufficiency is invalid")
        step_to_argument = {
            "verified": "valid",
            "conditionally_verified": "conditional",
            "gap": "gap",
            "incorrect": "invalid",
            "unclear": "unclear",
            "not_checked": "not_checked",
        }
        expected_result_argument = (
            step_to_argument.get(step_status)
            if isinstance(step_status, str)
            else None
        )
        if final and result_argument != expected_result_argument:
            errors.append(
                f"{prefix}.argument_status must match its support-step evidence"
            )
        if (
            final
            and result_statement_status in {"established", "refuted"}
            and result_contract != "verified"
        ):
            errors.append(
                f"{prefix}: {result_statement_status} requires verified "
                "contract fidelity"
            )
        closure = support_closure(str(step_id), str(move_id))
        dependency_use_ids = validate_string_list(
            result.get("dependency_use_ids"),
            f"{prefix}.dependency_use_ids",
            errors,
            allow_empty=True,
        )
        if len(dependency_use_ids) != len(set(dependency_use_ids)):
            errors.append(f"{prefix}.dependency_use_ids contains duplicates")
        if set(dependency_use_ids) != closure["dependency_uses"]:
            errors.append(
                f"{prefix}.dependency_use_ids do not match the support closure"
            )
        unknown_uses = set(dependency_use_ids) - set(direct_by_use)
        if unknown_uses:
            errors.append(
                f"{prefix}.dependency_use_ids name unknown uses: "
                + ", ".join(sorted(unknown_uses))
            )
        all_conclusion_dependency_uses.update(dependency_use_ids)
        dependency_state = combine_dependency_statuses(
            direct_by_use[use_id].get("status")
            for use_id in dependency_use_ids
            if use_id in direct_by_use
        )
        expected_result_closure = {
            "verified": "verified",
            "conditional": "conditionally_verified",
            "gap": "gap",
            "incorrect": "incorrect",
            "unclear": "unclear",
            "unchecked": "not_checked",
        }[dependency_state]
        if final and result_closure != expected_result_closure:
            errors.append(
                f"{prefix}.dependency_closure must match its exact dependency uses"
            )
        allowed_pointers = set(
            conclusions_by_id[conclusion_id].get("applies_under", [])
        )
        leaked_pointers = closure["obligation_pointers"] - allowed_pointers
        if leaked_pointers:
            errors.append(
                f"{prefix}: support closure uses assumptions outside "
                f"{conclusion_id}.applies_under: "
                + ", ".join(sorted(leaked_pointers))
            )
        result_issues = set(
            validate_issue_id_list(
                result.get("issue_ids"), f"{prefix}.issue_ids", errors
            )
        )
        if not closure["issue_ids"].issubset(result_issues):
            errors.append(
                f"{prefix}.issue_ids omit issues in the support closure"
            )

    missing_conclusion_results = set(conclusions_by_id) - seen_conclusion_results
    extra_conclusion_results = seen_conclusion_results - set(conclusions_by_id)
    if final and missing_conclusion_results:
        errors.append(
            "review.conclusion_results omits conclusions: "
            + ", ".join(sorted(missing_conclusion_results))
        )
    if extra_conclusion_results:
        errors.append(
            "review.conclusion_results contains unknown conclusions: "
            + ", ".join(sorted(extra_conclusion_results))
        )
    if final and all_conclusion_dependency_uses != set(direct_by_use):
        errors.append(
            "Every direct dependency use must belong to at least one conclusion "
            "support closure"
        )

    conclusion_step_id = review.get("conclusion_step_id")
    if len(conclusion_result_records) == 1:
        support = conclusion_result_records[0].get("support")
        support_step_id = (
            support.get("step_id") if isinstance(support, dict) else None
        )
        if final and conclusion_step_id != support_step_id:
            errors.append(
                "For one conclusion, review.conclusion_step_id must equal its "
                "support step"
            )
    elif final and is_nonempty_string(conclusion_step_id):
        errors.append(
            "review.conclusion_step_id must be empty for a multi-conclusion result"
        )

    statement_rank = {
        "established": 0,
        "conditional": 1,
        "not_assessed": 2,
        "unclear": 3,
        "not_established": 4,
        "refuted": 5,
    }
    result_statement_values = [
        result.get("statement_status")
        for result in conclusion_result_records
        if is_enum_value(result.get("statement_status"), STATEMENT_STATUSES)
    ]
    if final and result_statement_values:
        expected_statement_status = max(
            result_statement_values, key=lambda value: statement_rank[value]
        )
        if statement_status != expected_statement_status:
            errors.append(
                "review.statement_status must be the weakest conclusion judgment"
            )
    unresolved_normalization = {
        aspect
        for aspect, normalization_status in normalization_statuses.items()
        if not is_enum_value(normalization_status, {"checked", "not_applicable"})
    }
    if (
        final
        and is_enum_value(contract_status, {"verified", "conditionally_verified"})
        and unresolved_normalization
    ):
        errors.append(
            f"{contract_status} contract fidelity has unresolved "
            "normalization checks: "
            + ", ".join(sorted(unresolved_normalization))
        )
    if final:
        if contract_status == "not_checked":
            errors.append("Final ledger requires a contract-fidelity judgment")
        if dependency_closure == "not_checked":
            errors.append("Final ledger requires a dependency-closure judgment")
        if statement_status == "not_assessed":
            errors.append("Final ledger requires a separate statement-status judgment")
        if use_status == "not_checked":
            errors.append("Final ledger requires a use-site-sufficiency judgment")

    if (
        final
        and is_enum_value(statement_status, {"established", "refuted"})
        and contract_status != "verified"
    ):
        errors.append(
            f"review.statement_status {statement_status} requires verified "
            "contract fidelity"
        )
    if (
        final
        and statement_status == "conditional"
        and not is_enum_value(
            contract_status, {"verified", "conditionally_verified"}
        )
    ):
        errors.append(
            "review.statement_status conditional requires verified or "
            "conditionally_verified contract fidelity"
        )

    expected_argument = {
        "verified": "valid",
        "conditionally_verified": "conditional",
        "gap": "gap",
        "incorrect": "invalid",
        "unclear": "unclear",
        "not_checked": "not_checked",
    }[expected_status]
    if final and argument_status != expected_argument:
        errors.append(
            f"review.argument_status {argument_status!r} does not match "
            f"the step evidence ({expected_argument!r})"
        )
    if final and declared_status == "verified":
        if contract_status != "verified":
            errors.append("verified unit requires verified contract fidelity")
        if dependency_closure != "verified":
            errors.append("verified unit requires verified dependency closure")
        if statement_status != "established":
            errors.append("verified unit requires statement_status established")
        invalid_direct = [
            record.get("status")
            for record in direct_dependencies
            if not is_enum_value(record.get("status"), {"verified", "not_applicable"})
        ]
        if invalid_direct:
            errors.append("verified unit has nonverified direct dependencies")
    if final and declared_status == "conditionally_verified":
        if not is_enum_value(contract_status, {"verified", "conditionally_verified"}):
            errors.append("conditional unit has failed or unchecked contract fidelity")
        if not is_enum_value(dependency_closure, {"verified", "conditionally_verified"}):
            errors.append("conditional unit has failed or unchecked dependency closure")
        if not is_enum_value(statement_status, {"established", "conditional"}):
            errors.append("conditional unit needs established or conditional statement status")
        failed_direct = [
            record.get("status")
            for record in direct_dependencies
            if is_enum_value(record.get("status"), {"gap", "incorrect", "unclear"})
        ]
        if failed_direct:
            errors.append("conditional unit cannot hide failed direct dependencies")

    independent_check = validate_independent_check(
        ledger.get("independent_check"), final, errors
    )
    if independent_check and not independent_check.get("required"):
        if independent_check.get("status") != "not_required":
            errors.append("non-required independent check must have status not_required")
    if (
        final
        and independent_check.get("required")
        and independent_check.get("status") == "agreed"
        and independent_check.get("challenger_verdict") != declared_status
    ):
        errors.append(
            "independent_check marked agreed but challenger_verdict differs from unit_status"
        )
    if (
        final
        and independent_check.get("required")
        and is_enum_value(independent_check.get("status"), {"agreed", "resolved"})
        and independent_check.get("reconciled_verdict") != declared_status
    ):
        errors.append(
            "independent_check.reconciled_verdict differs from the final unit_status"
        )

    summary = {
        "ledger": str(ledger_path),
        "unit_id": unit_id,
        "evidence_contract_version": evidence_contract_version,
        "validation_mode": "final" if final else "draft",
        "validation_scope": {
            "local_record_integrity": (
                "failed" if errors else ("passed" if final else "inspection_only")
            ),
            "audit_wide_dependency_resolution": (
                "not_performed; run finalize on the audit root"
            ),
        },
        "source_file": str(source),
        "source_start": start,
        "source_end": end,
        "source_range": f"{start}-{end}",
        "coverage_mode": coverage_mode,
        "physical_lines": max(0, end - start + 1),
        "steps": len(steps),
        "step_ids": [
            step.get("id")
            for step in steps
            if isinstance(step, dict)
            and isinstance(step.get("id"), str)
            and STEP_ID_RE.fullmatch(step["id"])
        ],
        "obligation_sha256": (
            canonical_sha256(obligation) if isinstance(obligation, dict) else None
        ),
        "obligation_conclusion": (
            obligation.get("conclusion") if isinstance(obligation, dict) else None
        ),
        "obligation_conclusions": (
            [
                {
                    **record,
                    "contract_sha256": canonical_sha256(
                        conclusion_contract_payload(obligation, record["id"])
                    ),
                }
                for record in obligation.get("conclusions", [])
                if isinstance(record, dict)
                and is_nonempty_string(record.get("id"))
                and conclusion_contract_payload(obligation, record["id"])
                is not None
            ]
            if isinstance(obligation, dict)
            and isinstance(obligation.get("conclusions"), list)
            else []
        ),
        "obligation_normalization": (
            obligation.get("normalization_checks")
            if isinstance(obligation, dict)
            else None
        ),
        "expected_unit_status": expected_status,
        "declared_unit_status": declared_status,
        "issue_references": sorted(issue_references),
        "issue_links": issue_links,
        "direct_dependencies": direct_dependencies,
        "source_reference_dispositions": source_reference_dispositions,
        "citation_dispositions": citation_dispositions,
        "use_sites": review_use_sites,
        "result_dependency_claims": result_dependency_claims,
        "conclusion_results": conclusion_result_records,
        "review_components": {
            "contract_fidelity": contract_status,
            "argument_status": argument_status,
            "statement_status": statement_status,
            "dependency_closure": dependency_closure,
            "use_site_sufficiency": use_status,
        },
        "obligation_statement_spans": obligation_statement_spans,
        "obligation_context_spans": obligation_context_spans,
        "independent_check": independent_check,
        "errors": len(errors),
    }
    return errors, summary


def cmd_ledger_check(args: argparse.Namespace) -> int:
    ledger_path = args.ledger.resolve()
    errors, summary = check_ledger_data(ledger_path, args.final)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    return 0


def load_issue_log(root: Path) -> tuple[Path, list[dict[str, Any]], list[str]]:
    path = root / "audit" / "06_reports" / "ISSUE_LOG.json"
    errors: list[str] = []
    if not path.is_file():
        return path, [], [f"Canonical issue log not found: {path}"]
    try:
        data = json.loads(read_text(path))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return path, [], [f"Cannot read issue log: {exc}"]
    issues = data.get("issues") if isinstance(data, dict) else None
    if isinstance(data, dict) and data.get("schema_version") != SCHEMA_VERSION:
        errors.append(
            f"ISSUE_LOG.json schema_version must be {SCHEMA_VERSION}"
        )
    if not isinstance(issues, list):
        return path, [], ["ISSUE_LOG.json must contain an issues list"]
    return path, issues, errors


def validate_issues(
    issues: list[dict[str, Any]],
    referenced: set[str],
    final: bool = False,
    *,
    evidence_base: Path | None = None,
    interfaces: dict[str, dict[str, Any]] | None = None,
    source_snapshot_id: str | None = None,
    in_scope: Iterable[str] | None = None,
    reverse_graph: dict[str, set[str]] | None = None,
) -> tuple[list[str], Counter[str]]:
    errors: list[str] = []
    seen: set[str] = set()
    counts: Counter[str] = Counter()
    for index, issue in enumerate(issues, 1):
        prefix = f"Issue record {index}"
        if not isinstance(issue, dict):
            errors.append(f"{prefix} must be an object")
            continue
        issue_id = issue.get("id")
        if not isinstance(issue_id, str) or not ISSUE_ID_RE.fullmatch(issue_id):
            errors.append(f"{prefix} has invalid id; expected I-001")
            continue
        if issue_id in seen:
            errors.append(f"Duplicate issue id: {issue_id}")
        seen.add(issue_id)
        severity = issue.get("severity")
        confidence = issue.get("confidence")
        status = issue.get("status")
        finding_status = issue.get("finding_status")
        if not is_enum_value(severity, ISSUE_SEVERITIES):
            errors.append(f"{issue_id}: invalid severity {severity!r}")
        else:
            counts[f"severity_{severity}"] += 1
        if not is_enum_value(confidence, ISSUE_CONFIDENCES):
            errors.append(f"{issue_id}: invalid confidence {confidence!r}")
        if not is_enum_value(status, ISSUE_STATUSES):
            errors.append(f"{issue_id}: invalid status {status!r}")
        else:
            counts[f"status_{status}"] += 1
        if not is_enum_value(finding_status, ISSUE_FINDING_STATUSES):
            errors.append(f"{issue_id}: invalid finding_status {finding_status!r}")
        elif status == "resolved" and finding_status != "resolved":
            errors.append(f"{issue_id}: resolved lifecycle status requires finding_status resolved")
        elif is_enum_value(status, {"open", "deferred"}) and finding_status == "resolved":
            errors.append(f"{issue_id}: an open or deferred issue cannot have finding_status resolved")
        for field in ("location", "affected_result", "summary"):
            if not is_substantive_string(issue.get(field)):
                errors.append(f"{issue_id}: {field} must be nonempty and substantive")
        validate_string_list(
            issue.get("evidence"),
            f"{issue_id}.evidence",
            errors,
            substantive=True,
        )
        affected_result = issue.get("affected_result")
        scope_ids = set(in_scope) if in_scope is not None else None
        if scope_ids is not None and (
            not is_nonempty_string(affected_result) or affected_result not in scope_ids
        ):
            errors.append(f"{issue_id}: affected_result is outside the audited scope")
        affected_results = validate_string_list(
            issue.get("affected_results"),
            f"{issue_id}.affected_results",
            errors,
            allow_empty=False,
        )
        if len(affected_results) != len(set(affected_results)):
            errors.append(f"{issue_id}.affected_results contains duplicates")
        if scope_ids is not None:
            unknown_results = set(affected_results) - scope_ids
            if unknown_results:
                errors.append(
                    f"{issue_id}.affected_results names results outside scope: "
                    + ", ".join(sorted(unknown_results))
                )
        if reverse_graph is not None and is_nonempty_string(affected_result):
            expected_affected = {affected_result}
            if issue.get("load_bearing") is True:
                frontier = [affected_result]
                while frontier:
                    current = frontier.pop()
                    for dependent in reverse_graph.get(current, set()):
                        if dependent not in expected_affected:
                            expected_affected.add(dependent)
                            frontier.append(dependent)
            if affected_results != sorted(expected_affected):
                errors.append(
                    f"{issue_id}.affected_results must equal the reverse dependency closure: "
                    + ", ".join(sorted(expected_affected))
                )
        scope = issue.get("scope")
        if not is_enum_value(scope, {"unit", "global"}):
            errors.append(f"{issue_id}: scope must be unit or global")
        if scope == "unit" and issue_id not in referenced:
            errors.append(f"{issue_id}: unit issue is not referenced by any ledger step")

        interface_id = issue.get("interface_id")
        if interface_id is not None:
            if not isinstance(interface_id, str) or not INTERFACE_ID_RE.fullmatch(
                interface_id
            ):
                errors.append(f"{issue_id}: interface_id must match MI-001")
                interface = None
            else:
                interface = interfaces.get(interface_id) if interfaces is not None else None
                if interfaces is not None and interface is None:
                    errors.append(f"{issue_id}: unknown method interface {interface_id}")
            finding_class = issue.get("finding_class")
            affected_layer = issue.get("affected_layer")
            evidence_class = issue.get("evidence_class")
            estimator_target_status = issue.get("estimator_target_status")
            inspection_status = issue.get("implementation_inspection_status")
            code_to_documented = issue.get("code_to_documented_estimator")
            code_to_target = issue.get("code_to_required_target")
            provenance_status = issue.get("execution_provenance_status")
            if not is_enum_value(finding_class, INTERFACE_FINDING_CLASSES):
                errors.append(f"{issue_id}: invalid interface finding_class")
            if not is_enum_value(affected_layer, INTERFACE_AFFECTED_LAYERS):
                errors.append(f"{issue_id}: invalid affected_layer")
            if not is_enum_value(
                evidence_class, {"observed", "inferred", "not_established"}
            ):
                errors.append(f"{issue_id}: invalid evidence_class")
            if not is_enum_value(estimator_target_status, TARGET_RELATION_VERDICTS):
                errors.append(f"{issue_id}: invalid estimator_target_status")
            if not is_enum_value(inspection_status, IMPLEMENTATION_INSPECTION_STATUSES):
                errors.append(f"{issue_id}: invalid implementation_inspection_status")
            if not is_enum_value(code_to_documented, IMPLEMENTATION_COMPARISON_VERDICTS):
                errors.append(f"{issue_id}: invalid code_to_documented_estimator")
            if not is_enum_value(code_to_target, IMPLEMENTATION_COMPARISON_VERDICTS):
                errors.append(f"{issue_id}: invalid code_to_required_target")
            if not is_enum_value(provenance_status, EXECUTION_PROVENANCE_STATUSES):
                errors.append(f"{issue_id}: invalid execution_provenance_status")
            validate_string_list(
                issue.get("resolution_evidence_needed"),
                f"{issue_id}.resolution_evidence_needed",
                errors,
            )
            if interface is not None:
                target_relation = interface.get("target_relation")
                canonical_target = (
                    target_relation.get("verdict")
                    if isinstance(target_relation, dict)
                    else None
                )
                implementation_relation = interface.get("implementation_relation")
                canonical_inspection = None
                canonical_code_to_documented = None
                canonical_code_to_target = None
                canonical_provenance = None
                if isinstance(implementation_relation, dict):
                    canonical_inspection = implementation_relation.get(
                        "inspection_status"
                    )
                    comparisons = implementation_relation.get("comparisons")
                    if isinstance(comparisons, list):
                        comparison_verdicts = {
                            comparison.get("to"): comparison.get("verdict")
                            for comparison in comparisons
                            if isinstance(comparison, dict)
                        }
                        canonical_code_to_documented = comparison_verdicts.get(
                            "documented_estimator"
                        )
                        canonical_code_to_target = comparison_verdicts.get(
                            "required_target"
                        )
                    provenance = implementation_relation.get("execution_provenance")
                    if isinstance(provenance, dict):
                        canonical_provenance = provenance.get("status")
                if estimator_target_status != canonical_target:
                    errors.append(
                        f"{issue_id}: estimator_target_status disagrees with {interface_id}"
                    )
                if inspection_status != canonical_inspection:
                    errors.append(
                        f"{issue_id}: implementation_inspection_status disagrees with {interface_id}"
                    )
                if code_to_documented != canonical_code_to_documented:
                    errors.append(
                        f"{issue_id}: code_to_documented_estimator disagrees with {interface_id}"
                    )
                if code_to_target != canonical_code_to_target:
                    errors.append(
                        f"{issue_id}: code_to_required_target disagrees with {interface_id}"
                    )
                if provenance_status != canonical_provenance:
                    errors.append(
                        f"{issue_id}: execution_provenance_status disagrees with {interface_id}"
                    )
                interface_issue_ids = interface.get("issue_ids")
                if isinstance(interface_issue_ids, list) and issue_id not in interface_issue_ids:
                    errors.append(f"{issue_id}: not linked back from {interface_id}.issue_ids")
                specification = interface.get("interface_specification_status")
                if issue.get("load_bearing") is True and interface.get("load_bearing") is not True:
                    errors.append(
                        f"{issue_id}: a load-bearing issue requires a load-bearing interface"
                    )
                if finding_class == "exposition_ambiguity":
                    if (
                        status != "resolved"
                        and not is_enum_value(
                            specification, {"ambiguous", "incomplete"}
                        )
                    ):
                        errors.append(
                            f"{issue_id}: exposition_ambiguity requires an ambiguous or incomplete specification"
                        )
                    if canonical_target == "mismatch":
                        errors.append(
                            f"{issue_id}: exposition ambiguity cannot be reported as a target mismatch"
                        )
                if finding_class == "estimator_target_mismatch" and canonical_target != "mismatch":
                    errors.append(
                        f"{issue_id}: estimator_target_mismatch requires an established target mismatch"
                    )
                if (
                    finding_class == "implementation_mismatch"
                    and canonical_code_to_documented != "inconsistent"
                ):
                    errors.append(
                        f"{issue_id}: implementation_mismatch requires code-to-documentation inconsistency"
                    )
                if (
                    finding_class == "implementation_mismatch"
                    and issue.get("load_bearing") is True
                    and interface.get("implementation_required_for_claim") is not True
                ):
                    errors.append(
                        f"{issue_id}: a load-bearing implementation mismatch must be required for the claim"
                    )
                if finding_class == "scope_boundary" and not is_enum_value(
                    canonical_inspection,
                    {"available_not_checked", "unavailable", "out_of_scope"},
                ):
                    errors.append(
                        f"{issue_id}: scope_boundary requires an uninspected implementation status"
                    )
                if (
                    finding_class == "reproducibility_gap"
                    and canonical_provenance == "matched"
                ):
                    errors.append(
                        f"{issue_id}: reproducibility_gap conflicts with matched execution provenance"
                    )
                if (
                    finding_class == "reproducibility_gap"
                    and issue.get("load_bearing") is True
                    and interface.get("execution_provenance_required_for_claim") is not True
                ):
                    errors.append(
                        f"{issue_id}: a load-bearing reproducibility gap must be required for the claim"
                    )

        if final and not isinstance(issue.get("load_bearing"), bool):
            errors.append(f"{issue_id}: load_bearing must be true or false")
        if final and is_enum_value(severity, {"S0", "S1"}) and issue.get("load_bearing") is not True:
            errors.append(f"{issue_id}: S0 and S1 issues must be load-bearing")
        if final:
            validate_string_list(
                issue.get("downstream_consequences"),
                f"{issue_id}.downstream_consequences",
                errors,
                substantive=True,
            )
            if not is_substantive_string(issue.get("possible_repair")):
                errors.append(
                    f"{issue_id}: possible_repair must be explicit and substantive"
                )
        if status == "resolved" and final:
            if not is_substantive_string(issue.get("resolution")):
                errors.append(f"{issue_id}: resolved issue needs a substantive resolution")
            if not is_substantive_string(issue.get("source_revision")):
                errors.append(f"{issue_id}: resolved issue needs a substantive source_revision")
            validate_string_list(
                issue.get("recheck_evidence"),
                f"{issue_id}.recheck_evidence",
                errors,
                substantive=True,
            )
            if issue.get("source_snapshot_sha256") != source_snapshot_id:
                errors.append(
                    f"{issue_id}: resolved issue source_snapshot_sha256 is stale"
                )
            rechecked_units = validate_string_list(
                issue.get("rechecked_units"),
                f"{issue_id}.rechecked_units",
                errors,
            )
            if rechecked_units != sorted(affected_results):
                errors.append(
                    f"{issue_id}.rechecked_units must equal affected_results exactly"
                )
            if interface_id is not None:
                contract = issue.get("semantic_contract")
                if not isinstance(contract, dict):
                    errors.append(
                        f"{issue_id}: resolved interface issue needs a semantic_contract"
                    )
                else:
                    if not is_nonempty_string(contract.get("protected_meaning")):
                        errors.append(
                            f"{issue_id}.semantic_contract.protected_meaning must be explicit"
                        )
                    validate_string_list(
                        contract.get("dependent_claims"),
                        f"{issue_id}.semantic_contract.dependent_claims",
                        errors,
                    )
                    validate_string_list(
                        contract.get("reopen_if"),
                        f"{issue_id}.semantic_contract.reopen_if",
                        errors,
                    )
                    if not is_nonempty_string(contract.get("regression_check")):
                        errors.append(
                            f"{issue_id}.semantic_contract.regression_check must be explicit"
                        )
                    contract_snapshot = contract.get("source_snapshot_sha256")
                    if not is_nonempty_string(contract_snapshot):
                        errors.append(
                            f"{issue_id}.semantic_contract.source_snapshot_sha256 must be explicit"
                        )
                    elif (
                        source_snapshot_id is not None
                        and contract_snapshot != source_snapshot_id
                    ):
                        errors.append(
                            f"{issue_id}: semantic contract refers to a stale source snapshot"
                        )
                    spans = contract.get("supporting_spans")
                    if evidence_base is None:
                        errors.append(
                            f"{issue_id}: cannot verify semantic_contract supporting spans"
                        )
                    else:
                        validated_spans = validate_locked_span_list(
                            spans,
                            evidence_base,
                            f"{issue_id}.semantic_contract.supporting_spans",
                            errors,
                        )
                        allowed_roles = {
                            "authoritative_definition",
                            "authoritative_algorithm",
                            "authoritative_configuration",
                        }
                        for span in validated_spans:
                            if span.get("role") not in allowed_roles:
                                errors.append(
                                    f"{issue_id}: semantic support must be an authoritative span"
                                )

    for issue_id in sorted(referenced - seen):
        errors.append(f"Ledger references undefined issue: {issue_id}")
    counts["total"] = len(issues)
    return errors, counts


def render_issue_summary(issues: list[dict[str, Any]]) -> str:
    severity_counts = Counter(
        issue.get("severity")
        for issue in issues
        if isinstance(issue, dict)
        and is_enum_value(issue.get("severity"), ISSUE_SEVERITIES)
    )
    status_counts = Counter(
        issue.get("status")
        for issue in issues
        if isinstance(issue, dict)
        and is_enum_value(issue.get("status"), ISSUE_STATUSES)
    )
    finding_counts = Counter(
        issue.get("finding_status")
        for issue in issues
        if isinstance(issue, dict)
        and is_enum_value(issue.get("finding_status"), ISSUE_FINDING_STATUSES)
    )
    rows = [
        "# Canonical Issue Summary",
        "",
        "This file is generated from `ISSUE_LOG.json`. Do not edit counts here.",
        "",
        "## Counts",
        "",
        "| Metric | Count |",
        "|---|---|",
        f"| Total | {len(issues)} |",
    ]
    rows.extend(f"| {level} | {severity_counts[level]} |" for level in sorted(ISSUE_SEVERITIES))
    rows.extend(f"| {status} | {status_counts[status]} |" for status in sorted(ISSUE_STATUSES))
    rows.extend(
        f"| finding_{status} | {finding_counts[status]} |"
        for status in sorted(ISSUE_FINDING_STATUSES)
    )
    rows.extend(
        [
            "",
            "## Issues",
            "",
            "| ID | Severity | Confidence | Status | Finding status | Load-bearing | Finding class | Affected layer | Interface | Estimator target | Implementation inspection | Code to documented estimator | Code to required target | Execution provenance | Affected result | Affected results | Summary |",
            "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|",
        ]
    )
    if not issues:
        rows.append(
            "| None | None | None | None | None | None | None | None | None | None | None | None | None | None | None | None | No issues recorded |"
        )
    else:
        for issue in sorted(
            (item for item in issues if isinstance(item, dict)),
            key=lambda item: str(item.get("id", "")),
        ):
            values = canonical_issue_row(issue)
            rows.append(
                "| "
                + " | ".join(
                    escape_markdown(value) for value in values
                )
                + " |"
            )
    rows.append("")
    return "\n".join(rows)


def audit_ledgers(root: Path, final: bool) -> tuple[list[str], list[dict[str, Any]], set[str]]:
    errors: list[str] = []
    summaries: list[dict[str, Any]] = []
    referenced: set[str] = set()
    for ledger_path in sorted(root.rglob("*.ledger.json")):
        ledger_errors, summary = check_ledger_data(ledger_path, final)
        summaries.append(summary)
        referenced.update(summary.get("issue_references", []))
        errors.extend(f"{ledger_path}: {error}" for error in ledger_errors)
    return errors, summaries, referenced


def cmd_issues(args: argparse.Namespace) -> int:
    root = args.root.resolve()
    errors, summaries, referenced = audit_ledgers(root, args.final)
    if args.final and not summaries:
        errors.append("Final issue reconciliation requires at least one ledger")
    issue_path, issues, issue_read_errors = load_issue_log(root)
    errors.extend(issue_read_errors)
    manifest, manifest_errors = load_json_object(root / "AUDIT_MANIFEST.json", "audit manifest")
    errors.extend(manifest_errors)
    interfaces: dict[str, dict[str, Any]] | None = None
    source_snapshot_id: str | None = None
    if not manifest_errors:
        source_snapshot = manifest.get("source_snapshot")
        if isinstance(source_snapshot, dict) and is_nonempty_string(
            source_snapshot.get("sha256")
        ):
            source_snapshot_id = source_snapshot["sha256"]
        registry_value = manifest.get("method_interface_registry")
        if is_nonempty_string(registry_value):
            registry_path = resolve_stored_path(registry_value, root)
            registry, registry_errors = load_json_object(
                registry_path, "method-interface registry"
            )
            errors.extend(registry_errors)
            if not registry_errors:
                interfaces = validate_method_interface_registry(
                    registry, root, errors, final=args.final
                )
    issue_errors, counts = validate_issues(
        issues,
        referenced,
        args.final,
        evidence_base=root,
        interfaces=interfaces,
        source_snapshot_id=source_snapshot_id,
    )
    errors.extend(issue_errors)

    if args.write_summary and not issue_read_errors:
        summary_path = root / "audit" / "06_reports" / "ISSUE_SUMMARY.md"
        summary_path.write_text(
            render_issue_summary(issues), encoding="utf-8", newline="\n"
        )

    result = {
        "audit_root": str(root),
        "issue_log": str(issue_path),
        "ledgers": len(summaries),
        "ledger_issue_references": len(referenced),
        "issue_counts": dict(counts),
        "errors": len(errors),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    return 0


def combine_dependency_statuses(statuses: Iterable[str]) -> str:
    """Combine source and applicability states using the strongest limitation."""
    values = {status for status in statuses if isinstance(status, str)}
    for status in ("incorrect", "gap", "unclear", "unchecked", "conditional"):
        if status in values:
            return status
    return "verified"


def internal_dependency_status(
    summary: dict[str, Any], conclusion_id: str
) -> str:
    """Derive availability for one audited conclusion."""
    result = next(
        (
            row
            for row in summary.get("conclusion_results", [])
            if isinstance(row, dict)
            and row.get("conclusion_id") == conclusion_id
        ),
        None,
    )
    if not isinstance(result, dict):
        return "unchecked"
    statement_status = result.get("statement_status")
    if is_enum_value(statement_status, {"established", "conditional"}):
        contract_value = result.get("contract_fidelity")
        argument_value = result.get("argument_status")
        closure_value = result.get("dependency_closure")
        component_statuses = [
            {
                "verified": "verified",
                "conditionally_verified": "conditional",
                "gap": "gap",
                "incorrect": "incorrect",
                "unclear": "unclear",
                "not_checked": "unchecked",
            }.get(contract_value, "unchecked")
            if isinstance(contract_value, str)
            else "unchecked",
            {
                "valid": "verified",
                "conditional": "conditional",
                "gap": "gap",
                "invalid": "gap",
                "unclear": "unclear",
                "not_checked": "unchecked",
            }.get(argument_value, "unchecked")
            if isinstance(argument_value, str)
            else "unchecked",
            {
                "verified": "verified",
                "conditionally_verified": "conditional",
                "gap": "gap",
                "incorrect": "incorrect",
                "unclear": "unclear",
                "not_checked": "unchecked",
            }.get(closure_value, "unchecked")
            if isinstance(closure_value, str)
            else "unchecked",
        ]
        if statement_status == "conditional":
            component_statuses.append("conditional")
        return combine_dependency_statuses(component_statuses)
    return ({
        "refuted": "incorrect",
        "not_established": "gap",
        "unclear": "unclear",
        "not_assessed": "unchecked",
    }.get(statement_status, "unchecked")
    if isinstance(statement_status, str)
    else "unchecked")


def validate_issue_id_list(
    value: Any,
    field: str,
    errors: list[str],
    *,
    allow_empty: bool = True,
) -> list[str]:
    issue_ids = validate_string_list(
        value,
        field,
        errors,
        allow_empty=allow_empty,
    )
    if len(issue_ids) != len(set(issue_ids)):
        errors.append(f"{field} contains duplicates")
    for issue_id in issue_ids:
        if not ISSUE_ID_RE.fullmatch(issue_id):
            errors.append(f"{field} contains invalid issue id {issue_id!r}")
    return issue_ids


def validate_compatibility_matrix(
    value: Any,
    field: str,
    errors: list[str],
) -> tuple[str, set[str]]:
    statuses = validate_aspect_matrix(
        value,
        field,
        NORMALIZATION_ASPECTS,
        COMPATIBILITY_STATUSES,
        True,
        errors,
    )
    issue_ids: set[str] = set()
    if isinstance(value, list):
        for index, row in enumerate(value, 1):
            if not isinstance(row, dict):
                continue
            prefix = f"{field}[{index}]"
            row_issues = validate_issue_id_list(
                row.get("issue_ids"),
                f"{prefix}.issue_ids",
                errors,
            )
            status = row.get("status")
            if is_enum_value(status, {"passed", "not_applicable"}) and row_issues:
                errors.append(f"{prefix}: a clean compatibility row cannot cite issues")
            if is_enum_value(status, {
                "conditional",
                "gap",
                "incorrect",
                "unclear",
                "unchecked",
            }) and not row_issues:
                errors.append(f"{prefix}: a non-clean compatibility row requires issue_ids")
            issue_ids.update(row_issues)
    nonclean = [
        status
        for status in statuses.values()
        if isinstance(status, str) and status not in {"passed", "not_applicable"}
    ]
    applicability = combine_dependency_statuses(nonclean) if nonclean else "passed"
    return applicability, issue_ids


def validate_locked_span_list(
    value: Any,
    base: Path,
    field: str,
    errors: list[str],
    *,
    allow_empty: bool = False,
) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        errors.append(f"{field} must be a list")
        return []
    if not allow_empty and not value:
        errors.append(f"{field} must not be empty")
    for index, span in enumerate(value, 1):
        validate_locked_span(
            span,
            base,
            f"{field}[{index}]",
            errors,
            require_role=True,
        )
    return [span for span in value if isinstance(span, dict)]


def validate_method_interface_registry(
    registry: dict[str, Any],
    root: Path,
    errors: list[str],
    *,
    final: bool = True,
) -> dict[str, dict[str, Any]]:
    if registry.get("schema_version") != METHOD_INTERFACE_SCHEMA_VERSION:
        errors.append("Method-interface registry has an unsupported schema_version")

    scope = registry.get("scope")
    if not isinstance(scope, dict):
        errors.append("Method-interface registry scope must be an object")
        scope = {}
    if final and scope.get("status") != "reviewed":
        errors.append("Method-interface registry scope.status must be reviewed")
    trigger = scope.get("trigger")
    valid_triggers = {"required", "not_required"} if final else {
        "required",
        "not_required",
        "not_set",
    }
    if not is_enum_value(trigger, valid_triggers):
        errors.append(
            "Method-interface registry scope.trigger must be required or not_required"
        )
    if final and not is_nonempty_string(scope.get("reason")):
        errors.append("Method-interface registry scope.reason must be explicit")

    records = registry.get("interfaces")
    if not isinstance(records, list):
        errors.append("Method-interface registry must contain interfaces as a list")
        return {}
    if trigger == "required" and not records:
        errors.append("A required method-interface audit must contain an interface record")
    if trigger == "not_required" and records:
        errors.append("scope.trigger cannot be not_required when interfaces are recorded")

    result: dict[str, dict[str, Any]] = {}
    for index, record in enumerate(records, 1):
        prefix = f"Method interface {index}"
        if not isinstance(record, dict):
            errors.append(f"{prefix} must be an object")
            continue
        interface_id = record.get("id")
        if not isinstance(interface_id, str) or not INTERFACE_ID_RE.fullmatch(interface_id):
            errors.append(f"{prefix}.id must match MI-001")
            continue
        if interface_id in result:
            errors.append(f"Duplicate method interface id: {interface_id}")
        result[interface_id] = record
        prefix = interface_id

        if not is_enum_value(record.get("kind"), INTERFACE_KINDS):
            errors.append(f"{prefix}.kind is invalid")
        if not isinstance(record.get("load_bearing"), bool):
            errors.append(f"{prefix}.load_bearing must be true or false")
        if not isinstance(record.get("implementation_required_for_claim"), bool):
            errors.append(
                f"{prefix}.implementation_required_for_claim must be true or false"
            )
        if not isinstance(record.get("execution_provenance_required_for_claim"), bool):
            errors.append(
                f"{prefix}.execution_provenance_required_for_claim must be true or false"
            )
        validate_string_list(
            record.get("affected_results"), f"{prefix}.affected_results", errors
        )

        target = record.get("population_target")
        if not isinstance(target, dict):
            errors.append(f"{prefix}.population_target must be an object")
            target = {}
        for field in ("formula", "measure_and_support", "equality_notion"):
            if not is_nonempty_string(target.get(field)):
                errors.append(f"{prefix}.population_target.{field} must be explicit")
        if not is_nonempty_string(record.get("identification_identity")):
            errors.append(f"{prefix}.identification_identity must be explicit")

        sample_laws = record.get("fitting_sample_laws")
        sample_roles: list[str] = []
        if not isinstance(sample_laws, list) or not sample_laws:
            errors.append(f"{prefix}.fitting_sample_laws must be a nonempty list")
            sample_laws = []
        for law_index, law in enumerate(sample_laws, 1):
            law_prefix = f"{prefix}.fitting_sample_laws[{law_index}]"
            if not isinstance(law, dict):
                errors.append(f"{law_prefix} must be an object")
                continue
            role = law.get("role")
            if not is_nonempty_string(role):
                errors.append(f"{law_prefix}.role must be explicit")
            else:
                sample_roles.append(role)
            for field in ("law", "reference_law"):
                if not is_nonempty_string(law.get(field)):
                    errors.append(f"{law_prefix}.{field} must be explicit")
            validate_locked_span_list(
                law.get("evidence_spans"),
                root,
                f"{law_prefix}.evidence_spans",
                errors,
            )
        if len(sample_roles) != len(set(sample_roles)):
            errors.append(f"{prefix}.fitting_sample_laws has duplicate roles")
        if record.get("kind") == "density_ratio" and set(sample_roles) != {
            "numerator",
            "denominator",
        }:
            errors.append(
                f"{prefix}: density_ratio requires exactly numerator and denominator laws"
            )

        for field in ("marginal_relationships", "evaluation_sites", "downstream_uses"):
            validate_string_list(record.get(field), f"{prefix}.{field}", errors)

        specification = record.get("interface_specification_status")
        if not is_enum_value(specification, INTERFACE_SPECIFICATION_STATUSES):
            errors.append(f"{prefix}.interface_specification_status is invalid")
        derivation = record.get("derivation_status")
        if not is_enum_value(derivation, ARGUMENT_STATUSES):
            errors.append(f"{prefix}.derivation_status is invalid")

        target_relation = record.get("target_relation")
        if not isinstance(target_relation, dict):
            errors.append(f"{prefix}.target_relation must be an object")
            target_relation = {}
        target_verdict = target_relation.get("verdict")
        if not is_enum_value(target_verdict, TARGET_RELATION_VERDICTS):
            errors.append(f"{prefix}.target_relation.verdict is invalid")
        if not is_nonempty_string(target_relation.get("reason")):
            errors.append(f"{prefix}.target_relation.reason must be explicit")
        target_assumptions = validate_string_list(
            target_relation.get("assumptions"),
            f"{prefix}.target_relation.assumptions",
            errors,
            allow_empty=True,
        )
        target_spans = validate_locked_span_list(
            target_relation.get("evidence_spans"),
            root,
            f"{prefix}.target_relation.evidence_spans",
            errors,
        )
        if target_verdict == "conditional_match" and not target_assumptions:
            errors.append(f"{prefix}: conditional_match requires named assumptions")
        if is_enum_value(specification, {"ambiguous", "incomplete"}) and not is_enum_value(
            target_verdict, {"not_assessable", "not_checked"}
        ):
            errors.append(
                f"{prefix}: an ambiguous or incomplete specification cannot establish "
                f"target_relation {target_verdict!r}"
            )
        if target_verdict == "mismatch" and specification != "clear":
            errors.append(
                f"{prefix}: mismatch requires authoritative evidence fixing the estimator specification"
            )
        if target_verdict == "mismatch" and not any(
                is_enum_value(
                    span.get("role"),
                    {
                        "authoritative_definition",
                        "authoritative_algorithm",
                        "authoritative_configuration",
                    },
                )
            for span in target_spans
        ):
            errors.append(
                f"{prefix}: mismatch requires an authoritative source-locked span"
            )

        implementation = record.get("implementation_relation")
        if not isinstance(implementation, dict):
            errors.append(f"{prefix}.implementation_relation must be an object")
            implementation = {}
        inspection_status = implementation.get("inspection_status")
        if not is_enum_value(inspection_status, IMPLEMENTATION_INSPECTION_STATUSES):
            errors.append(
                f"{prefix}.implementation_relation.inspection_status is invalid"
            )
        inspection_mode = implementation.get("inspection_mode")
        if not is_enum_value(inspection_mode, IMPLEMENTATION_INSPECTION_MODES):
            errors.append(f"{prefix}.implementation_relation.inspection_mode is invalid")
        implementation_spans = validate_locked_span_list(
            implementation.get("evidence_spans"),
            root,
            f"{prefix}.implementation_relation.evidence_spans",
            errors,
            allow_empty=inspection_status != "inspected",
        )
        allowed_implementation_roles = {
            "implementation_snapshot",
            "algorithm_specification",
            "configuration",
        }
        if inspection_status == "inspected":
            if not is_nonempty_string(implementation.get("revision")):
                errors.append(
                    f"{prefix}: inspected implementation requires an exact revision"
                )
            if inspection_mode == "not_applicable":
                errors.append(
                    f"{prefix}: inspected implementation requires static, executed, or both"
                )
            if not implementation_spans:
                errors.append(
                    f"{prefix}: inspected implementation requires hash-locked evidence"
                )
            if any(
                not is_enum_value(span.get("role"), allowed_implementation_roles)
                for span in implementation_spans
            ):
                errors.append(
                    f"{prefix}: implementation evidence has an unsupported role"
                )
        elif inspection_mode != "not_applicable":
            errors.append(
                f"{prefix}: uninspected implementation must use inspection_mode not_applicable"
            )
        if not is_nonempty_string(implementation.get("reason")):
            errors.append(f"{prefix}.implementation_relation.reason must be explicit")

        comparisons = implementation.get("comparisons")
        comparison_by_target: dict[str, dict[str, Any]] = {}
        if not isinstance(comparisons, list):
            errors.append(f"{prefix}.implementation_relation.comparisons must be a list")
            comparisons = []
        for comparison_index, comparison in enumerate(comparisons, 1):
            comparison_prefix = (
                f"{prefix}.implementation_relation.comparisons[{comparison_index}]"
            )
            if not isinstance(comparison, dict):
                errors.append(f"{comparison_prefix} must be an object")
                continue
            target_name = comparison.get("to")
            verdict = comparison.get("verdict")
            if not is_enum_value(
                target_name, {"documented_estimator", "required_target"}
            ):
                errors.append(f"{comparison_prefix}.to is invalid")
                continue
            if target_name in comparison_by_target:
                errors.append(f"{prefix}: duplicate implementation comparison {target_name}")
            comparison_by_target[target_name] = comparison
            if not is_enum_value(verdict, IMPLEMENTATION_COMPARISON_VERDICTS):
                errors.append(f"{comparison_prefix}.verdict is invalid")
            if not is_nonempty_string(comparison.get("reason")):
                errors.append(f"{comparison_prefix}.reason must be explicit")
            comparison_spans = validate_locked_span_list(
                comparison.get("evidence_spans"),
                root,
                f"{comparison_prefix}.evidence_spans",
                errors,
                allow_empty=not is_enum_value(
                    verdict, {"consistent", "inconsistent"}
                ),
            )
            if is_enum_value(verdict, {"consistent", "inconsistent"}):
                if inspection_status != "inspected":
                    errors.append(
                        f"{comparison_prefix}: a definite comparison requires inspected evidence"
                    )
                if not comparison_spans:
                    errors.append(
                        f"{comparison_prefix}: a definite comparison requires locked evidence"
                    )
            if inspection_status != "inspected" and not is_enum_value(
                verdict, {"not_assessable", "not_checked", "not_applicable"}
            ):
                errors.append(
                    f"{comparison_prefix}: uninspected code cannot support a definite comparison"
                )
        if set(comparison_by_target) != {"documented_estimator", "required_target"}:
            errors.append(
                f"{prefix}: implementation comparisons must cover documented_estimator and required_target"
            )
        if inspection_status == "not_applicable" and any(
            comparison.get("verdict") != "not_applicable"
            for comparison in comparison_by_target.values()
        ):
            errors.append(
                f"{prefix}: not_applicable implementation inspection requires not_applicable comparisons"
            )

        provenance = implementation.get("execution_provenance")
        if not isinstance(provenance, dict):
            errors.append(
                f"{prefix}.implementation_relation.execution_provenance must be an object"
            )
            provenance = {}
        provenance_status = provenance.get("status")
        if not is_enum_value(provenance_status, EXECUTION_PROVENANCE_STATUSES):
            errors.append(
                f"{prefix}.implementation_relation.execution_provenance.status is invalid"
            )
        if not is_nonempty_string(provenance.get("reason")):
            errors.append(
                f"{prefix}.implementation_relation.execution_provenance.reason must be explicit"
            )
        provenance_spans = validate_locked_span_list(
            provenance.get("evidence_spans"),
            root,
            f"{prefix}.implementation_relation.execution_provenance.evidence_spans",
            errors,
            allow_empty=not is_enum_value(
                provenance_status, {"matched", "not_matched"}
            ),
        )
        if is_enum_value(provenance_status, {"matched", "not_matched"}):
            if inspection_status != "inspected":
                errors.append(
                    f"{prefix}: execution provenance requires an inspected implementation revision"
                )
            if not provenance_spans:
                errors.append(
                    f"{prefix}: execution provenance requires locked run-linkage evidence"
                )
            if any(
                not is_enum_value(
                    span.get("role"),
                    {"execution_provenance", "run_configuration"},
                )
                for span in provenance_spans
            ):
                errors.append(
                    f"{prefix}: execution provenance evidence has an unsupported role"
                )
        if inspection_status == "not_applicable" and provenance_status != "not_applicable":
            errors.append(
                f"{prefix}: not_applicable implementation inspection requires not_applicable provenance"
            )

        alternatives = record.get("alternative_interpretations")
        if not isinstance(alternatives, list):
            errors.append(f"{prefix}.alternative_interpretations must be a list")
            alternatives = []
        for alt_index, alternative in enumerate(alternatives, 1):
            alt_prefix = f"{prefix}.alternative_interpretations[{alt_index}]"
            if not isinstance(alternative, dict):
                errors.append(f"{alt_prefix} must be an object")
                continue
            for field in ("interpretation", "consequence"):
                if not is_nonempty_string(alternative.get(field)):
                    errors.append(f"{alt_prefix}.{field} must be explicit")
            validate_string_list(
                alternative.get("evidence"), f"{alt_prefix}.evidence", errors
            )
        if is_enum_value(specification, {"ambiguous", "incomplete"}) and len(alternatives) < 2:
            errors.append(
                f"{prefix}: ambiguous or incomplete interfaces require at least two interpretations"
            )

        resolution_needed = record.get("resolution_evidence_needed")
        unresolved_interface = (
            is_enum_value(
                specification, {"ambiguous", "incomplete", "not_checked"}
            )
            or is_enum_value(
                target_verdict,
                {"conditional_match", "not_assessable", "not_checked"},
            )
            or (
                record.get("implementation_required_for_claim") is True
                and (
                    is_enum_value(
                        inspection_status,
                        {"available_not_checked", "unavailable", "out_of_scope"},
                    )
                    or any(
                        comparison_by_target.get(target_name, {}).get("verdict")
                        != "consistent"
                        for target_name in {
                            "documented_estimator",
                            "required_target",
                        }
                    )
                )
            )
            or (
                record.get("execution_provenance_required_for_claim") is True
                and provenance_status != "matched"
            )
        )
        validate_string_list(
            resolution_needed,
            f"{prefix}.resolution_evidence_needed",
            errors,
            allow_empty=not unresolved_interface,
        )
        issue_ids = validate_string_list(
            record.get("issue_ids"), f"{prefix}.issue_ids", errors, allow_empty=True
        )
        for issue_id in issue_ids:
            if not ISSUE_ID_RE.fullmatch(issue_id):
                errors.append(f"{prefix}.issue_ids contains invalid issue id {issue_id!r}")
        finding_requires_issue = (
            specification != "clear"
            or target_verdict != "match"
            or any(
                comparison.get("verdict") == "inconsistent"
                for comparison in comparison_by_target.values()
            )
            or provenance_status == "not_matched"
            or (
                record.get("implementation_required_for_claim") is True
                and is_enum_value(
                    inspection_status,
                    {"available_not_checked", "unavailable", "out_of_scope"},
                )
            )
            or (
                record.get("execution_provenance_required_for_claim") is True
                and provenance_status != "matched"
            )
        )
        if finding_requires_issue and not issue_ids:
            errors.append(f"{prefix}: non-clean interface status requires a canonical issue")
    return result


def external_result_contract(record: dict[str, Any]) -> dict[str, Any]:
    """Return the immutable external-result identity used by every use edge."""
    return {
        "source_identity": record.get("source_identity"),
        "version": record.get("version"),
        "theorem_location": record.get("theorem_location"),
        "exact_statement": record.get("exact_statement"),
        "source_evidence": record.get("source_evidence"),
    }


def validate_external_source_evidence(
    value: Any,
    root: Path,
    field: str,
    errors: list[str],
) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        errors.append(f"{field} must be a list")
        return []
    validated: list[dict[str, Any]] = []
    for index, row in enumerate(value, 1):
        prefix = f"{field}[{index}]"
        if not isinstance(row, dict):
            errors.append(f"{prefix} must be an object")
            continue
        validated.append(row)
        for name in ("file", "sha256", "locator", "role"):
            if not is_substantive_string(row.get(name)):
                errors.append(f"{prefix}.{name} must be nonempty and substantive")
        file_value = row.get("file")
        digest = row.get("sha256")
        if is_nonempty_string(file_value):
            source_path = resolve_stored_path(file_value, root)
            if not source_path.is_file():
                errors.append(f"{prefix}.file does not exist: {source_path}")
            elif not is_nonempty_string(digest) or sha256_file(source_path) != digest:
                errors.append(f"{prefix}: source drift; whole-file SHA-256 does not match")
    return validated


def validate_external_result_catalog(
    registry: dict[str, Any],
    root: Path,
    errors: list[str],
) -> tuple[dict[str, dict[str, Any]], dict[str, str]]:
    records = registry.get("external_results")
    if not isinstance(records, list):
        errors.append("Dependency registry must contain external_results as a list")
        return {}, {}
    results: dict[str, dict[str, Any]] = {}
    contract_hashes: dict[str, str] = {}
    for index, record in enumerate(records, 1):
        prefix = f"external_results[{index}]"
        if not isinstance(record, dict):
            errors.append(f"{prefix} must be an object")
            continue
        result_id = record.get("id")
        status = record.get("status")
        if not is_nonempty_string(result_id):
            errors.append(f"{prefix}.id must be a nonempty string")
            continue
        if result_id in results:
            errors.append(f"Duplicate external result id: {result_id}")
        results[result_id] = record
        if not is_enum_value(status, DEPENDENCY_STATUSES - {"not_applicable"}):
            errors.append(f"{result_id}: invalid external result status {status!r}")
        for field in (
            "source_identity",
            "version",
            "theorem_location",
            "exact_statement",
        ):
            if not is_substantive_string(record.get(field)):
                errors.append(f"{result_id}.{field} must be nonempty and substantive")
        source_evidence = validate_external_source_evidence(
            record.get("source_evidence"),
            root,
            f"{result_id}.source_evidence",
            errors,
        )
        if status != "unchecked" and not source_evidence:
            errors.append(f"{result_id}.source_evidence must not be empty")
        contract_hashes[result_id] = canonical_sha256(external_result_contract(record))
        if status == "unchecked" and not is_substantive_string(record.get("reason")):
            errors.append(f"{result_id}: unchecked external result needs a substantive reason")
        validate_issue_id_list(
            record.get("issue_ids"),
            f"{result_id}.issue_ids",
            errors,
        )
    return results, contract_hashes


def validate_dependency_registry_review(
    registry: dict[str, Any],
    *,
    source_snapshot_sha256: Any,
    inventory_sha256: str,
    in_scope: list[str],
    errors: list[str],
) -> None:
    if registry.get("schema_version") != SCHEMA_VERSION:
        errors.append("Dependency registry has an unsupported schema_version")
    if registry.get("closure_contract_version") != CLOSURE_CONTRACT_VERSION:
        errors.append(
            "Dependency registry closure_contract_version does not match the validator"
        )
    review = registry.get("review")
    if not isinstance(review, dict):
        errors.append("Dependency registry review must be an object")
        return
    if review.get("status") != "reviewed":
        errors.append("Dependency registry review.status must be reviewed")
    if review.get("source_snapshot_sha256") != source_snapshot_sha256:
        errors.append(
            "Dependency registry review.source_snapshot_sha256 is stale or incorrect"
        )
    if review.get("inventory_sha256") != inventory_sha256:
        errors.append("Dependency registry review.inventory_sha256 is stale or incorrect")
    if review.get("in_scope_units") != in_scope:
        errors.append(
            "Dependency registry review.in_scope_units must equal audit scope exactly"
        )
    validate_string_list(
        review.get("evidence"),
        "Dependency registry review.evidence",
        errors,
        substantive=True,
    )


def expected_result_uses(
    summaries_by_id: dict[str, dict[str, Any]],
    errors: list[str],
) -> dict[tuple[str, str], dict[str, Any]]:
    """Aggregate ledger invocations by stable dependency-use ID."""
    expected: dict[tuple[str, str], dict[str, Any]] = {}
    for dependent_unit, summary in summaries_by_id.items():
        direct_by_id = {
            row.get("use_id"): row
            for row in summary.get("direct_dependencies", [])
            if isinstance(row, dict) and is_nonempty_string(row.get("use_id"))
        }
        for claim in summary.get("result_dependency_claims", []):
            if (
                not isinstance(claim, dict)
                or not is_nonempty_string(claim.get("id"))
                or not is_nonempty_string(claim.get("use_id"))
            ):
                continue
            dependency_id = claim["id"]
            use_id = claim["use_id"]
            key = (dependent_unit, use_id)
            direct = direct_by_id.get(use_id)
            if direct is None:
                continue
            current = expected.setdefault(
                key,
                {
                    "dependent_unit": dependent_unit,
                    "use_id": use_id,
                    "dependency_id": dependency_id,
                    "kind": direct.get("kind"),
                    "dependency_conclusion_id": direct.get("conclusion_id"),
                    "status": direct.get("status"),
                    "needed_form": direct.get("needed_form"),
                    "compatibility_check": direct.get("compatibility_check"),
                    "step_ids": set(),
                },
            )
            for field in (
                "id",
                "use_id",
                "kind",
                "conclusion_id",
                "status",
                "needed_form",
                "compatibility_check",
            ):
                expected_field = {
                    "id": "dependency_id",
                    "conclusion_id": "dependency_conclusion_id",
                }.get(field, field)
                if current.get(expected_field) != direct.get(field):
                    errors.append(
                        f"{dependent_unit}: ledger dependency use {use_id} has "
                        f"inconsistent {field} values"
                    )
            step_id = claim.get("owner_step")
            if is_nonempty_string(step_id):
                current["step_ids"].add(step_id)
    for record in expected.values():
        record["step_ids"] = sorted(record["step_ids"])
    return expected


def validate_dependency_use_identity(
    use: Any,
    prefix: str,
    expected: dict[str, Any] | None,
    errors: list[str],
) -> dict[str, Any]:
    if not isinstance(use, dict):
        errors.append(f"{prefix} must be an object")
        return {}
    for field in ("dependent_unit", "use_id", "dependency_id"):
        if not is_nonempty_string(use.get(field)):
            errors.append(f"{prefix}.{field} must be a nonempty string")
    if (
        is_nonempty_string(use.get("use_id"))
        and not DEPENDENCY_USE_ID_RE.fullmatch(use["use_id"])
    ):
        errors.append(f"{prefix}.use_id must match D001")
    step_ids = validate_string_list(
        use.get("step_ids"),
        f"{prefix}.step_ids",
        errors,
    )
    if len(step_ids) != len(set(step_ids)):
        errors.append(f"{prefix}.step_ids contains duplicates")
    if not all(STEP_ID_RE.fullmatch(step_id) for step_id in step_ids):
        errors.append(f"{prefix}.step_ids contains an invalid ledger step ID")
    for field in ("needed_form", "dependency_conclusion", "compatibility_check"):
        if not is_substantive_string(use.get(field)):
            errors.append(f"{prefix}.{field} must be nonempty and substantive")
    if not is_nonempty_string(use.get("dependency_contract_sha256")):
        errors.append(f"{prefix}.dependency_contract_sha256 must be nonempty")
    if not is_enum_value(use.get("status"), DEPENDENCY_STATUSES - {"not_applicable"}):
        errors.append(f"{prefix}.status is invalid")
    if expected is not None:
        for field in (
            "dependent_unit",
            "use_id",
            "dependency_id",
            "dependency_conclusion_id",
            "step_ids",
            "needed_form",
            "compatibility_check",
        ):
            if use.get(field) != expected.get(field):
                errors.append(f"{prefix}.{field} disagrees with the invoking ledger")
    return use


def validate_prerequisite_map(
    value: Any,
    root: Path,
    field: str,
    errors: list[str],
) -> tuple[str, set[str]]:
    if not isinstance(value, list):
        errors.append(f"{field} must be a list")
        return "unchecked", set()
    if not value:
        errors.append(f"{field} must not be empty")
        return "unchecked", set()
    mapped_statuses: list[str] = []
    issue_ids: set[str] = set()
    for index, row in enumerate(value, 1):
        prefix = f"{field}[{index}]"
        if not isinstance(row, dict):
            errors.append(f"{prefix} must be an object")
            continue
        for name in ("prerequisite", "manuscript_evidence"):
            if not is_substantive_string(row.get(name)):
                errors.append(f"{prefix}.{name} must be nonempty and substantive")
        status = row.get("status")
        if not is_enum_value(
            status, {"satisfied", "not_satisfied", "partial", "unclear"}
        ):
            errors.append(f"{prefix}.status is invalid")
        else:
            mapped_statuses.append(
                {
                    "satisfied": "passed",
                    "not_satisfied": "gap",
                    "partial": "conditional",
                    "unclear": "unclear",
                }[status]
            )
        row_issues = validate_issue_id_list(
            row.get("issue_ids"),
            f"{prefix}.issue_ids",
            errors,
        )
        if status == "satisfied" and row_issues:
            errors.append(f"{prefix}: a satisfied prerequisite cannot cite issues")
        if is_enum_value(
            status, {"not_satisfied", "partial", "unclear"}
        ) and not row_issues:
            errors.append(f"{prefix}: a non-clean prerequisite requires issue_ids")
        issue_ids.update(row_issues)
        validate_locked_span_list(
            row.get("evidence_spans"),
            root,
            f"{prefix}.evidence_spans",
            errors,
            allow_empty=status != "satisfied",
        )
    nonclean = [status for status in mapped_statuses if status != "passed"]
    applicability = combine_dependency_statuses(nonclean) if nonclean else "passed"
    return applicability, issue_ids


def validate_dependency_closure(
    registry: dict[str, Any],
    root: Path,
    summaries_by_id: dict[str, dict[str, Any]],
    *,
    source_snapshot_sha256: Any,
    inventory_sha256: str,
    in_scope: list[str],
    errors: list[str],
) -> dict[str, Any]:
    """Validate every ledger dependency against one current reviewed use row."""
    validate_dependency_registry_review(
        registry,
        source_snapshot_sha256=source_snapshot_sha256,
        inventory_sha256=inventory_sha256,
        in_scope=in_scope,
        errors=errors,
    )
    expected = expected_result_uses(summaries_by_id, errors)
    external_results, external_hashes = validate_external_result_catalog(
        registry, root, errors
    )
    collision = set(external_results) & set(summaries_by_id)
    if collision:
        errors.append(
            "Dependency IDs cannot be both internal and external: "
            + ", ".join(sorted(collision))
        )

    edges: list[dict[str, Any]] = []
    closure_issue_ids: set[str] = set()
    seen_internal: set[tuple[str, str]] = set()
    internal_rows = registry.get("internal_uses")
    if not isinstance(internal_rows, list):
        errors.append("Dependency registry internal_uses must be a list")
        internal_rows = []
    for index, raw_use in enumerate(internal_rows, 1):
        prefix = f"internal_uses[{index}]"
        use = raw_use if isinstance(raw_use, dict) else {}
        key = (use.get("dependent_unit"), use.get("use_id"))
        valid_key = all(is_nonempty_string(item) for item in key)
        if valid_key and key in seen_internal:
            errors.append(
                f"Duplicate internal use for {key[0]} / {key[1]}"
            )
        if valid_key:
            seen_internal.add(key)
        expected_use = expected.get(key) if valid_key else None
        if expected_use is None or expected_use.get("kind") != "internal_result":
            errors.append(f"{prefix}: stale or unused internal use")
            expected_use = None
        use = validate_dependency_use_identity(use, prefix, expected_use, errors)
        dependency_id = use.get("dependency_id")
        target = summaries_by_id.get(dependency_id)
        dependency_conclusion_id = use.get("dependency_conclusion_id")
        if (
            not isinstance(dependency_conclusion_id, str)
            or not CONCLUSION_ID_RE.fullmatch(dependency_conclusion_id)
        ):
            errors.append(
                f"{prefix}.dependency_conclusion_id must identify one conclusion"
            )
        source_status = (
            internal_dependency_status(target, str(dependency_conclusion_id))
            if target
            else "unchecked"
        )
        if target is None and is_nonempty_string(dependency_id):
            errors.append(f"{prefix}: unknown internal dependency {dependency_id}")
        target_conclusion = next(
            (
                row
                for row in target.get("obligation_conclusions", [])
                if isinstance(row, dict)
                and row.get("id") == dependency_conclusion_id
            ),
            None,
        ) if target else None
        if target is not None and target_conclusion is None:
            errors.append(
                f"{prefix}: unknown dependency conclusion "
                f"{dependency_conclusion_id}"
            )
        expected_conclusion = (
            target_conclusion.get("claim")
            if isinstance(target_conclusion, dict)
            else None
        )
        expected_hash = (
            target_conclusion.get("contract_sha256")
            if isinstance(target_conclusion, dict)
            else None
        )
        if use.get("dependency_conclusion") != expected_conclusion:
            errors.append(f"{prefix}.dependency_conclusion is stale or incorrect")
        if use.get("dependency_contract_sha256") != expected_hash:
            errors.append(f"{prefix}.dependency_contract_sha256 is stale or incorrect")
        applicability, matrix_issues = validate_compatibility_matrix(
            use.get("compatibility_checks"),
            f"{prefix}.compatibility_checks",
            errors,
        )
        source_issues = (
            set(
                next(
                    (
                        row.get("issue_ids", [])
                        for row in target.get("conclusion_results", [])
                        if isinstance(row, dict)
                        and row.get("conclusion_id")
                        == dependency_conclusion_id
                    ),
                    [],
                )
            )
            if target is not None and source_status != "verified"
            else set()
        )
        expected_issues = source_issues | matrix_issues
        use_issues = validate_issue_id_list(
            use.get("issue_ids"), f"{prefix}.issue_ids", errors
        )
        if use_issues != sorted(expected_issues):
            errors.append(f"{prefix}.issue_ids do not match source and compatibility findings")
        effective = combine_dependency_statuses((source_status, applicability))
        if use.get("status") != effective:
            errors.append(
                f"{prefix}.status disagrees with source and compatibility status; expected {effective}"
            )
        if expected_use is not None and expected_use.get("status") != effective:
            errors.append(
                f"{prefix}: ledger dependency status disagrees with effective status {effective}"
            )
        if effective != "verified" and not use_issues:
            errors.append(f"{prefix}: a nonverified internal use requires canonical issues")
        closure_issue_ids.update(use_issues)
        if valid_key:
            edges.append(
                {
                    "dependent_unit": key[0],
                    "use_id": key[1],
                    "dependency_id": dependency_id,
                    "dependency_conclusion_id": dependency_conclusion_id,
                    "kind": "internal_result",
                    "source_status": source_status,
                    "applicability_status": applicability,
                    "effective_status": effective,
                    "issue_ids": use_issues,
                }
            )

    expected_internal = {
        key for key, value in expected.items() if value.get("kind") == "internal_result"
    }
    for dependent, use_id in sorted(expected_internal):
        dependency = expected[(dependent, use_id)].get("dependency_id")
        if dependency not in summaries_by_id:
            errors.append(
                f"{dependent}: unknown internal dependency {dependency}"
            )
    missing_internal = expected_internal - seen_internal
    if missing_internal:
        errors.append(
            "Dependency registry is missing internal use rows: "
            + ", ".join(f"{unit}/{use_id}" for unit, use_id in sorted(missing_internal))
        )

    seen_external: set[tuple[str, str]] = set()
    for result_id, record in external_results.items():
        uses = record.get("uses")
        if not isinstance(uses, list):
            errors.append(f"{result_id}.uses must be a list")
            uses = []
        record_issues = validate_issue_id_list(
            record.get("issue_ids"), f"{result_id}.issue_ids", errors
        )
        source_status = record.get("status")
        if source_status != "verified" and not record_issues:
            errors.append(f"{result_id}: a nonverified external result requires issue_ids")
        expected_for_result = {
            key
            for key, value in expected.items()
            if value.get("kind") == "external_result"
            and value.get("dependency_id") == result_id
        }
        if not expected_for_result:
            errors.append(f"{result_id}: unused or stale external result record")
        for index, raw_use in enumerate(uses, 1):
            prefix = f"{result_id}.uses[{index}]"
            use = raw_use if isinstance(raw_use, dict) else {}
            key = (use.get("dependent_unit"), use.get("use_id"))
            valid_key = all(is_nonempty_string(item) for item in key)
            if use.get("dependency_id") != result_id:
                errors.append(f"{prefix}.dependency_id must equal parent external result ID")
            if valid_key and key in seen_external:
                errors.append(f"Duplicate external use for {key[0]} / {key[1]}")
            if valid_key:
                seen_external.add(key)
            expected_use = expected.get(key) if valid_key else None
            if expected_use is None or expected_use.get("kind") != "external_result":
                errors.append(f"{prefix}: stale or unused external use")
                expected_use = None
            use = validate_dependency_use_identity(use, prefix, expected_use, errors)
            if use.get("dependency_conclusion") != record.get("exact_statement"):
                errors.append(f"{prefix}.dependency_conclusion is stale or incorrect")
            if use.get("dependency_contract_sha256") != external_hashes.get(result_id):
                errors.append(f"{prefix}.dependency_contract_sha256 is stale or incorrect")
            compatibility, compatibility_issues = validate_compatibility_matrix(
                use.get("compatibility_checks"),
                f"{prefix}.compatibility_checks",
                errors,
            )
            prerequisite_status, prerequisite_issues = validate_prerequisite_map(
                use.get("prerequisite_map"),
                root,
                f"{prefix}.prerequisite_map",
                errors,
            )
            applicability = combine_dependency_statuses(
                (compatibility, prerequisite_status)
            )
            if applicability == "verified":
                applicability = "passed"
            expected_issues = (
                set(record_issues) | compatibility_issues | prerequisite_issues
            )
            use_issues = validate_issue_id_list(
                use.get("issue_ids"), f"{prefix}.issue_ids", errors
            )
            if use_issues != sorted(expected_issues):
                errors.append(
                    f"{prefix}.issue_ids do not match source, prerequisite, and compatibility findings"
                )
            expected_citations = sorted(
                disposition.get("key")
                for disposition in summaries_by_id.get(
                    str(use.get("dependent_unit")), {}
                ).get("citation_dispositions", [])
                if isinstance(disposition, dict)
                and disposition.get("disposition") == "external_result"
                and disposition.get("dependency_id") == result_id
                and disposition.get("dependency_use_id") == use.get("use_id")
                and is_nonempty_string(disposition.get("key"))
            )
            citation_keys = validate_string_list(
                use.get("citation_keys"),
                f"{prefix}.citation_keys",
                errors,
            )
            if len(citation_keys) != len(set(citation_keys)):
                errors.append(f"{prefix}.citation_keys contains duplicates")
            if citation_keys != expected_citations:
                errors.append(f"{prefix}.citation_keys disagree with citation dispositions")
            effective = combine_dependency_statuses((str(source_status), applicability))
            if use.get("status") != effective:
                errors.append(
                    f"{prefix}.status disagrees with source and applicability status; expected {effective}"
                )
            if expected_use is not None and expected_use.get("status") != effective:
                errors.append(
                    f"{prefix}: ledger dependency status disagrees with effective status {effective}"
                )
            if effective != "verified" and not use_issues:
                errors.append(f"{prefix}: a nonverified external use requires canonical issues")
            closure_issue_ids.update(use_issues)
            if valid_key:
                edges.append(
                    {
                        "dependent_unit": key[0],
                        "use_id": key[1],
                        "dependency_id": result_id,
                        "dependency_conclusion_id": None,
                        "kind": "external_result",
                        "source_status": source_status,
                        "applicability_status": applicability,
                        "effective_status": effective,
                        "issue_ids": use_issues,
                    }
                )

    expected_external = {
        key for key, value in expected.items() if value.get("kind") == "external_result"
    }
    missing_external = expected_external - seen_external
    if missing_external:
        errors.append(
            "Dependency registry is missing external use rows: "
            + ", ".join(f"{unit}/{use_id}" for unit, use_id in sorted(missing_external))
        )

    graph: dict[str, set[str]] = {unit_id: set() for unit_id in summaries_by_id}
    statuses_by_unit: dict[str, list[str]] = defaultdict(list)
    for edge in edges:
        dependent = edge["dependent_unit"]
        if dependent in graph:
            statuses_by_unit[dependent].append(edge["effective_status"])
        if edge["kind"] == "internal_result" and dependent in graph:
            graph[dependent].add(edge["dependency_id"])
    cycle = find_cycle(graph)
    if cycle:
        errors.append("Proof-unit dependency cycle: " + " -> ".join(cycle))
    closure_map = {
        "verified": "verified",
        "conditional": "conditionally_verified",
        "gap": "gap",
        "incorrect": "incorrect",
        "unclear": "unclear",
        "unchecked": "not_checked",
    }
    for unit_id, summary in summaries_by_id.items():
        edge_status = combine_dependency_statuses(statuses_by_unit.get(unit_id, []))
        expected_closure = closure_map[edge_status]
        declared_closure = summary.get("review_components", {}).get(
            "dependency_closure"
        )
        if declared_closure != expected_closure:
            errors.append(
                f"{unit_id}: review.dependency_closure is {declared_closure!r}; expected {expected_closure!r} from effective uses"
            )
    return {
        "external_results": external_results,
        "edges": edges,
        "unit_graph": graph,
        "issue_ids": closure_issue_ids,
    }


def validate_completion_pass(
    value: Any, field: str, errors: list[str]
) -> None:
    if not isinstance(value, dict):
        errors.append(f"completion.{field} must be an object")
        return
    status = value.get("status")
    if not is_enum_value(status, PASS_STATUSES):
        errors.append(f"completion.{field}.status is invalid")
    elif status not in {"completed", "completed_with_findings"}:
        errors.append(f"completion.{field} has not been completed")
    validate_string_list(
        value.get("evidence"),
        f"completion.{field}.evidence",
        errors,
        substantive=True,
    )


def validate_global_consistency_pass(
    value: Any,
    in_scope: list[str],
    errors: list[str],
) -> dict[str, Any]:
    field = "completion.global_consistency_pass"
    if not isinstance(value, dict):
        errors.append(f"{field} must be an object")
        return {"defect": False, "inconclusive": True, "issue_ids": set()}
    checks = value.get("checks")
    statuses = validate_aspect_matrix(
        checks,
        f"{field}.checks",
        GLOBAL_CONSISTENCY_ASPECTS,
        GLOBAL_CONSISTENCY_STATUSES,
        True,
        errors,
    )
    issue_ids: set[str] = set()
    impacts: dict[str, dict[str, Any]] = {}
    if isinstance(checks, list):
        for index, row in enumerate(checks, 1):
            if not isinstance(row, dict):
                continue
            prefix = f"{field}.checks[{index}]"
            affected = row.get("affected_units")
            if not isinstance(affected, list) or not all(
                is_nonempty_string(item) for item in affected
            ):
                errors.append(f"{prefix}.affected_units must be a string list")
                affected = []
            elif len(affected) != len(set(affected)):
                errors.append(f"{prefix}.affected_units contains duplicates")
            unknown = set(affected) - set(in_scope)
            if unknown:
                errors.append(
                    f"{prefix}.affected_units names results outside scope: "
                    + ", ".join(sorted(unknown))
                )
            row_issues = validate_issue_id_list(
                row.get("issue_ids"), f"{prefix}.issue_ids", errors
            )
            issue_ids.update(row_issues)
            status = row.get("status")
            aspect = row.get("aspect")
            if aspect in GLOBAL_CONSISTENCY_ASPECTS:
                impacts[aspect] = {
                    "status": status,
                    "affected_units": set(affected),
                    "issue_ids": set(row_issues),
                }
            if is_enum_value(status, {"passed", "not_applicable"}):
                if affected or row_issues:
                    errors.append(
                        f"{prefix}: a clean global-consistency row requires empty affected_units and issue_ids"
                    )
            elif is_enum_value(status, {"defect", "inconclusive"}):
                if not affected or not row_issues:
                    errors.append(
                        f"{prefix}: {status} requires affected_units and issue_ids"
                    )
    has_findings = any(
        is_enum_value(status, {"defect", "inconclusive"})
        for status in statuses.values()
    )
    expected_status = "completed_with_findings" if has_findings else "completed"
    if value.get("status") != expected_status:
        errors.append(
            f"{field}.status must be {expected_status} for the recorded checks"
        )
    return {
        "defect": any(status == "defect" for status in statuses.values()),
        "inconclusive": any(
            status == "inconclusive" for status in statuses.values()
        ),
        "issue_ids": issue_ids,
        "statuses": statuses,
        "impacts": impacts,
    }


def canonical_id_field(values: Any) -> str:
    if isinstance(values, (str, bytes)):
        return "<invalid>"
    try:
        materialized = list(values)
    except (TypeError, ValueError):
        return "<invalid>"
    if not all(is_nonempty_string(value) for value in materialized):
        return "<invalid>"
    normalized = sorted(set(materialized))
    return ", ".join(normalized) if normalized else "none"


def canonical_issue_row(issue: dict[str, Any]) -> list[str]:
    values = [
        str(issue.get("id", "")),
        str(issue.get("severity", "")),
        str(issue.get("confidence", "")),
        str(issue.get("status", "")),
        str(issue.get("finding_status", "")),
        str(issue.get("load_bearing", "")),
        str(issue.get("finding_class", "")),
        str(issue.get("affected_layer", "")),
        str(issue.get("interface_id", "")),
        str(issue.get("estimator_target_status", "")),
        str(issue.get("implementation_inspection_status", "")),
        str(issue.get("code_to_documented_estimator", "")),
        str(issue.get("code_to_required_target", "")),
        str(issue.get("execution_provenance_status", "")),
        str(issue.get("affected_result", "")),
        canonical_id_field(issue.get("affected_results", [])),
        str(issue.get("summary", "")),
    ]
    return [value.replace("\n", " ") for value in values]


def canonical_interface_issue_row(issue: dict[str, Any]) -> list[str]:
    def ordered_text(value: Any) -> str:
        if not isinstance(value, list) or not all(
            is_substantive_string(item) for item in value
        ):
            return "<invalid>"
        return "; ".join(item.replace("\n", " ") for item in value)

    evidence_scope = (
        "Evidence: "
        + ordered_text(issue.get("evidence"))
        + " Consequences: "
        + ordered_text(issue.get("downstream_consequences"))
    )
    return [
        str(issue.get("id", "")),
        str(issue.get("finding_class", "")),
        str(issue.get("interface_id", "")),
        str(issue.get("estimator_target_status", "")),
        str(issue.get("implementation_inspection_status", "")),
        str(issue.get("code_to_documented_estimator", "")),
        str(issue.get("code_to_required_target", "")),
        str(issue.get("execution_provenance_status", "")),
        str(issue.get("affected_layer", "")),
        evidence_scope,
    ]


def report_section(text: str, heading: str) -> str | None:
    match = re.search(
        rf"^{re.escape(heading)}\s*$\n(.*?)(?=^##\s|\Z)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    return match.group(1) if match is not None else None


def markdown_table_rows(section: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in section.splitlines():
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            content = stripped[1:-1]
            cells: list[str] = []
            current: list[str] = []
            index = 0
            while index < len(content):
                if content[index] == "\\" and index + 1 < len(content) and content[
                    index + 1
                ] == "|":
                    current.append("|")
                    index += 2
                    continue
                if content[index] == "|":
                    cells.append("".join(current).strip())
                    current = []
                else:
                    current.append(content[index])
                index += 1
            cells.append("".join(current).strip())
            rows.append(cells)
    return rows



def finalization_target_is_safe(path: Path) -> bool:
    return not path.is_symlink() and path.parent.resolve() == path.parent


def finalization_record_path(
    manifest: dict[str, Any], root: Path
) -> tuple[Path, list[str]]:
    root = root.resolve()
    canonical = root / "audit" / "06_reports" / "FINALIZATION.json"
    errors: list[str] = []
    if not finalization_target_is_safe(canonical):
        errors.append("Canonical finalization-record location is symlinked")
    value = manifest.get("finalization_record")
    if not is_nonempty_string(value):
        errors.append("manifest.finalization_record must be a nonempty path")
        return canonical, errors
    candidate = resolve_stored_path(value, root)
    if candidate != canonical:
        errors.append(
            "manifest.finalization_record must resolve to "
            "audit/06_reports/FINALIZATION.json"
        )
    return canonical, errors


def check_audit_finalization(root: Path) -> tuple[list[str], dict[str, Any]]:
    root = root.resolve()
    errors: list[str] = []
    manifest_path = root / "AUDIT_MANIFEST.json"
    manifest, manifest_errors = load_json_object(manifest_path, "audit manifest")
    errors.extend(manifest_errors)
    if manifest_errors:
        return errors, {"audit_root": str(root), "errors": len(errors)}
    if manifest.get("schema_version") != SCHEMA_VERSION:
        errors.append("AUDIT_MANIFEST.json has an unsupported schema_version")
    protocol = manifest.get("protocol")
    if not isinstance(protocol, dict):
        errors.append("AUDIT_MANIFEST.json protocol must be an object")
        protocol = {}
    expected_protocol = protocol_identity()
    for field, expected in expected_protocol.items():
        if protocol.get(field) != expected:
            errors.append(
                f"protocol.{field} does not match the validator in use"
            )
    if not is_nonempty_string(manifest.get("method_interface_registry")):
        errors.append("manifest.method_interface_registry must be a path")
    _, finalization_path_errors = finalization_record_path(manifest, root)
    errors.extend(finalization_path_errors)

    paper_value = manifest.get("paper_file")
    paper = (
        resolve_stored_path(paper_value, root)
        if is_nonempty_string(paper_value)
        else root / "__missing_paper__"
    )
    if not paper.is_file():
        errors.append(f"Paper source not found: {paper}")

    snapshot = manifest.get("source_snapshot")
    recorded_files: dict[Path, str] = {}
    recorded_snapshot_rows: list[dict[str, str]] = []
    if not isinstance(snapshot, dict) or not isinstance(snapshot.get("files"), list):
        errors.append("Manifest source_snapshot.files must be a list")
    else:
        for index, record in enumerate(snapshot["files"], 1):
            prefix = f"source_snapshot.files[{index}]"
            if not isinstance(record, dict):
                errors.append(f"{prefix} must be an object")
                continue
            file_value = record.get("file")
            digest = record.get("sha256")
            if not is_nonempty_string(file_value) or not is_nonempty_string(digest):
                errors.append(f"{prefix} needs nonempty file and sha256 values")
                continue
            path = resolve_stored_path(file_value, root)
            if path in recorded_files:
                errors.append(f"Duplicate source snapshot entry: {path}")
            recorded_files[path] = digest
            recorded_snapshot_rows.append({"file": file_value, "sha256": digest})
        snapshot_id = snapshot.get("sha256")
        expected_snapshot_id = canonical_sha256(recorded_snapshot_rows)
        if not is_nonempty_string(snapshot_id) or snapshot_id != expected_snapshot_id:
            errors.append("Manifest source_snapshot.sha256 is missing or inconsistent")

    current_files: list[Path] = []
    current_warnings: list[str] = []
    fresh_inventory: dict[str, Any] = {"units": [], "warnings": []}
    fresh_cross_references: dict[str, Any] = {"warnings": []}
    additional_files, fls_path, discovered_project_root, recorded_outside = (
        parse_manifest_source_discovery(manifest, root, errors)
    )
    if paper.is_file():
        closure = discover_source_closure(
            paper,
            additional_files=additional_files,
            fls_file=fls_path,
            project_root=discovered_project_root or paper.parent,
        )
        current_files = closure["files"]
        current_warnings = closure["warnings"]
        if closure["outside_project_inputs"] != recorded_outside:
            errors.append(
                "source_discovery.fls.outside_project_inputs does not match "
                "the current recorder trace"
            )
        fresh_inventory = scan_formal_units(
            paper,
            source_files=current_files,
            source_warnings=current_warnings,
        )
        fresh_cross_references = scan_cross_references(
            paper,
            source_files=current_files,
            source_warnings=current_warnings,
        )
    if set(recorded_files) != set(current_files):
        missing = sorted(str(path) for path in set(current_files) - set(recorded_files))
        stale = sorted(str(path) for path in set(recorded_files) - set(current_files))
        if missing:
            errors.append("Source closure has new or unrecorded files: " + ", ".join(missing))
        if stale:
            errors.append("Source closure no longer contains: " + ", ".join(stale))
    for path, digest in recorded_files.items():
        if not path.is_file():
            errors.append(f"Snapshotted source file not found: {path}")
        elif sha256_file(path) != digest:
            errors.append(f"Source drift in included file: {path}")

    crossref_json_path = (
        root / "audit" / "01_index" / "cross_reference_audit.json"
    )
    stored_cross_references, crossref_read_errors = load_json_object(
        crossref_json_path, "cross_reference_audit.json"
    )
    errors.extend(crossref_read_errors)
    if not crossref_read_errors and stored_cross_references != fresh_cross_references:
        errors.append(
            "cross_reference_audit.json is stale or disagrees with the fresh scan"
        )
    crossref_markdown_path = (
        root / "audit" / "01_index" / "cross_reference_audit.md"
    )
    if not crossref_markdown_path.is_file():
        errors.append(f"cross_reference_audit.md not found: {crossref_markdown_path}")
    elif not crossref_read_errors and read_text(
        crossref_markdown_path
    ) != crossref_markdown(stored_cross_references):
        errors.append(
            "cross_reference_audit.md is stale or disagrees with cross_reference_audit.json"
        )

    inventory_value = manifest.get("inventory_file")
    inventory_path = (
        resolve_stored_path(inventory_value, root)
        if is_nonempty_string(inventory_value)
        else root / "__missing_inventory__"
    )
    inventory, inventory_errors = load_json_object(inventory_path, "proof-unit inventory")
    errors.extend(inventory_errors)
    units = inventory.get("units", []) if not inventory_errors else []
    if not isinstance(units, list):
        errors.append("Proof-unit inventory must contain a units list")
        units = []
    unit_inventory: dict[str, dict[str, Any]] = {}
    for index, unit in enumerate(units, 1):
        if not isinstance(unit, dict) or not is_nonempty_string(unit.get("id")):
            errors.append(f"Inventory unit {index} has no valid id")
            continue
        unit_id = unit["id"]
        if not isinstance(unit.get("proof_required"), bool):
            errors.append(f"Inventory unit {unit_id} must declare proof_required")
        if unit_id in unit_inventory:
            errors.append(f"Duplicate inventory unit id: {unit_id}")
        unit_inventory[unit_id] = unit
    fresh_units_by_id = {
        unit.get("id"): unit
        for unit in fresh_inventory.get("units", [])
        if isinstance(unit, dict) and is_nonempty_string(unit.get("id"))
    }
    fresh_unit_ids = set(fresh_units_by_id)
    required_inventory_overrides: set[tuple[str, str]] = {
        (unit_id, "manual_unit") for unit_id in set(unit_inventory) - fresh_unit_ids
    }
    missing_discovered_units = fresh_unit_ids - set(unit_inventory)
    if missing_discovered_units:
        errors.append(
            "Reviewed inventory omits parser-discovered units: "
            + ", ".join(sorted(missing_discovered_units))
        )
    for unit_id in sorted(fresh_unit_ids & set(unit_inventory)):
        fresh_unit = fresh_units_by_id[unit_id]
        reviewed_unit = unit_inventory[unit_id]
        for field in ("environment", "label", "proof_required"):
            if reviewed_unit.get(field) != fresh_unit.get(field):
                errors.append(
                    f"Reviewed inventory changes parser-discovered {field} for {unit_id}"
                )
        if canonical_location(reviewed_unit.get("statement")) != canonical_location(
            fresh_unit.get("statement")
        ):
            errors.append(
                f"Reviewed inventory changes parser-discovered statement for {unit_id}"
            )
        proof_changed = canonical_location(
            reviewed_unit.get("proof")
        ) != canonical_location(fresh_unit.get("proof"))
        if proof_changed:
            required_inventory_overrides.add((unit_id, "proof_location"))
            if reviewed_unit.get("proof_redirects") not in (None, []):
                errors.append(
                    f"{unit_id}: a replaced or rejected proof cannot retain "
                    "parser redirect spans"
                )
        elif reviewed_unit.get("proof_redirects") != fresh_unit.get(
            "proof_redirects"
        ):
            errors.append(
                f"{unit_id}: reviewed proof_redirects disagree with the parser"
            )
        fresh_association = fresh_unit.get("proof_association")
        reviewed_association = reviewed_unit.get("proof_association")
        if (
            proof_changed
            or (
                isinstance(fresh_association, dict)
                and fresh_association.get("status") == "review_required"
            )
            or reviewed_association != fresh_association
        ):
            required_inventory_overrides.add((unit_id, "proof_association"))

    scope = manifest.get("audit_scope")
    if not isinstance(scope, dict):
        errors.append("audit_scope must be a reviewed object")
        scope = {}
    if scope.get("status") != "reviewed":
        errors.append("audit_scope.status must be reviewed")
    if not is_enum_value(scope.get("depth"), {"focused", "full"}):
        errors.append("audit_scope.depth must be focused or full")
    assessment = scope.get("overall_assessment")
    if not is_enum_value(
        assessment, {"no_defect_found", "defects_found", "inconclusive"}
    ):
        errors.append("audit_scope.overall_assessment is not set")
    in_scope = validate_string_list(
        scope.get("in_scope_units"), "audit_scope.in_scope_units", errors
    )
    if len(set(in_scope)) != len(in_scope):
        errors.append("audit_scope.in_scope_units contains duplicates")
    target_units = validate_string_list(
        scope.get("target_units"), "audit_scope.target_units", errors
    )
    if not target_units:
        errors.append("audit_scope.target_units must name at least one result")
    if len(set(target_units)) != len(target_units):
        errors.append("audit_scope.target_units contains duplicates")
    if not set(target_units).issubset(in_scope):
        errors.append("Every target unit must also be in scope")
    critical = validate_string_list(
        scope.get("critical_units"), "audit_scope.critical_units", errors
    )
    if len(set(critical)) != len(critical):
        errors.append("audit_scope.critical_units contains duplicates")
    if not set(critical).issubset(in_scope):
        errors.append("Every critical unit must also be in scope")
    if (
        scope.get("depth") == "focused"
        and not set(target_units).issubset(critical)
    ):
        errors.append("Every focused target unit must also be critical")
    in_scope_interfaces = validate_string_list(
        scope.get("in_scope_interfaces"),
        "audit_scope.in_scope_interfaces",
        errors,
        allow_empty=True,
    )
    if len(set(in_scope_interfaces)) != len(in_scope_interfaces):
        errors.append("audit_scope.in_scope_interfaces contains duplicates")
    validate_string_list(
        scope.get("source_or_parser_limits"),
        "audit_scope.source_or_parser_limits",
        errors,
        allow_empty=True,
    )
    overrides = scope.get("inventory_overrides")
    override_keys: set[tuple[str, str]] = set()
    if not isinstance(overrides, list):
        errors.append("audit_scope.inventory_overrides must be a list")
        overrides = []
    for index, override in enumerate(overrides, 1):
        prefix = f"audit_scope.inventory_overrides[{index}]"
        if not isinstance(override, dict):
            errors.append(f"{prefix} must be an object")
            continue
        unit_id = override.get("unit_id")
        kind = override.get("kind")
        if not is_nonempty_string(unit_id) or not is_enum_value(
            kind, {"manual_unit", "proof_location", "proof_association"}
        ):
            errors.append(f"{prefix} needs a valid unit_id and kind")
            continue
        key = (unit_id, kind)
        if key in override_keys:
            errors.append(f"Duplicate inventory override: {unit_id}/{kind}")
        override_keys.add(key)
        for field in ("reason", "evidence"):
            if not is_substantive_string(override.get(field)):
                errors.append(
                    f"{prefix}.{field} must be nonempty and substantive"
                )
        fresh_unit = fresh_units_by_id.get(str(unit_id))
        reviewed_unit = unit_inventory.get(str(unit_id))
        if kind == "manual_unit":
            if fresh_unit is not None or reviewed_unit is None:
                errors.append(
                    f"{prefix}: manual_unit must bind one parser-omitted reviewed unit"
                )
            elif override.get("reviewed_unit_sha256") != canonical_sha256(
                reviewed_unit
            ):
                errors.append(f"{prefix}.reviewed_unit_sha256 is stale")
            elif isinstance(reviewed_unit.get("proof"), dict):
                manual_proof = reviewed_unit["proof"]
                try:
                    manual_path = resolve_stored_path(
                        str(manual_proof["file"]), paper.parent
                    )
                    manual_start = manual_proof["start_line"]
                    manual_end = manual_proof["end_line"]
                except (KeyError, TypeError, ValueError):
                    errors.append(f"{prefix}: manual proof range is invalid")
                else:
                    try:
                        safe_manual_boundary = bool(
                            is_int(manual_start)
                            and is_int(manual_end)
                            and manual_path.is_file()
                            and proof_span_has_safe_boundary(
                                manual_path, manual_start, manual_end
                            )
                        )
                    except (OSError, UnicodeError, ValueError):
                        safe_manual_boundary = False
                    if not safe_manual_boundary:
                        errors.append(
                            f"{prefix}: manual proof must equal a complete proof "
                            "environment or bounded proof region"
                        )
        elif kind == "proof_location":
            if fresh_unit is None or reviewed_unit is None:
                errors.append(
                    f"{prefix}: proof_location requires a parser-discovered unit"
                )
                continue
            parser_proof = canonical_location(fresh_unit.get("proof"))
            reviewed_proof = canonical_location(reviewed_unit.get("proof"))
            if override.get("parser_proof") != parser_proof:
                errors.append(f"{prefix}.parser_proof is stale")
            if override.get("reviewed_proof") != reviewed_proof:
                errors.append(f"{prefix}.reviewed_proof is stale")
            reviewed_association = reviewed_unit.get("proof_association")
            reviewed_method = (
                reviewed_association.get("method")
                if isinstance(reviewed_association, dict)
                else None
            )
            if (
                not is_nonempty_string(override.get("association_method"))
                or override.get("association_method") != reviewed_method
            ):
                errors.append(
                    f"{prefix}.association_method must match the reviewed association"
                )
            if reviewed_proof is None:
                if override.get("reviewed_proof_sha256") is not None:
                    errors.append(
                        f"{prefix}.reviewed_proof_sha256 must be null when the "
                        "reviewed proof is null"
                    )
            elif reviewed_proof == {}:
                errors.append(f"{prefix}.reviewed_proof is malformed")
            else:
                try:
                    reviewed_path = resolve_stored_path(
                        str(reviewed_proof["file"]), paper.parent
                    )
                    reviewed_start = reviewed_proof["start_line"]
                    reviewed_end = reviewed_proof["end_line"]
                except (KeyError, TypeError, ValueError):
                    errors.append(f"{prefix}.reviewed_proof has an invalid range")
                else:
                    if reviewed_path not in recorded_files:
                        errors.append(
                            f"{prefix}.reviewed_proof is outside the source snapshot"
                        )
                    if not is_int(reviewed_start) or not is_int(reviewed_end):
                        errors.append(
                            f"{prefix}.reviewed_proof needs integer line bounds"
                        )
                    elif reviewed_path.is_file():
                        try:
                            digest = source_span_sha256(
                                reviewed_path, reviewed_start, reviewed_end
                            )
                        except (OSError, UnicodeError, ValueError) as exc:
                            errors.append(f"{prefix}.reviewed_proof: {exc}")
                        else:
                            if override.get("reviewed_proof_sha256") != digest:
                                errors.append(
                                    f"{prefix}.reviewed_proof_sha256 is stale"
                                )
                            if not proof_span_has_safe_boundary(
                                reviewed_path, reviewed_start, reviewed_end
                            ):
                                errors.append(
                                    f"{prefix}.reviewed_proof must equal a complete "
                                    "proof environment or a bounded proof region"
                                )
                    else:
                        errors.append(
                            f"{prefix}.reviewed_proof source file is missing"
                        )
        elif kind == "proof_association":
            if fresh_unit is None or reviewed_unit is None:
                errors.append(
                    f"{prefix}: proof_association requires a parser-discovered unit"
                )
                continue
            parser_association = fresh_unit.get("proof_association")
            reviewed_association = reviewed_unit.get("proof_association")
            if override.get("parser_association") != parser_association:
                errors.append(f"{prefix}.parser_association is stale")
            if override.get("reviewed_association") != reviewed_association:
                errors.append(f"{prefix}.reviewed_association is stale")
            if not isinstance(reviewed_association, dict):
                errors.append(f"{prefix}.reviewed_association must be an object")
                continue
            association_occurrences = validate_string_list(
                reviewed_association.get("evidence_occurrence_ids"),
                f"{prefix}.reviewed_association.evidence_occurrence_ids",
                errors,
                allow_empty=True,
            )
            if len(association_occurrences) != len(
                set(association_occurrences)
            ):
                errors.append(
                    f"{prefix}.reviewed_association.evidence_occurrence_ids "
                    "contains duplicates"
                )
            if not all(
                occurrence_id.startswith("R-")
                for occurrence_id in association_occurrences
            ):
                errors.append(
                    f"{prefix}.reviewed_association.evidence_occurrence_ids "
                    "must contain parser occurrence IDs"
                )
            reviewed_status = reviewed_association.get("status")
            reviewed_method = reviewed_association.get("method")
            valid_association = bool(
                reviewed_status == "associated"
                and reviewed_method
                in {"reviewed_redirect_anchor", "reviewed_manual"}
            )
            valid_rejection = bool(
                reviewed_status == "rejected"
                and reviewed_method == "reviewed_rejection"
                and reviewed_unit.get("proof") is None
                and not association_occurrences
            )
            if (
                reviewed_association.get("target") != unit_id
                or not (valid_association or valid_rejection)
            ):
                errors.append(
                    f"{prefix}.reviewed_association must explicitly confirm or "
                    "reject the parser association"
                )
            if not is_substantive_string(
                override.get("rendered_source_evidence")
            ):
                errors.append(
                    f"{prefix}.rendered_source_evidence must be substantive"
                )
            parser_status = (
                parser_association.get("status")
                if isinstance(parser_association, dict)
                else None
            )
            parser_method = (
                parser_association.get("method")
                if isinstance(parser_association, dict)
                else None
            )
            if parser_status == "review_required" and valid_association:
                if (
                    parser_method != "redirect_anchor"
                    or reviewed_method != "reviewed_redirect_anchor"
                    or canonical_location(reviewed_unit.get("proof"))
                    != canonical_location(fresh_unit.get("proof"))
                    or reviewed_association.get("evidence_occurrence_ids")
                    != parser_association.get("evidence_occurrence_ids")
                ):
                    errors.append(
                        f"{prefix}: redirected proof confirmation must preserve the "
                        "parser candidate and its exact evidence occurrences"
                    )
            elif valid_association and canonical_location(
                reviewed_unit.get("proof")
            ) != canonical_location(
                fresh_unit.get("proof")
            ) and reviewed_method != "reviewed_manual":
                errors.append(
                    f"{prefix}: a changed proof span requires reviewed_manual"
                )
    missing_overrides = required_inventory_overrides - override_keys
    if missing_overrides:
        errors.append(
            "Reviewed inventory additions lack explicit overrides: "
            + ", ".join(f"{unit_id}/{kind}" for unit_id, kind in sorted(missing_overrides))
        )
    stale_overrides = override_keys - required_inventory_overrides
    if stale_overrides:
        errors.append(
            "Inventory overrides do not match a parser omission: "
            + ", ".join(f"{unit_id}/{kind}" for unit_id, kind in sorted(stale_overrides))
        )

    label_owners = reviewed_label_owners(
        fresh_cross_references, unit_inventory, paper.parent
    )
    support_source_lines = readable_source_lines(current_files, [])
    support_index = build_unowned_label_support_index(
        support_source_lines,
        unit_inventory.values(),
        label_owners,
        paper.parent,
    )
    canonical_evidence_by_unit: dict[str, dict[str, Any]] = {}
    reviewed_proof_spans: list[tuple[str, Path, int, int]] = []
    global_occurrence_ids = {
        occurrence.get("occurrence_id")
        for occurrence in fresh_cross_references.get("occurrences", [])
        if isinstance(occurrence, dict)
        and is_nonempty_string(occurrence.get("occurrence_id"))
    }
    for unit_id, unit in sorted(unit_inventory.items()):
        statement_location = unit.get("statement")
        if not isinstance(statement_location, dict):
            errors.append(f"{unit_id}: reviewed statement location is invalid")
        else:
            try:
                statement_path = resolve_stored_path(
                    str(statement_location["file"]), paper.parent
                )
                statement_start = statement_location["start_line"]
                statement_end = statement_location["end_line"]
            except (KeyError, TypeError, ValueError):
                errors.append(f"{unit_id}: reviewed statement range is invalid")
            else:
                if statement_path not in recorded_files:
                    errors.append(
                        f"{unit_id}: reviewed statement is outside the source snapshot"
                    )
                if (
                    not is_int(statement_start)
                    or not is_int(statement_end)
                    or not statement_path.is_file()
                ):
                    errors.append(
                        f"{unit_id}: reviewed statement has invalid source bounds"
                    )
                else:
                    try:
                        source_span_sha256(
                            statement_path, statement_start, statement_end
                        )
                    except (OSError, UnicodeError, ValueError) as exc:
                        errors.append(f"{unit_id}: reviewed statement: {exc}")

        proof_location = unit.get("proof")
        proof_association = unit.get("proof_association")
        if isinstance(proof_association, dict):
            association_occurrences = proof_association.get(
                "evidence_occurrence_ids"
            )
            if isinstance(association_occurrences, list):
                unknown_association_occurrences = {
                    occurrence_id
                    for occurrence_id in association_occurrences
                    if is_nonempty_string(occurrence_id)
                    and occurrence_id not in global_occurrence_ids
                }
                if unknown_association_occurrences:
                    errors.append(
                        f"{unit_id}: proof_association names stale source "
                        "occurrences: "
                        + ", ".join(sorted(unknown_association_occurrences))
                    )
        if isinstance(proof_location, dict):
            if (
                not isinstance(proof_association, dict)
                or proof_association.get("status") != "associated"
                or proof_association.get("target") != unit_id
            ):
                errors.append(
                    f"{unit_id}: every reviewed proof span requires an explicitly "
                    "associated proof_association"
                )
            try:
                proof_path = resolve_stored_path(
                    str(proof_location["file"]), paper.parent
                )
                proof_start = proof_location["start_line"]
                proof_end = proof_location["end_line"]
            except (KeyError, TypeError, ValueError):
                errors.append(f"{unit_id}: reviewed proof range is invalid")
                continue
            if proof_path not in recorded_files:
                errors.append(
                    f"{unit_id}: reviewed proof is outside the source snapshot"
                )
            if (
                not is_int(proof_start)
                or not is_int(proof_end)
                or not proof_path.is_file()
            ):
                errors.append(f"{unit_id}: reviewed proof has invalid source bounds")
                continue
            try:
                source_span_sha256(proof_path, proof_start, proof_end)
                if not proof_span_has_safe_boundary(
                    proof_path, proof_start, proof_end
                ):
                    errors.append(
                        f"{unit_id}: reviewed proof must equal a complete proof "
                        "environment or a bounded proof region"
                    )
                evidence = reviewed_span_evidence(
                    unit_id,
                    unit,
                    paper.parent,
                    label_owners,
                    support_index,
                )
            except (OSError, UnicodeError, ValueError) as exc:
                errors.append(f"{unit_id}: cannot rescan reviewed proof span: {exc}")
                continue
            canonical_evidence_by_unit[unit_id] = evidence
            reviewed_proof_spans.append(
                (unit_id, proof_path.resolve(), proof_start, proof_end)
            )
        elif proof_location is not None:
            errors.append(f"{unit_id}: reviewed proof must be an object or null")
            evidence = {
                "reference_occurrences": [],
                "dependencies": [],
                "candidate_internal_dependencies": [],
                "citations": [],
                "warnings": [],
            }
            canonical_evidence_by_unit[unit_id] = evidence
        else:
            if (
                isinstance(proof_association, dict)
                and proof_association.get("status") == "associated"
            ):
                errors.append(
                    f"{unit_id}: proof_association cannot be associated without a proof span"
                )
            try:
                evidence = reviewed_span_evidence(
                    unit_id,
                    unit,
                    paper.parent,
                    label_owners,
                    support_index,
                )
            except (OSError, UnicodeError, ValueError) as exc:
                errors.append(
                    f"{unit_id}: cannot rescan reviewed statement span: {exc}"
                )
                continue
            canonical_evidence_by_unit[unit_id] = evidence

        for field in (
            "reference_occurrences",
            "dependencies",
            "candidate_internal_dependencies",
            "citations",
        ):
            if unit.get(field) != evidence.get(field):
                errors.append(
                    f"{unit_id}: reviewed inventory {field} disagrees with the "
                    "canonical rescan"
                )
        unrecorded_span_warnings = set(evidence.get("warnings", [])) - (
            set(current_warnings)
            | set(fresh_inventory.get("warnings", []))
            | set(fresh_cross_references.get("warnings", []))
        )
        if unrecorded_span_warnings:
            errors.append(
                f"{unit_id}: reviewed unit rescan introduced warnings absent "
                "from the reviewed parser-warning set: "
                + "; ".join(sorted(unrecorded_span_warnings))
            )

    for index, (unit_id, path, start, end) in enumerate(reviewed_proof_spans):
        for other_id, other_path, other_start, other_end in reviewed_proof_spans[
            index + 1 :
        ]:
            if (
                path == other_path
                and max(start, other_start) <= min(end, other_end)
            ):
                errors.append(
                    f"Reviewed proof spans overlap: {unit_id} and {other_id} at "
                    f"{path}"
                )
    recorded_warnings = manifest.get("parser_warnings")
    if not isinstance(recorded_warnings, list) or not all(
        is_nonempty_string(item) for item in recorded_warnings
    ):
        errors.append("manifest.parser_warnings must contain nonempty strings")
        recorded_warnings = []
    if len(recorded_warnings) != len(set(recorded_warnings)):
        errors.append("manifest.parser_warnings contains duplicates")
    fresh_warning_set = (
        set(current_warnings)
        | set(fresh_inventory.get("warnings", []))
        | set(fresh_cross_references.get("warnings", []))
    )
    if set(recorded_warnings) != fresh_warning_set:
        errors.append(
            "manifest.parser_warnings does not match the current parser warning set"
        )

    warning_reviews = manifest.get("parser_warning_reviews", [])
    if not isinstance(warning_reviews, list):
        errors.append("manifest.parser_warning_reviews must be a list")
        warning_reviews = []
    reviewed_warning_messages: list[str] = []
    for index, review in enumerate(warning_reviews, 1):
        prefix = f"parser_warning_reviews[{index}]"
        if not isinstance(review, dict):
            errors.append(f"{prefix} must be an object")
            continue
        warning = review.get("warning")
        disposition = review.get("disposition")
        if not is_nonempty_string(warning):
            errors.append(f"{prefix}.warning must be a nonempty string")
            continue
        reviewed_warning_messages.append(warning)
        if not is_enum_value(
            disposition,
            {
                "unreviewed",
                "confirmed_non_load_bearing",
                "scope_limitation",
                "unresolved",
            },
        ):
            errors.append(f"{prefix}.disposition is invalid")
        affected_units = review.get("affected_units")
        if not isinstance(affected_units, list) or not all(
            is_nonempty_string(item) for item in affected_units
        ):
            errors.append(f"{prefix}.affected_units must be a string list")
            affected_units = []
        elif len(affected_units) != len(set(affected_units)):
            errors.append(f"{prefix}.affected_units contains duplicates")
        unknown_affected = set(affected_units) - set(unit_inventory)
        if unknown_affected:
            errors.append(
                f"{prefix}.affected_units names unknown units: "
                + ", ".join(sorted(unknown_affected))
            )
        if not is_nonempty_string(review.get("evidence")):
            errors.append(f"{prefix}.evidence must be a nonempty string")
        if disposition == "unreviewed":
            errors.append(f"{prefix} has not been reviewed")
        if disposition == "unresolved" and assessment == "no_defect_found":
            errors.append(
                f"{prefix}: an unresolved parser warning blocks no_defect_found"
            )
        if disposition == "scope_limitation":
            if not scope.get("source_or_parser_limits"):
                errors.append(
                    f"{prefix}: scope_limitation requires "
                    "audit_scope.source_or_parser_limits"
                )
            if assessment == "no_defect_found" and (
                not affected_units or set(affected_units) & set(in_scope)
            ):
                errors.append(
                    f"{prefix}: an in-scope parser limitation blocks no_defect_found"
                )
    if len(reviewed_warning_messages) != len(set(reviewed_warning_messages)):
        errors.append("manifest.parser_warning_reviews contains duplicate warnings")
    if set(reviewed_warning_messages) != set(recorded_warnings):
        errors.append(
            "manifest.parser_warning_reviews must be a one-to-one review of "
            "manifest.parser_warnings"
        )

    exclusions = scope.get("excluded_units")
    excluded_ids: set[str] = set()
    if not isinstance(exclusions, list):
        errors.append("audit_scope.excluded_units must be a list")
        exclusions = []
    for index, exclusion in enumerate(exclusions, 1):
        prefix = f"audit_scope.excluded_units[{index}]"
        if not isinstance(exclusion, dict):
            errors.append(f"{prefix} must be an object")
            continue
        excluded_id = exclusion.get("id")
        if not is_nonempty_string(excluded_id) or not is_nonempty_string(
            exclusion.get("reason")
        ):
            errors.append(f"{prefix} needs nonempty id and reason")
            continue
        if excluded_id in excluded_ids:
            errors.append(f"Duplicate excluded unit: {excluded_id}")
        excluded_ids.add(excluded_id)
    if set(in_scope) & excluded_ids:
        errors.append("A proof unit cannot be both in scope and excluded")
    unknown_scope = (set(in_scope) | excluded_ids) - set(unit_inventory)
    if unknown_scope:
        errors.append("Scope names unknown inventory units: " + ", ".join(sorted(unknown_scope)))
    omitted_inventory = set(unit_inventory) - set(in_scope) - excluded_ids
    if omitted_inventory:
        errors.append(
            "Inventory units lack an in-scope or explicit-exclusion decision: "
            + ", ".join(sorted(omitted_inventory))
        )
    if scope.get("depth") == "full":
        excluded_proof_units = {
            unit_id
            for unit_id, unit in unit_inventory.items()
            if unit.get("proof_required") is True and unit_id not in set(in_scope)
        }
        if excluded_proof_units:
            errors.append(
                "A full audit cannot exclude proof-required units: "
                + ", ".join(sorted(excluded_proof_units))
            )

    cross_reference_result = validate_cross_reference_reviews(
        manifest.get("cross_reference_reviews"),
        fresh_cross_references,
        in_scope,
        errors,
    )

    completion = manifest.get("completion")
    if not isinstance(completion, dict):
        errors.append("completion must be an object")
        completion = {}
    for field in (
        "inventory_reviewed",
        "parser_warnings_reviewed",
        "dependency_registry_reviewed",
        "method_interface_registry_reviewed",
        "final_report_ready",
    ):
        if completion.get(field) is not True:
            errors.append(f"completion.{field} must be true")
    global_consistency_result = validate_global_consistency_pass(
        completion.get("global_consistency_pass"), in_scope, errors
    )
    source_resolution = global_consistency_result.get("impacts", {}).get(
        "source_resolution", {}
    )
    anomaly_status = (
        "defect"
        if cross_reference_result.get("defect")
        else "inconclusive"
        if cross_reference_result.get("inconclusive")
        else "clean"
    )
    source_status = source_resolution.get("status")
    if anomaly_status == "defect" and source_status != "defect":
        errors.append(
            "global source_resolution status must be defect for defect cross-reference reviews"
        )
    if anomaly_status == "inconclusive" and not is_enum_value(
        source_status, {"defect", "inconclusive"}
    ):
        errors.append(
            "global source_resolution status must cover inconclusive cross-reference reviews"
        )
    if not set(cross_reference_result.get("affected_units", set())).issubset(
        source_resolution.get("affected_units", set())
    ):
        errors.append(
            "global source_resolution affected_units omit cross-reference impacts"
        )
    if not set(cross_reference_result.get("issue_ids", set())).issubset(
        source_resolution.get("issue_ids", set())
    ):
        errors.append("global source_resolution issue_ids omit cross-reference issues")
    validate_completion_pass(
        completion.get("adversarial_pass"), "adversarial_pass", errors
    )
    final_report = root / "audit" / "06_reports" / "FINAL_REPORT.md"
    report_assessment: str | None = None
    report_text = ""
    report_fields: dict[str, str] = {}
    if not final_report.is_file():
        errors.append(f"Final report not found: {final_report}")
    elif completion.get("final_report_ready") is True:
        report_text = read_text(final_report)
        for label in (
            "Overall assessment code",
            "Overall judgment",
            "Checked scope",
            "Target results",
            "Source revision",
            "Skill version",
            "Artifact schema version",
            "Evidence contract version",
            "Method-interface schema version",
            "Closure contract version",
            "Source snapshot ID",
            "Finalization record",
            "Highest-consequence issue",
            "Final confidence",
            "Files and results checked",
            "Results not checked",
            "External results checked",
            "External results not checked",
            "Tooling, extraction, or rendering limitations",
            "Independence level of the critical-path challenge",
        ):
            matches = list(re.finditer(
                rf"^- {re.escape(label)}:\s*(.*?)\s*$", report_text, re.MULTILINE
            ))
            if not matches:
                errors.append(f"Final report is missing the {label} field")
            elif len(matches) != 1:
                errors.append(f"Final report has a duplicate {label} field")
            elif not matches[0].group(1):
                errors.append(f"Final report still has an empty {label} field")
            else:
                report_fields[label] = matches[0].group(1)
                if label == "Overall assessment code":
                    report_assessment = matches[0].group(1)
        for heading in (
            "## Audit boundary and limitations",
            "## Main theorem chain",
            "## Conclusion judgments",
            "## Dependency closure",
            "## Independent critical-path challenge",
            "## Issue summary",
            "## Method-interface findings",
            "## Proposed repairs",
            "## Computational evidence",
            "## Unchecked scope",
            "## Assurance boundary",
        ):
            heading_count = len(
                re.findall(rf"^{re.escape(heading)}\s*$", report_text, re.MULTILINE)
            )
            if heading_count == 0:
                errors.append(f"Final report is missing required heading: {heading}")
            elif heading_count != 1:
                errors.append(f"Final report has a duplicate required heading: {heading}")
        for obsolete_heading in (
            "## Verified results",
            "## Conditional, gap, incorrect, or unclear results",
        ):
            if re.search(
                rf"^{re.escape(obsolete_heading)}\s*$", report_text, re.MULTILINE
            ):
                errors.append(
                    f"Final report contains obsolete duplicate status heading: {obsolete_heading}"
                )
        if report_assessment is not None and report_assessment != assessment:
            errors.append(
                "Final report assessment disagrees with audit_scope.overall_assessment"
            )
        expected_report_protocol = {
            "Skill version": SKILL_VERSION,
            "Artifact schema version": str(SCHEMA_VERSION),
            "Evidence contract version": str(EVIDENCE_CONTRACT_VERSION),
            "Method-interface schema version": str(METHOD_INTERFACE_SCHEMA_VERSION),
            "Closure contract version": str(CLOSURE_CONTRACT_VERSION),
            "Source snapshot ID": (
                snapshot.get("sha256") if isinstance(snapshot, dict) else None
            ),
            "Finalization record": manifest.get("finalization_record"),
        }
        for label, expected in expected_report_protocol.items():
            if report_fields.get(label) != expected:
                errors.append(f"Final report {label} disagrees with the manifest")
        canonical_judgments = {
            "no_defect_found": "No defect found under the stated non-formal protocol.",
            "defects_found": "Defects found under the stated non-formal protocol.",
            "inconclusive": "Inconclusive under the stated non-formal protocol.",
        }
        canonical_judgment = (
            canonical_judgments.get(assessment)
            if isinstance(assessment, str)
            else None
        )
        if report_fields.get("Overall judgment") != canonical_judgment:
            errors.append("Final report Overall judgment is not the canonical judgment")
        if report_fields.get("Checked scope") != canonical_id_field(in_scope):
            errors.append("Final report Checked scope disagrees with audit scope")
        if report_fields.get("Target results") != canonical_id_field(
            target_units
        ):
            errors.append("Final report Target results disagrees with audit scope")
        if report_fields.get("Results not checked") != canonical_id_field(excluded_ids):
            errors.append("Final report Results not checked disagrees with exclusions")
        expected_limits = canonical_id_field(scope.get("source_or_parser_limits", []))
        if report_fields.get(
            "Tooling, extraction, or rendering limitations"
        ) != expected_limits:
            errors.append(
                "Final report Tooling, extraction, or rendering limitations disagree with audit scope"
            )
        if "This is a non-formal audit." not in report_text:
            errors.append("Final report must state the non-formal assurance boundary")
        if re.search(
            r"(?:complete proof certification|certif(?:y|ies|ied).{0,80}proof.{0,40}(?:correct|valid))",
            report_text,
            re.IGNORECASE | re.DOTALL,
        ):
            errors.append("Final report contains unsupported proof-certification language")
        if re.search(
            r"(?<!not )(?<!not a )\b(?:formally\s+(?:verified|checked|certified)|"
            r"(?:kernel|machine|proof[- ]assistant)[ -](?:checked|verified|certified))"
            r"\s+(?:mathematical\s+)?proof\b|"
            r"\bproof\b.{0,40}\b(?:is|was|has been)\s+(?!not\b)formally\s+"
            r"(?:verified|checked|certified)\b",
            report_text,
            re.IGNORECASE | re.DOTALL,
        ):
            errors.append(
                "Final report contains unsupported formal-verification language"
            )
        if re.search(
            r"\b(?:every|all)\b.{0,80}\b(?:theorem|proof)s?\b.{0,100}\b(?:correct|valid)\b",
            report_text,
            re.IGNORECASE | re.DOTALL,
        ):
            errors.append("Final report contains an unsupported correctness overclaim")

    ledger_errors, summaries, referenced = audit_ledgers(root, True)
    errors.extend(ledger_errors)
    referenced.update(global_consistency_result.get("issue_ids", set()))
    referenced.update(cross_reference_result.get("issue_ids", set()))
    if not summaries:
        errors.append("Finalization requires at least one proof-unit ledger")
    summaries_by_id: dict[str, dict[str, Any]] = {}
    for summary in summaries:
        unit_id = summary.get("unit_id")
        if not is_nonempty_string(unit_id):
            continue
        if unit_id in summaries_by_id:
            errors.append(f"Duplicate ledger unit_id: {unit_id}")
        summaries_by_id[unit_id] = summary
    missing_ledgers = set(in_scope) - set(summaries_by_id)
    extra_ledgers = set(summaries_by_id) - set(in_scope)
    if missing_ledgers:
        errors.append("In-scope units missing ledgers: " + ", ".join(sorted(missing_ledgers)))
    if extra_ledgers:
        errors.append("Ledgers exist outside declared scope: " + ", ".join(sorted(extra_ledgers)))

    for unit_id in sorted(set(in_scope) & set(summaries_by_id) & set(unit_inventory)):
        summary = summaries_by_id[unit_id]
        unit = unit_inventory[unit_id]
        statement = unit.get("statement")
        if not isinstance(statement, dict):
            errors.append(f"{unit_id}: invalid inventory statement location")
            continue
        try:
            statement_source = resolve_stored_path(str(statement["file"]), paper.parent)
            statement_start = statement["start_line"]
            statement_end = statement["end_line"]
        except (KeyError, TypeError, ValueError):
            errors.append(f"{unit_id}: invalid inventory statement range")
            continue
        exact_contract_anchor = any(
            Path(span.get("file", "")).resolve() == statement_source
            and span.get("start_line") == statement_start
            and span.get("end_line") == statement_end
            for span in summary.get("obligation_statement_spans", [])
        )
        if not exact_contract_anchor:
            errors.append(
                f"{unit_id}: obligation statement span does not exactly match the inventory"
            )
        for span in summary.get("obligation_statement_spans", []) + summary.get(
            "obligation_context_spans", []
        ):
            span_path = Path(span.get("file", "")).resolve()
            if span_path not in recorded_files:
                errors.append(
                    f"{unit_id}: obligation span is outside the snapshotted source closure: "
                    f"{span_path}"
                )

        proof_location = unit.get("proof")
        if (
            unit.get("proof_required") is True
            and proof_location is None
            and not is_enum_value(
                summary.get("declared_unit_status"),
                {"gap", "incorrect", "unclear"},
            )
        ):
            errors.append(
                f"{unit_id}: proof-required result has no inventoried proof range"
            )
        coverage_target = proof_location if isinstance(proof_location, dict) else statement
        try:
            target_source = resolve_stored_path(
                str(coverage_target["file"]), paper.parent
            )
            target_start = coverage_target["start_line"]
            target_end = coverage_target["end_line"]
            if (
                isinstance(proof_location, dict)
                and target_source == statement_source
                and summary.get("coverage_mode") == "statement_and_proof"
            ):
                target_start = min(target_start, statement_start)
                target_end = max(target_end, statement_end)
        except (KeyError, TypeError, ValueError):
            errors.append(f"{unit_id}: invalid inventoried proof range")
        else:
            if (
                target_source != statement_source
                and summary.get("coverage_mode") != "proof_with_separate_statement"
            ):
                errors.append(
                    f"{unit_id}: cross-file statement and proof require "
                    "proof_with_separate_statement coverage"
                )
            if target_source != Path(summary.get("source_file", "")).resolve():
                errors.append(
                    f"{unit_id}: ledger does not cover the inventoried proof source file"
                )
            elif not (
                summary.get("source_start", 0) <= target_start
                and summary.get("source_end", 0) >= target_end
            ):
                errors.append(
                    f"{unit_id}: ledger range omits part of the required statement/proof source"
                )

        direct_by_use = {
            record.get("use_id"): record
            for record in summary.get("direct_dependencies", [])
            if isinstance(record, dict)
            and is_nonempty_string(record.get("use_id"))
        }
        dispositions_by_occurrence = {
            record.get("occurrence_id"): record
            for record in summary.get("source_reference_dispositions", [])
            if isinstance(record, dict)
            and is_nonempty_string(record.get("occurrence_id"))
        }
        source_occurrences = {
            record.get("occurrence_id"): record
            for record in canonical_evidence_by_unit.get(unit_id, {}).get(
                "reference_occurrences", []
            )
            if isinstance(record, dict)
            and is_nonempty_string(record.get("occurrence_id"))
        }
        step_result_claims = {
            claim.get("use_id"): claim
            for claim in summary.get("result_dependency_claims", [])
            if isinstance(claim, dict)
            and is_nonempty_string(claim.get("use_id"))
        }
        missing_dispositions = set(source_occurrences) - set(
            dispositions_by_occurrence
        )
        if missing_dispositions:
            errors.append(
                f"{unit_id}: source occurrences lack reviewed dispositions: "
                + ", ".join(sorted(missing_dispositions))
            )
        stale_dispositions = set(dispositions_by_occurrence) - set(
            source_occurrences
        )
        if stale_dispositions:
            errors.append(
                f"{unit_id}: source-reference dispositions are not present in "
                "the reviewed proof: "
                + ", ".join(sorted(stale_dispositions))
            )
        proof_path: Path | None = None
        proof_start = proof_end = proof_last_line = 0
        if isinstance(proof_location, dict):
            try:
                proof_path = resolve_stored_path(
                    str(proof_location["file"]), paper.parent
                )
                proof_start = proof_location["start_line"]
                proof_end = proof_location["end_line"]
                if is_int(proof_start) and is_int(proof_end):
                    proof_last_line = last_substantive_line(
                        proof_path, proof_start, proof_end
                    )
            except (KeyError, TypeError, ValueError, OSError, UnicodeError):
                proof_path = None
        for occurrence_id, disposition in dispositions_by_occurrence.items():
            occurrence = source_occurrences.get(occurrence_id)
            if occurrence is None:
                continue
            if (
                disposition.get("target") != occurrence.get("target")
                or disposition.get("command") != occurrence.get("command")
            ):
                errors.append(
                    f"{unit_id}: disposition {occurrence_id} does not match the "
                    "canonical occurrence target and command"
                )
            role = disposition.get("disposition")
            target = occurrence.get("target")
            owner_status = occurrence.get("resolution_status")
            owner_unit_id = occurrence.get("owner_unit_id")
            owner_region = occurrence.get("owner_region")
            if role == "internal_result":
                use_id = disposition.get("dependency_use_id")
                dependency = direct_by_use.get(use_id)
                claim = step_result_claims.get(use_id)
                if (
                    owner_status != "unique"
                    or not is_nonempty_string(owner_unit_id)
                    or owner_unit_id == unit_id
                ):
                    errors.append(
                        f"{unit_id}: occurrence {occurrence_id} cannot be an "
                        "internal result because it has no unique other-unit owner"
                    )
                if (
                    dependency is None
                    or dependency.get("kind") != "internal_result"
                    or dependency.get("id") != owner_unit_id
                ):
                    errors.append(
                        f"{unit_id}: occurrence {occurrence_id} does not resolve "
                        "through its exact dependency use to the label owner"
                    )
                if (
                    claim is None
                    or claim.get("kind") != "internal_result"
                    or claim.get("id") != owner_unit_id
                ):
                    errors.append(
                        f"{unit_id}: occurrence {occurrence_id} is not mapped to "
                        "an exact proof-step dependency use"
                    )
            elif role == "local_step":
                if owner_status != "unique" or owner_unit_id != unit_id:
                    errors.append(
                        f"{unit_id}: local-step occurrence {occurrence_id} must "
                        "resolve to a label owned by the same unit"
                    )
            elif role == "obligation_context":
                if (
                    owner_status == "unique"
                    and (
                        owner_unit_id != unit_id
                        or owner_region != "statement"
                    )
                ):
                    errors.append(
                        f"{unit_id}: obligation occurrence {occurrence_id} is "
                        "not owned by this result's statement"
                    )
            elif role == "own_result_identification":
                closing_occurrence = bool(
                    occurrence.get("structural_context") == "proof_header"
                    or (
                        proof_path is not None
                        and is_int(occurrence.get("line"))
                        and occurrence["line"] >= max(
                            proof_start, proof_last_line - 2
                        )
                    )
                )
                if (
                    owner_status != "unique"
                    or owner_unit_id != unit_id
                    or target != unit_id
                    or not closing_occurrence
                ):
                    errors.append(
                        f"{unit_id}: own-result occurrence {occurrence_id} is "
                        "not a proof header or reviewed closing identification"
                    )
            elif role == "navigation":
                if occurrence.get("command") != "hyperref":
                    errors.append(
                        f"{unit_id}: navigation occurrence {occurrence_id} must "
                        "use an explicit hyperref command"
                    )
            elif role == "non_load_bearing":
                if (
                    owner_status == "unique"
                    and owner_unit_id == unit_id
                    and target == unit_id
                    and occurrence.get("structural_context") != "proof_header"
                    and (
                        not is_int(occurrence.get("line"))
                        or occurrence["line"] < max(
                            proof_start, proof_last_line - 2
                        )
                    )
                ):
                    errors.append(
                        f"{unit_id}: a mid-proof self-reference "
                        f"{occurrence_id} cannot be hidden as non-load-bearing"
                    )
            if (
                role == "unresolved"
                and summary.get("declared_unit_status") == "verified"
            ):
                errors.append(
                    f"{unit_id}: verified unit has unresolved source occurrence "
                    f"{occurrence_id}"
                )
            if (
                owner_status
                in {"missing", "duplicate", "ambiguous", "dynamic", "unowned"}
                and role not in {"unresolved", "navigation", "non_load_bearing"}
                and not (
                    owner_status == "unowned"
                    and role == "obligation_context"
                )
            ):
                errors.append(
                    f"{unit_id}: unresolved occurrence {occurrence_id} cannot "
                    f"serve the premise-bearing role {role}"
                )

        citation_dispositions = {
            record.get("key"): record
            for record in summary.get("citation_dispositions", [])
            if isinstance(record, dict) and is_nonempty_string(record.get("key"))
        }
        source_citations = {
            citation
            for citation in unit.get("citations", [])
            if is_nonempty_string(citation)
        }
        missing_citation_dispositions = source_citations - set(citation_dispositions)
        if missing_citation_dispositions:
            errors.append(
                f"{unit_id}: citations lack reviewed dispositions: "
                + ", ".join(sorted(missing_citation_dispositions))
            )
        stale_citation_dispositions = set(citation_dispositions) - source_citations
        if stale_citation_dispositions:
            errors.append(
                f"{unit_id}: citation dispositions are not present in the proof: "
                + ", ".join(sorted(stale_citation_dispositions))
            )
        for citation, disposition in citation_dispositions.items():
            disposition_status = disposition.get("disposition")
            if disposition_status == "external_result":
                dependency_id = disposition.get("dependency_id")
                dependency_use_id = disposition.get("dependency_use_id")
                dependency = direct_by_use.get(dependency_use_id)
                claim = step_result_claims.get(dependency_use_id)
                if (
                    dependency is None
                    or dependency.get("kind") != "external_result"
                    or dependency.get("id") != dependency_id
                ):
                    errors.append(
                        f"{unit_id}: citation {citation} does not resolve to an external "
                        "direct dependency use"
                    )
                if (
                    claim is None
                    or claim.get("kind") != "external_result"
                    or claim.get("id") != dependency_id
                ):
                    errors.append(
                        f"{unit_id}: citation dependency use {dependency_use_id} "
                        "is not mapped to a proof step"
                    )
            if (
                disposition_status == "unresolved"
                and summary.get("declared_unit_status") == "verified"
            ):
                errors.append(f"{unit_id}: verified unit has unresolved citation {citation}")

        occurrence_context = {
            occurrence.get("occurrence_id"): occurrence.get(
                "structural_context"
            )
            for evidence in canonical_evidence_by_unit.values()
            for occurrence in evidence.get("reference_occurrences", [])
            if isinstance(occurrence, dict)
            and is_nonempty_string(occurrence.get("occurrence_id"))
        }
        redirect_spans = [
            redirect
            for reviewed_unit in unit_inventory.values()
            for redirect in reviewed_unit.get("proof_redirects", [])
            if isinstance(reviewed_unit, dict)
            and isinstance(reviewed_unit.get("proof_redirects"), list)
            and isinstance(redirect, dict)
        ]
        expected_use_sites: set[str] = set()
        for occurrence in fresh_cross_references.get("occurrences", []):
            if not isinstance(occurrence, dict):
                continue
            occurrence_owner = label_owners.get(occurrence.get("target"), {})
            refers_to_unit = bool(
                occurrence.get("target") == unit_id
                or (
                    occurrence_owner.get("status") == "unique"
                    and occurrence_owner.get("owner_unit_id") == unit_id
                )
            )
            if not refers_to_unit:
                continue
            if span_contains_location(
                unit.get("statement"),
                occurrence.get("file"),
                occurrence.get("line"),
                paper.parent,
            ) or span_contains_location(
                unit.get("proof"),
                occurrence.get("file"),
                occurrence.get("line"),
                paper.parent,
            ):
                continue
            if occurrence_context.get(
                occurrence.get("occurrence_id")
            ) == "proof_header":
                continue
            if any(
                span_contains_location(
                    redirect,
                    occurrence.get("file"),
                    occurrence.get("line"),
                    paper.parent,
                )
                for redirect in redirect_spans
            ):
                continue
            if (
                is_nonempty_string(occurrence.get("file"))
                and is_int(occurrence.get("line"))
            ):
                expected_use_sites.add(
                    f"{occurrence['file']}:{occurrence['line']}"
                )
        recorded_use_sites = {
            value for value in summary.get("use_sites", []) if is_nonempty_string(value)
        }
        if recorded_use_sites != expected_use_sites:
            errors.append(
                f"{unit_id}: review.use_sites disagrees with canonical downstream "
                "uses; expected " + canonical_id_field(expected_use_sites)
            )
        if (
            expected_use_sites
            and summary.get("review_components", {}).get("use_site_sufficiency")
            == "not_applicable"
        ):
            errors.append(
                f"{unit_id}: use-site sufficiency cannot be not_applicable because "
                "the result is referenced"
            )

    registry_value = manifest.get("dependency_registry")
    registry_path = (
        resolve_stored_path(registry_value, root)
        if is_nonempty_string(registry_value)
        else root / "__missing_registry__"
    )
    registry, registry_errors = load_json_object(registry_path, "dependency registry")
    errors.extend(registry_errors)
    closure_result = (
        validate_dependency_closure(
            registry,
            root,
            summaries_by_id,
            source_snapshot_sha256=(
                snapshot.get("sha256") if isinstance(snapshot, dict) else None
            ),
            inventory_sha256=(
                sha256_file(inventory_path) if inventory_path.is_file() else ""
            ),
            in_scope=in_scope,
            errors=errors,
        )
        if not registry_errors
        else {
            "external_results": {},
            "edges": [],
            "unit_graph": {unit_id: set() for unit_id in summaries_by_id},
            "issue_ids": set(),
        }
    )
    external_results = closure_result["external_results"]
    dependency_edges = closure_result["edges"]
    unit_graph = closure_result["unit_graph"]
    referenced.update(closure_result["issue_ids"])
    if scope.get("depth") == "focused":
        required_scope: set[str] = set()
        pending_targets = list(target_units)
        while pending_targets:
            current_unit = pending_targets.pop()
            if current_unit in required_scope:
                continue
            required_scope.add(current_unit)
            pending_targets.extend(
                dependency
                for dependency in unit_graph.get(current_unit, set())
                if dependency not in required_scope
            )
        missing_scope = required_scope - set(in_scope)
        unrelated_scope = set(in_scope) - required_scope
        if missing_scope:
            errors.append(
                "Focused audit omits transitive target dependencies: "
                + ", ".join(sorted(missing_scope))
            )
        if unrelated_scope:
            errors.append(
                "Focused audit includes units outside the exact target closure: "
                + ", ".join(sorted(unrelated_scope))
            )
    interface_registry_value = manifest.get("method_interface_registry")
    interface_registry_path = (
        resolve_stored_path(interface_registry_value, root)
        if is_nonempty_string(interface_registry_value)
        else root / "__missing_method_interface_registry__"
    )
    interface_registry, interface_registry_errors = load_json_object(
        interface_registry_path, "method-interface registry"
    )
    errors.extend(interface_registry_errors)
    interfaces = (
        validate_method_interface_registry(interface_registry, root, errors)
        if not interface_registry_errors
        else {}
    )
    if set(in_scope_interfaces) != set(interfaces):
        missing_interfaces = set(interfaces) - set(in_scope_interfaces)
        unknown_interfaces = set(in_scope_interfaces) - set(interfaces)
        if missing_interfaces:
            errors.append(
                "audit_scope.in_scope_interfaces omits registry interfaces: "
                + ", ".join(sorted(missing_interfaces))
            )
        if unknown_interfaces:
            errors.append(
                "audit_scope.in_scope_interfaces names unknown interfaces: "
                + ", ".join(sorted(unknown_interfaces))
            )
    for interface_id, interface in interfaces.items():
        affected_results = interface.get("affected_results")
        if isinstance(affected_results, list):
            unknown_results = {
                result_id
                for result_id in affected_results
                if is_nonempty_string(result_id) and result_id not in in_scope
            }
            if unknown_results:
                errors.append(
                    f"{interface_id}.affected_results names results outside scope: "
                    + ", ".join(sorted(unknown_results))
                )
    for unit_id in critical:
        summary = summaries_by_id.get(unit_id)
        if summary is None:
            continue
        challenge = summary.get("independent_check", {})
        if not challenge.get("required"):
            errors.append(f"Critical unit {unit_id} requires an independent challenger pass")
        elif not is_enum_value(challenge.get("status"), {"agreed", "resolved"}):
            errors.append(f"Critical unit {unit_id} has no reconciled challenger verdict")
        artifact = challenge.get("artifact")
        if is_nonempty_string(artifact):
            artifact_path = resolve_stored_path(artifact, root)
            if not artifact_path.is_file() or artifact_path.stat().st_size == 0:
                errors.append(
                    f"Critical unit {unit_id} challenger artifact is missing or empty: {artifact_path}"
                )

    issue_path, issues, issue_read_errors = load_issue_log(root)
    errors.extend(issue_read_errors)
    source_snapshot_id = (
        snapshot.get("sha256") if isinstance(snapshot, dict) else None
    )
    reverse_graph: dict[str, set[str]] = {
        unit_id: set() for unit_id in summaries_by_id
    }
    for dependent, dependencies in unit_graph.items():
        for dependency in dependencies:
            reverse_graph.setdefault(dependency, set()).add(dependent)
    issue_errors, _ = validate_issues(
        issues,
        referenced,
        True,
        evidence_base=root,
        interfaces=interfaces,
        source_snapshot_id=source_snapshot_id,
        in_scope=in_scope,
        reverse_graph=reverse_graph,
    )
    errors.extend(issue_errors)
    issues_by_id = {
        issue.get("id"): issue
        for issue in issues
        if isinstance(issue, dict) and is_nonempty_string(issue.get("id"))
    }
    issue_summary_path = root / "audit" / "06_reports" / "ISSUE_SUMMARY.md"
    expected_issue_summary = render_issue_summary(issues)
    if not issue_summary_path.is_file():
        errors.append(f"Canonical issue summary not found: {issue_summary_path}")
    elif read_text(issue_summary_path) != expected_issue_summary:
        errors.append("ISSUE_SUMMARY.md is stale or disagrees with ISSUE_LOG.json")
    for interface_id, interface in interfaces.items():
        issue_ids = interface.get("issue_ids")
        if not isinstance(issue_ids, list):
            continue
        for issue_id in issue_ids:
            issue = issues_by_id.get(issue_id)
            if issue is None:
                errors.append(f"{interface_id}: references undefined issue {issue_id}")
            elif issue.get("interface_id") != interface_id:
                errors.append(
                    f"{interface_id}: issue {issue_id} does not link back to the interface"
                )
    if report_text:
        checked_external = {
            result_id
            for result_id, record in external_results.items()
            if record.get("status") != "unchecked"
        }
        unchecked_external = {
            result_id
            for result_id, record in external_results.items()
            if record.get("status") == "unchecked"
        }
        if report_fields.get("External results checked") != canonical_id_field(
            checked_external
        ):
            errors.append(
                "Final report External results checked disagrees with the dependency registry"
            )
        if report_fields.get("External results not checked") != canonical_id_field(
            unchecked_external
        ):
            errors.append(
                "Final report External results not checked disagrees with the dependency registry"
            )
        unresolved_issues = [
            issue
            for issue in issues_by_id.values()
            if is_enum_value(issue.get("status"), {"open", "deferred"})
            and is_enum_value(issue.get("severity"), ISSUE_SEVERITIES)
        ]
        if unresolved_issues:
            severity_rank = {"S0": 0, "S1": 1, "S2": 2, "S3": 3}
            highest_rank = min(severity_rank[issue["severity"]] for issue in unresolved_issues)
            highest_issue_ids = {
                issue["id"]
                for issue in unresolved_issues
                if severity_rank[issue["severity"]] == highest_rank
            }
        else:
            highest_issue_ids = set()
        if report_fields.get("Highest-consequence issue") != canonical_id_field(
            highest_issue_ids
        ):
            errors.append(
                "Final report Highest-consequence issue disagrees with the issue log"
            )
        independence_levels = [
            summaries_by_id[unit_id].get("independent_check", {}).get(
                "independence_level"
            )
            for unit_id in critical
            if unit_id in summaries_by_id
        ]
        expected_independence = canonical_id_field(
            level
            for level in independence_levels
            if is_enum_value(level, INDEPENDENCE_LEVELS)
        )
        if report_fields.get(
            "Independence level of the critical-path challenge"
        ) != expected_independence:
            errors.append(
                "Final report Independence level of the critical-path challenge disagrees with critical ledgers"
            )
        challenge_section = report_section(
            report_text, "## Independent critical-path challenge"
        )
        challenge_rows = markdown_table_rows(challenge_section or "")
        challenge_header = [
            "Result",
            "Challenge status",
            "Independence level",
            "Challenger verdict",
            "Reconciled verdict",
            "Disagreements",
            "Resolution",
            "Artifact",
        ]
        if not challenge_rows or challenge_rows[0] != challenge_header:
            errors.append(
                "Final report Independent critical-path challenge has an invalid table header"
            )
        challenge_data = challenge_rows[2:] if len(challenge_rows) >= 2 else []
        expected_challenge_rows: list[list[str]] = []
        for unit_id in critical:
            check = summaries_by_id.get(unit_id, {}).get("independent_check", {})
            disagreements = check.get("disagreements")
            disagreement_text = (
                "; ".join(disagreements)
                if isinstance(disagreements, list)
                and bool(disagreements)
                and all(is_nonempty_string(item) for item in disagreements)
                else "none"
                if disagreements == []
                else "<invalid>"
            )
            resolution = check.get("resolution")
            expected_challenge_rows.append(
                [
                    unit_id,
                    str(check.get("status")),
                    str(check.get("independence_level")),
                    str(check.get("challenger_verdict")),
                    str(check.get("reconciled_verdict")),
                    disagreement_text.replace("\n", " "),
                    (
                        str(resolution).replace("\n", " ")
                        if is_substantive_string(resolution)
                        else "none"
                    ),
                    str(check.get("artifact")),
                ]
            )
        if sorted(challenge_data) != sorted(expected_challenge_rows):
            errors.append(
                "Final report Independent critical-path challenge rows disagree with critical ledgers"
            )
        checked_description = report_fields.get("Files and results checked", "")
        if paper.name not in checked_description or any(
            re.search(
                rf"(?<![A-Za-z0-9:_-]){re.escape(unit_id)}(?![A-Za-z0-9:_-])",
                checked_description,
            )
            is None
            for unit_id in in_scope
        ):
            errors.append(
                "Final report Files and results checked omits the paper or an in-scope result"
            )

        main_section = report_section(report_text, "## Main theorem chain")
        main_rows = markdown_table_rows(main_section or "")
        main_header = [
            "Result",
            "Unit status",
            "Contract fidelity",
            "Argument status",
            "Statement status",
            "Dependency closure",
            "Use-site sufficiency",
            "Evidence",
        ]
        if not main_rows or main_rows[0] != main_header:
            errors.append("Final report Main theorem chain has an invalid table header")
        main_data = main_rows[2:] if len(main_rows) >= 2 else []
        seen_main: set[str] = set()
        for row in main_data:
            if len(row) != 8 or not is_nonempty_string(row[0]):
                errors.append("Final report contains a malformed main-chain row")
                continue
            if row[0] in seen_main:
                errors.append(f"Final report has a duplicate main-chain row for {row[0]}")
            seen_main.add(row[0])
            summary = summaries_by_id.get(row[0])
            if summary is None or row[0] not in in_scope:
                errors.append(f"Final report has a stale main-chain row for {row[0]}")
                continue
            components = summary.get("review_components", {})
            expected_prefix = [
                row[0],
                str(summary.get("declared_unit_status")),
                str(components.get("contract_fidelity")),
                str(components.get("argument_status")),
                str(components.get("statement_status")),
                str(components.get("dependency_closure")),
                str(components.get("use_site_sufficiency")),
            ]
            if row[:7] != expected_prefix or not is_substantive_string(row[7]):
                errors.append(
                    f"Final report main-chain row disagrees with ledger {row[0]}"
                )
        missing_main = set(in_scope) - seen_main
        if missing_main:
            errors.append(
                "Final report Main theorem chain omits: "
                + ", ".join(sorted(missing_main))
            )
        conclusion_section = report_section(
            report_text, "## Conclusion judgments"
        )
        conclusion_rows = markdown_table_rows(conclusion_section or "")
        conclusion_header = [
            "Result",
            "Conclusion",
            "Contract fidelity",
            "Argument status",
            "Statement status",
            "Dependency closure",
            "Use-site sufficiency",
            "Support",
            "Dependency use IDs",
            "Issue IDs",
        ]
        if not conclusion_rows or conclusion_rows[0] != conclusion_header:
            errors.append(
                "Final report Conclusion judgments has an invalid table header"
            )
        conclusion_data = (
            conclusion_rows[2:] if len(conclusion_rows) >= 2 else []
        )
        expected_conclusion_rows: list[list[str]] = []
        for result_id in in_scope:
            for conclusion_result in summaries_by_id.get(
                result_id, {}
            ).get("conclusion_results", []):
                if not isinstance(conclusion_result, dict):
                    continue
                support = conclusion_result.get("support")
                support_text = (
                    f"{support.get('step_id')}/{support.get('move_id')}"
                    if isinstance(support, dict)
                    else "<invalid>"
                )
                expected_conclusion_rows.append(
                    [
                        result_id,
                        str(conclusion_result.get("conclusion_id")),
                        str(conclusion_result.get("contract_fidelity")),
                        str(conclusion_result.get("argument_status")),
                        str(conclusion_result.get("statement_status")),
                        str(conclusion_result.get("dependency_closure")),
                        str(conclusion_result.get("use_site_sufficiency")),
                        support_text,
                        canonical_id_field(
                            conclusion_result.get("dependency_use_ids", [])
                        ),
                        canonical_id_field(
                            conclusion_result.get("issue_ids", [])
                        ),
                    ]
                )
        if sorted(conclusion_data) != sorted(expected_conclusion_rows):
            errors.append(
                "Final report Conclusion judgments rows disagree with the "
                "per-conclusion ledger judgments"
            )
        closure_section = report_section(report_text, "## Dependency closure")
        closure_rows = markdown_table_rows(closure_section or "")
        closure_header = [
            "Dependent",
            "Use ID",
            "Dependency",
            "Dependency conclusion",
            "Kind",
            "Source status",
            "Applicability status",
            "Effective status",
            "Issue IDs",
        ]
        if not closure_rows or closure_rows[0] != closure_header:
            errors.append("Final report Dependency closure has an invalid table header")
        closure_data = closure_rows[2:] if len(closure_rows) >= 2 else []
        expected_closure_rows = sorted(
            [
                str(edge.get("dependent_unit")),
                str(edge.get("use_id")),
                str(edge.get("dependency_id")),
                (
                    str(edge.get("dependency_conclusion_id"))
                    if is_nonempty_string(
                        edge.get("dependency_conclusion_id")
                    )
                    else "none"
                ),
                str(edge.get("kind")),
                str(edge.get("source_status")),
                str(edge.get("applicability_status")),
                str(edge.get("effective_status")),
                canonical_id_field(edge.get("issue_ids", [])),
            ]
            for edge in dependency_edges
        )
        if sorted(closure_data) != expected_closure_rows:
            errors.append(
                "Final report Dependency closure rows disagree with canonical dependency uses"
            )
        issue_section = report_section(report_text, "## Issue summary") or ""
        issue_rows = markdown_table_rows(issue_section)
        issue_header = [
            "ID",
            "Severity",
            "Confidence",
            "Status",
            "Finding status",
            "Load-bearing",
            "Finding class",
            "Affected layer",
            "Interface",
            "Estimator target",
            "Implementation inspection",
            "Code to documented estimator",
            "Code to required target",
            "Execution provenance",
            "Affected result",
            "Affected results",
            "Summary",
        ]
        if issues_by_id:
            if not issue_rows or issue_rows[0] != issue_header:
                errors.append(
                    "Final report Issue summary must contain the canonical full-field table"
                )
            issue_data = issue_rows[2:] if len(issue_rows) >= 2 else []
            expected_issue_rows = sorted(
                canonical_issue_row(issue) for issue in issues_by_id.values()
            )
            if sorted(issue_data) != expected_issue_rows:
                errors.append(
                    "Final report Issue summary rows disagree with canonical issues"
                )
        elif issue_rows or issue_section.strip() != "No issues.":
            errors.append(
                "Final report Issue summary must state exactly No issues. when the log is empty"
            )
        method_section = report_section(
            report_text, "## Method-interface findings"
        ) or ""
        method_rows = markdown_table_rows(method_section)
        method_header = [
            "Issue ID",
            "Finding class",
            "Interface ID",
            "Estimator-target status",
            "Implementation inspection",
            "Code to documented estimator",
            "Code to required target",
            "Execution provenance",
            "Affected layer",
            "Evidence scope and consequence",
        ]
        interface_issues = [
            issue
            for issue in issues_by_id.values()
            if is_nonempty_string(issue.get("interface_id"))
        ]
        if interface_issues:
            if not method_rows or method_rows[0] != method_header:
                errors.append(
                    "Final report Method-interface findings has an invalid table header"
                )
            method_data = method_rows[2:] if len(method_rows) >= 2 else []
            expected_method_rows = sorted(
                canonical_interface_issue_row(issue) for issue in interface_issues
            )
            if sorted(method_data) != expected_method_rows:
                errors.append(
                    "Final report Method-interface findings rows disagree with canonical interface issues"
                )
        elif method_rows or method_section.strip() != "None.":
            errors.append(
                "Final report Method-interface findings must state exactly None. when there are no interface issues"
            )
        for issue_id, issue in issues_by_id.items():
            if re.search(rf"(?<![A-Za-z0-9-]){re.escape(issue_id)}(?![A-Za-z0-9-])", report_text) is None:
                errors.append(f"Final report omits canonical issue {issue_id}")
        if issues_by_id and re.search(r"\bNo issues\b\.?", report_text, re.IGNORECASE):
            errors.append("Final report says no issues although canonical issues exist")
    for unit_id, summary in summaries_by_id.items():
        links_by_step: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for link in summary.get("issue_links", []):
            issue = issues_by_id.get(link.get("issue_id"))
            if issue is None:
                continue
            links_by_step[link.get("step_id")].append(issue)
            if issue.get("scope") == "unit" and issue.get("affected_result") != unit_id:
                errors.append(
                    f"{issue.get('id')}: affected_result does not match ledger {unit_id}"
                )
            if (
                is_enum_value(issue.get("status"), {"open", "deferred"})
                and issue.get("load_bearing") is True
                and (
                    (
                        issue.get("finding_status") == "defect"
                        and is_enum_value(
                            link.get("step_status"),
                            {"verified", "conditionally_verified"},
                        )
                    )
                    or (
                        issue.get("finding_status") == "inconclusive"
                        and link.get("step_status") == "verified"
                    )
                )
            ):
                errors.append(
                    f"{unit_id}:{link.get('step_id')} cannot be {link.get('step_status')} "
                    f"while load-bearing {issue.get('id')} remains {issue.get('status')}"
                )
        for link in summary.get("issue_links", []):
            if not is_enum_value(
                link.get("step_status"), {"gap", "incorrect", "unclear"}
            ):
                continue
            related = links_by_step.get(link.get("step_id"), [])
            if related and all(issue.get("status") == "resolved" for issue in related):
                errors.append(
                    f"{unit_id}:{link.get('step_id')} has a failure status but only resolved issues"
                )

    progress_path = root / "PROGRESS.json"
    progress, progress_errors = load_json_object(progress_path, "progress state")
    errors.extend(progress_errors)
    if not progress_errors:
        if progress.get("schema_version") != SCHEMA_VERSION:
            errors.append("PROGRESS.json has an unsupported schema_version")
        if progress.get("paper_file") != paper_value:
            errors.append("PROGRESS.json paper_file disagrees with the manifest")
        if progress.get("source_snapshot_sha256") != source_snapshot_id:
            errors.append("PROGRESS.json source_snapshot_sha256 is stale")
        if progress.get("status") != "complete":
            errors.append("PROGRESS.json status must be complete")
        if progress.get("current_pass") != 8 or not is_int(
            progress.get("current_pass")
        ):
            errors.append("PROGRESS.json current_pass must be integer 8 at finalization")
        if progress.get("active_unit") is not None:
            errors.append("PROGRESS.json active_unit must be null at finalization")
        completed_units = progress.get("completed_units")
        if not isinstance(completed_units, list) or not all(
            is_nonempty_string(item) for item in completed_units
        ):
            errors.append("PROGRESS.json completed_units must contain unit IDs")
        elif completed_units != in_scope:
            errors.append(
                "PROGRESS.json completed_units must equal in-scope units exactly"
            )
        expected_conditional = sorted(
            unit_id
            for unit_id, summary in summaries_by_id.items()
            if unit_id in in_scope
            and summary.get("declared_unit_status") == "conditionally_verified"
        )
        conditional_units = progress.get("conditional_units")
        if conditional_units != expected_conditional:
            errors.append(
                "PROGRESS.json conditional_units does not match conditional ledgers"
            )
        if progress.get("blocked_units") != {}:
            errors.append("PROGRESS.json blocked_units must be empty at finalization")
        if progress.get("not_started_units") != []:
            errors.append("PROGRESS.json not_started_units must be empty at finalization")
        expected_high_priority = sorted(
            issue.get("id")
            for issue in issues
            if isinstance(issue, dict)
            and is_enum_value(issue.get("status"), {"open", "deferred"})
            and is_enum_value(issue.get("severity"), {"S0", "S1"})
            and is_nonempty_string(issue.get("id"))
        )
        if progress.get("open_high_priority_issues") != expected_high_priority:
            errors.append(
                "PROGRESS.json open_high_priority_issues does not match the issue log"
            )
        expected_limits = scope.get("source_or_parser_limits")
        if progress.get("source_or_parser_limits") != expected_limits:
            errors.append(
                "PROGRESS.json source_or_parser_limits disagrees with audit scope"
            )
        if not is_substantive_string(progress.get("next_action")):
            errors.append("PROGRESS.json next_action must be substantive")

    open_load_bearing = [
        issue
        for issue in issues
        if isinstance(issue, dict)
        and is_enum_value(issue.get("severity"), ISSUE_SEVERITIES)
        and is_enum_value(issue.get("status"), {"open", "deferred"})
        and issue.get("load_bearing") is True
    ]
    unit_statuses = {
        unit_id: summary.get("declared_unit_status")
        for unit_id, summary in summaries_by_id.items()
        if unit_id in in_scope
    }
    def implementation_components(
        interface: dict[str, Any],
    ) -> tuple[Any, dict[str, Any], Any]:
        implementation = interface.get("implementation_relation")
        if not isinstance(implementation, dict):
            return None, {}, None
        comparisons = implementation.get("comparisons")
        comparison_rows = comparisons if isinstance(comparisons, list) else []
        comparison_verdicts = {
            comparison.get("to"): comparison.get("verdict")
            for comparison in comparison_rows
            if isinstance(comparison, dict)
        }
        provenance = implementation.get("execution_provenance")
        provenance_status = (
            provenance.get("status") if isinstance(provenance, dict) else None
        )
        return (
            implementation.get("inspection_status"),
            comparison_verdicts,
            provenance_status,
        )

    interface_defect = False
    interface_inconclusive = False
    for interface in interfaces.values():
        inspection_status, comparison_verdicts, provenance_status = (
            implementation_components(interface)
        )
        target_relation = interface.get("target_relation")
        target_verdict = (
            target_relation.get("verdict")
            if isinstance(target_relation, dict)
            else None
        )
        if (
            target_verdict == "mismatch"
            or (
                interface.get("implementation_required_for_claim") is True
                and "inconsistent" in comparison_verdicts.values()
            )
            or (
                interface.get("execution_provenance_required_for_claim") is True
                and provenance_status == "not_matched"
            )
        ):
            interface_defect = True
        if interface.get("load_bearing") is not True:
            continue
        if (
            is_enum_value(
                interface.get("interface_specification_status"),
                {"ambiguous", "incomplete", "not_checked"},
            )
            or is_enum_value(
                target_verdict,
                {"conditional_match", "not_assessable", "not_checked"},
            )
            or (
                interface.get("implementation_required_for_claim") is True
                and (
                    inspection_status != "inspected"
                    or comparison_verdicts.get("documented_estimator") != "consistent"
                    or comparison_verdicts.get("required_target") != "consistent"
                )
            )
            or (
                interface.get("execution_provenance_required_for_claim") is True
                and provenance_status != "matched"
            )
        ):
            interface_inconclusive = True
    for issue in open_load_bearing:
        allowed = (
            {"gap", "incorrect", "unclear", "not_checked"}
            if issue.get("finding_status") == "defect"
            else {
                "conditionally_verified",
                "gap",
                "incorrect",
                "unclear",
                "not_checked",
            }
            if issue.get("finding_status") == "inconclusive"
            else set(UNIT_STATUSES)
        )
        for unit_id in issue.get("affected_results", []):
            unit_status = unit_statuses.get(unit_id)
            if unit_status is not None and not is_enum_value(unit_status, allowed):
                errors.append(
                    f"{issue.get('id')}: load-bearing {issue.get('finding_status')} finding has not weakened affected result {unit_id}"
                )

    parser_inconclusive = False
    for warning_review in warning_reviews:
        if not isinstance(warning_review, dict):
            parser_inconclusive = True
            continue
        disposition = warning_review.get("disposition")
        if disposition == "unresolved":
            parser_inconclusive = True
            continue
        if disposition != "scope_limitation":
            continue
        affected = warning_review.get("affected_units")
        if (
            not isinstance(affected, list)
            or not affected
            or bool(
                {
                    item for item in affected if is_nonempty_string(item)
                }
                & set(in_scope)
            )
        ):
            parser_inconclusive = True
    dependency_defect = any(
        is_enum_value(edge.get("effective_status"), {"gap", "incorrect"})
        for edge in dependency_edges
    )
    dependency_inconclusive = any(
        is_enum_value(
            edge.get("effective_status"), {"conditional", "unclear", "unchecked"}
        )
        for edge in dependency_edges
    )
    has_defect = any(
        is_enum_value(status, {"gap", "incorrect"})
        for status in unit_statuses.values()
    ) or any(
        issue.get("finding_status") == "defect" for issue in open_load_bearing
    ) or interface_defect or dependency_defect or global_consistency_result.get(
        "defect", False
    ) or cross_reference_result.get("defect", False)
    has_inconclusive = any(
        is_enum_value(status, {"conditionally_verified", "unclear", "not_checked"})
        for status in unit_statuses.values()
    ) or any(
        issue.get("finding_status") == "inconclusive"
        for issue in open_load_bearing
    ) or interface_inconclusive or dependency_inconclusive or bool(
        global_consistency_result.get("inconclusive", False)
    ) or cross_reference_result.get("inconclusive", False) or parser_inconclusive
    derived_assessment = (
        "defects_found"
        if has_defect
        else "inconclusive"
        if has_inconclusive
        else "no_defect_found"
    )
    if is_enum_value(
        assessment, {"no_defect_found", "defects_found", "inconclusive"}
    ):
        if assessment != derived_assessment:
            errors.append(
                f"overall_assessment {assessment} contradicts the evidence; "
                f"expected {derived_assessment}"
            )

    if assessment == "no_defect_found":
        for unit_id, summary in summaries_by_id.items():
            if unit_id not in in_scope:
                continue
            components = summary.get("review_components", {})
            if components.get("statement_status") != "established":
                errors.append(f"{unit_id}: statement is not established")
            if not is_enum_value(
                components.get("use_site_sufficiency"),
                {"sufficient", "not_applicable"},
            ):
                errors.append(f"{unit_id}: use-site sufficiency is not established")

    result = {
        "audit_root": str(root),
        "schema_version": SCHEMA_VERSION,
        "assessment": assessment,
        "derived_assessment": derived_assessment,
        "source_files": len(recorded_files),
        "parser_warnings": len(fresh_warning_set),
        "inventory_units": len(unit_inventory),
        "target_units": len(target_units),
        "in_scope_units": len(in_scope),
        "ledgers": len(summaries),
        "external_results": len(external_results),
        "method_interfaces": len(interfaces),
        "issue_log": str(issue_path),
        "issues": len(issues),
        "errors": len(errors),
        "assurance_boundary": (
            "Non-formal audit only. Success means the required evidence and closure "
            "gates passed; it is not a kernel-checked proof certificate."
        ),
    }
    return errors, result


def finalization_payload_sha256(record: dict[str, Any]) -> str:
    payload = dict(record)
    payload.pop("record_payload_sha256", None)
    return canonical_sha256(payload)



def cmd_finalize(args: argparse.Namespace) -> int:
    root = args.root.resolve()
    errors, result = check_audit_finalization(root)
    manifest, manifest_errors = load_json_object(root / "AUDIT_MANIFEST.json", "audit manifest")
    record_path, record_path_errors = finalization_record_path(manifest, root)
    if not finalization_target_is_safe(record_path):
        raise ValueError(
            "Refusing to write through a symlinked finalization-record location"
        )
    if not manifest_errors:
        for error in record_path_errors:
            if error not in errors:
                errors.append(error)
    source_snapshot = manifest.get("source_snapshot") if not manifest_errors else None
    artifact_manifest = audit_state_manifest(root, record_path)
    record = {
        "finalization_schema_version": 1,
        "status": "passed" if not errors else "failed",
        "generated_utc": utc_now(),
        "protocol": protocol_identity(),
        "source_snapshot_sha256": (
            source_snapshot.get("sha256")
            if isinstance(source_snapshot, dict)
            else None
        ),
        "artifact_manifest": artifact_manifest,
        "audit_state_sha256": canonical_sha256(artifact_manifest),
        "errors": errors,
    }
    record["record_payload_sha256"] = finalization_payload_sha256(record)
    record_path.parent.mkdir(parents=True, exist_ok=True)
    record_path.write_text(
        json.dumps(record, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    result["finalization_record"] = str(record_path)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    return 0


def artifact_manifest_changes(
    recorded: Any, current: list[dict[str, str]]
) -> tuple[list[str], dict[str, list[str]]]:
    changes = {"added": [], "removed": [], "changed": []}
    if recorded is None:
        return [], changes
    if not isinstance(recorded, list):
        return ["FINALIZATION.json artifact_manifest must be a list"], changes
    recorded_map: dict[str, str] = {}
    errors: list[str] = []
    for index, row in enumerate(recorded, 1):
        prefix = f"FINALIZATION.json artifact_manifest[{index}]"
        if not isinstance(row, dict):
            errors.append(f"{prefix} must be an object")
            continue
        file_value = row.get("file")
        digest = row.get("sha256")
        if not is_nonempty_string(file_value) or not is_nonempty_string(digest):
            errors.append(f"{prefix} needs nonempty file and sha256 values")
            continue
        if file_value in recorded_map:
            errors.append(f"Duplicate finalization artifact: {file_value}")
        recorded_map[file_value] = digest
    current_map = {row["file"]: row["sha256"] for row in current}
    changes["added"] = sorted(set(current_map) - set(recorded_map))
    changes["removed"] = sorted(set(recorded_map) - set(current_map))
    changes["changed"] = sorted(
        path
        for path in set(recorded_map) & set(current_map)
        if recorded_map[path] != current_map[path]
    )
    return errors, changes


def check_finalization_freshness(root: Path) -> dict[str, Any]:
    root = root.resolve()
    gate_errors, _ = check_audit_finalization(root)
    result: dict[str, Any] = {
        "record_status": "missing",
        "freshness": "not_applicable",
        "usable_finalization": False,
        "preflight_status": "failed" if gate_errors else "passed",
        "finalizable_now": not gate_errors,
        "record": None,
        "stale_reasons": [],
        "current_gate_errors": gate_errors,
        "artifact_changes": {"added": [], "removed": [], "changed": []},
    }
    manifest, manifest_errors = load_json_object(
        root / "AUDIT_MANIFEST.json", "audit manifest"
    )
    if manifest_errors:
        result["record_status"] = "invalid"
        result["freshness"] = "unknown"
        result["stale_reasons"] = manifest_errors
        return result
    record_path, record_path_errors = finalization_record_path(manifest, root)
    if record_path_errors:
        result["record_status"] = "invalid"
        result["freshness"] = "unknown"
        result["stale_reasons"] = record_path_errors
        return result
    result["record"] = str(record_path)
    if not record_path.is_file():
        return result

    record, record_errors = load_json_object(record_path, "finalization record")
    if record_errors:
        result["record_status"] = "invalid"
        result["freshness"] = "unknown"
        result["stale_reasons"] = record_errors
        return result
    status = record.get("status")
    if not is_enum_value(status, {"passed", "failed"}):
        result["record_status"] = "invalid"
        result["freshness"] = "unknown"
        result["stale_reasons"] = [
            "FINALIZATION.json status must be passed or failed"
        ]
        return result
    record_schema = record.get("finalization_schema_version")
    if record_schema is not None and not (type(record_schema) is int and record_schema == 1):
        result["record_status"] = "invalid"
        result["freshness"] = "unknown"
        result["stale_reasons"] = [
            "FINALIZATION.json has an unsupported finalization_schema_version"
        ]
        return result
    if type(record_schema) is int and record_schema == 1:
        schema_errors: list[str] = []
        generated_utc = record.get("generated_utc")
        if not is_nonempty_string(generated_utc):
            schema_errors.append(
                "Schema 1 FINALIZATION.json requires generated_utc"
            )
        else:
            try:
                generated_time = datetime.fromisoformat(generated_utc)
            except ValueError:
                schema_errors.append(
                    "Schema 1 FINALIZATION.json generated_utc must be ISO 8601"
                )
            else:
                if generated_time.tzinfo is None:
                    schema_errors.append(
                        "Schema 1 FINALIZATION.json generated_utc needs a timezone"
                    )
        if not isinstance(record.get("artifact_manifest"), list):
            schema_errors.append(
                "Schema 1 FINALIZATION.json requires an artifact_manifest list"
            )
        if not is_nonempty_string(record.get("record_payload_sha256")):
            schema_errors.append(
                "Schema 1 FINALIZATION.json requires record_payload_sha256"
            )
        if schema_errors:
            result["record_status"] = "invalid"
            result["freshness"] = "unknown"
            result["stale_reasons"] = schema_errors
            return result
    result["record_status"] = status
    reasons: list[str] = []

    payload_digest = record.get("record_payload_sha256")
    if payload_digest is not None and (
        not is_nonempty_string(payload_digest)
        or payload_digest != finalization_payload_sha256(record)
    ):
        reasons.append("Finalization record payload hash does not match")

    current_artifacts = audit_state_manifest(root, record_path)
    current_state_digest = canonical_sha256(current_artifacts)
    if record.get("audit_state_sha256") != current_state_digest:
        reasons.append("Audit artifacts changed after finalization")
    artifact_errors, changes = artifact_manifest_changes(
        record.get("artifact_manifest"), current_artifacts
    )
    reasons.extend(artifact_errors)
    result["artifact_changes"] = changes

    if record.get("protocol") != protocol_identity():
        reasons.append("Finalization protocol does not match the current validator")
    snapshot = manifest.get("source_snapshot")
    manifest_snapshot = snapshot.get("sha256") if isinstance(snapshot, dict) else None
    if record.get("source_snapshot_sha256") != manifest_snapshot:
        reasons.append("Finalization source snapshot does not match the manifest")

    recorded_errors = record.get("errors")
    if not isinstance(recorded_errors, list):
        reasons.append("FINALIZATION.json errors must be a list")
    elif recorded_errors != gate_errors:
        reasons.append("Current finalization-gate result differs from the recorded result")
    if status == "passed" and gate_errors:
        reasons.append("A passed finalization record no longer passes the full gate")

    result["stale_reasons"] = list(dict.fromkeys(reasons))
    result["freshness"] = "stale" if result["stale_reasons"] else "current"
    result["usable_finalization"] = (
        status == "passed"
        and result["freshness"] == "current"
        and not gate_errors
    )
    return result


def status_markdown(data: dict[str, Any]) -> str:
    finalization = data["finalization"]
    rows = [
        "# Proof-Check Status",
        "",
        f"- Audit root: `{data['audit_root']}`",
        f"- Ledgers: {data['ledgers']}",
        f"- Ledger validation errors: {data['ledger_errors']}",
        f"- Issues: {data['issues']}",
        f"- Finalization record status: {finalization['record_status']}",
        f"- Finalization freshness: {finalization['freshness']}",
        f"- Usable finalization: {str(finalization['usable_finalization']).lower()}",
        f"- Preflight status: {finalization['preflight_status']}",
        f"- Finalizable now: {str(finalization['finalizable_now']).lower()}",
        "",
        "## Unit statuses",
        "",
        "| Status | Count |",
        "|---|---|",
    ]
    rows.extend(
        f"| {status} | {count} |"
        for status, count in sorted(data["unit_statuses"].items())
    )
    rows.append("")
    if data["invalid_ledgers"]:
        rows.extend(["## Invalid ledgers", ""])
        rows.extend(f"- `{path}`" for path in data["invalid_ledgers"])
        rows.append("")
    if finalization["stale_reasons"]:
        rows.extend(["## Finalization problems", ""])
        rows.extend(f"- {reason}" for reason in finalization["stale_reasons"])
        rows.append("")
    if finalization["current_gate_errors"]:
        rows.extend(["## Current finalization-gate errors", ""])
        rows.extend(f"- {error}" for error in finalization["current_gate_errors"])
        rows.append("")
    changes = finalization["artifact_changes"]
    if any(changes.values()):
        rows.extend(["## Changed audit artifacts", ""])
        for kind in ("added", "removed", "changed"):
            for path in changes[kind]:
                rows.append(f"- {kind}: `{path}`")
        rows.append("")
    return "\n".join(rows)


def cmd_status(args: argparse.Namespace) -> int:
    root = args.root.resolve()
    errors, summaries, _ = audit_ledgers(root, False)
    _, issues, issue_read_errors = load_issue_log(root)
    finalization = check_finalization_freshness(root)
    output = getattr(args, "output", None)
    if (
        output is not None
        and finalization["record_status"] != "missing"
        and output.resolve().is_relative_to(root)
    ):
        raise ValueError(
            "Refusing to write status output inside an audit root that has "
            "a finalization record"
        )
    counts = Counter(
        summary.get("expected_unit_status", "unknown") for summary in summaries
    )
    invalid = [summary["ledger"] for summary in summaries if summary.get("errors")]
    result = {
        "audit_root": str(root),
        "ledgers": len(summaries),
        "ledger_errors": len(errors),
        "invalid_ledgers": invalid,
        "unit_statuses": dict(counts),
        "issues": len(issues),
        "issue_log_errors": len(issue_read_errors),
        "finalization": finalization,
    }
    text = (
        status_markdown(result)
        if getattr(args, "format", "json") == "markdown"
        else json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    )
    write_or_print(text, output, getattr(args, "force", False))
    finalization_failed = (
        finalization["record_status"] in {"failed", "invalid"}
        or finalization["freshness"] in {"stale", "unknown"}
        or (
            finalization["record_status"] != "missing"
            and bool(finalization["current_gate_errors"])
        )
    )
    return 1 if errors or issue_read_errors or finalization_failed else 0


def add_output_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--format", choices=("json", "markdown"), default="json")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--force", action="store_true", help="Replace an existing output file")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Deterministic support for source-locked statistical proof audits"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    scaffold = subparsers.add_parser("scaffold", help="Create a new audit workspace")
    scaffold.add_argument("--paper", type=Path, required=True)
    scaffold.add_argument("--output", type=Path, required=True)
    scaffold.add_argument(
        "--additional-source",
        action="append",
        nargs=3,
        metavar=("PATH", "REASON", "EVIDENCE"),
        help=(
            "Add a load-bearing source file with its inclusion reason and evidence; "
            "repeat for multiple files"
        ),
    )
    scaffold.add_argument(
        "--fls",
        type=Path,
        help="Use an existing TeX recorder file for supplemental project-local discovery",
    )
    scaffold.add_argument(
        "--project-root",
        type=Path,
        help=(
            "Project boundary and fallback root for local source discovery; "
            "defaults to the paper directory"
        ),
    )
    scaffold.set_defaults(func=cmd_scaffold)
    index = subparsers.add_parser("index", help="Index formal LaTeX proof units")
    index.add_argument("--file", type=Path, required=True)
    add_output_arguments(index)
    index.set_defaults(func=cmd_index)

    crossref = subparsers.add_parser("crossref", help="Audit LaTeX labels and references")
    crossref.add_argument("--file", type=Path, required=True)
    add_output_arguments(crossref)
    crossref.set_defaults(func=cmd_crossref)

    extract = subparsers.add_parser(
        "extract", help="Create a source-locked line ledger for one proof unit"
    )
    extract.add_argument("--file", type=Path, required=True)
    extract.add_argument("--start", type=int, required=True)
    extract.add_argument("--end", type=int, required=True)
    extract.add_argument("--statement-start", type=int)
    extract.add_argument("--statement-end", type=int)
    extract.add_argument("--statement-file", type=Path)
    extract.add_argument("--separate-statement-reason")
    extract.add_argument("--unit-id", required=True)
    extract.add_argument("--output", type=Path, required=True)
    extract.add_argument("--force", action="store_true")
    extract.set_defaults(func=cmd_extract)

    ledger = subparsers.add_parser(
        "ledger-check", help="Validate source coverage and proof-step evidence"
    )
    ledger.add_argument("ledger", type=Path)
    ledger.add_argument("--final", action="store_true")
    ledger.set_defaults(func=cmd_ledger_check)

    issues = subparsers.add_parser(
        "issues", help="Reconcile canonical issues with proof-unit ledgers"
    )
    issues.add_argument("--root", type=Path, required=True)
    issues.add_argument("--write-summary", action="store_true")
    issues.add_argument("--final", action="store_true")
    issues.set_defaults(func=cmd_issues)

    finalize = subparsers.add_parser(
        "finalize",
        help="Enforce audit scope, source, dependency, issue, and challenger closure",
    )
    finalize.add_argument("--root", type=Path, required=True)
    finalize.set_defaults(func=cmd_finalize)

    status = subparsers.add_parser("status", help="Summarize resumable audit state")
    status.add_argument("--root", type=Path, required=True)
    add_output_arguments(status)
    status.set_defaults(func=cmd_status)
    return parser


def main() -> int:
    configure_console_errors()
    parser = build_parser()
    args = parser.parse_args()
    try:
        return int(args.func(args))
    except (FileExistsError, FileNotFoundError, ValueError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
