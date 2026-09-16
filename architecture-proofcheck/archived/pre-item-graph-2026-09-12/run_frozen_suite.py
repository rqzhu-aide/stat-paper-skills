"""Small unittest runner with distinct logs and before/after source identities.

The September 4 runner and receipts remain under followup-audit unchanged.
Use --test MODULE[.CLASS[.METHOD]] for focused checks; omit it for discovery.
Receipts assume reviewed code and a trusted process, not an adversarial author.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
import unittest
import uuid

RUNNER = Path(__file__).resolve()
REPO = RUNNER.parent.parent


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_json(path: Path, value) -> None:
    with path.open('x', encoding='utf-8', newline='\n') as handle:
        json.dump(value, handle, indent=2, ensure_ascii=False)
        handle.write('\n')


def snapshot(root: Path) -> list[dict]:
    return [{'path': path.relative_to(root).as_posix(), 'sha256': digest(path.read_bytes())}
            for path in sorted(root.rglob('*'))
            if path.is_file() and '__pycache__' not in path.parts and path.suffix != '.pyc']


class Outcomes(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.passed = []

    def addSuccess(self, test):
        super().addSuccess(test)
        self.passed.append(test.id())


def child(args) -> int:
    sys.path.insert(0, str(args.skill_root / 'tests'))
    loader = unittest.TestLoader()
    suite = (loader.loadTestsFromNames(args.test) if args.test else
             loader.discover(str(args.skill_root / 'tests'), pattern=args.pattern))
    started = time.perf_counter()
    result = unittest.TextTestRunner(stream=sys.stdout, verbosity=2, resultclass=Outcomes).run(suite)
    outcomes = {
        'tests': result.testsRun, 'passed': len(result.passed),
        'failures': len(result.failures), 'errors': len(result.errors),
        'skipped': len(result.skipped), 'expected_failures': len(result.expectedFailures),
        'unexpected_successes': len(result.unexpectedSuccesses),
        'unittest_seconds': time.perf_counter() - started,
        'skip_reasons': [{'test': test.id(), 'reason': reason} for test, reason in result.skipped],
        'expected_failure_tests': [test.id() for test, _ in result.expectedFailures],
        'unexpected_success_tests': [test.id() for test in result.unexpectedSuccesses],
    }
    write_json(args.result_json, outcomes)
    return 0 if result.wasSuccessful() and result.testsRun else 1


def main() -> int:
    # Redirected Windows output may default to a legacy code page. A failed
    # assertion containing manuscript mathematics must still reach the log
    # and outcome receipt instead of crashing unittest's error printer.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="backslashreplace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skill-root', type=Path, default=REPO / 'stat-paper-proofcheck')
    parser.add_argument('--output-root', type=Path, default=RUNNER.parent / 'implementation-runs')
    parser.add_argument('--pattern', default='test_*.py')
    parser.add_argument('--test', action='append', default=[])
    parser.add_argument('--child', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('--result-json', type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args()
    args.skill_root = args.skill_root.resolve()
    if args.child:
        return child(args)
    if not (args.skill_root / 'tests').is_dir():
        parser.error('--skill-root must contain the skill tests')
    started = datetime.now(timezone.utc)
    output = args.output_root.resolve() / (started.strftime('%Y%m%dT%H%M%SZ-') + uuid.uuid4().hex[:8])
    output.mkdir(parents=True, exist_ok=False)
    before = snapshot(args.skill_root)
    runner_before = digest(RUNNER.read_bytes())
    write_json(output / 'snapshot-before.json', before)
    command = [sys.executable, '-B', str(RUNNER), '--child', '--skill-root', str(args.skill_root),
               '--pattern', args.pattern, '--result-json', str(output / 'outcomes.json')]
    for selector in args.test:
        command.extend(['--test', selector])
    timer = time.perf_counter()
    log = output / 'tests.log'
    with log.open('x', encoding='utf-8') as handle:
        process = subprocess.run(command, cwd=args.skill_root.parent, stdout=handle, stderr=subprocess.STDOUT)
    elapsed = time.perf_counter() - timer
    after = snapshot(args.skill_root)
    runner_after = digest(RUNNER.read_bytes())
    write_json(output / 'snapshot-after.json', after)
    outcome_path = output / 'outcomes.json'
    outcomes = json.loads(outcome_path.read_text(encoding='utf-8')) if outcome_path.is_file() else None
    unchanged = before == after and runner_before == runner_after
    clean = bool(outcomes and outcomes['tests'] and not any(outcomes[key] for key in (
        'failures', 'errors', 'expected_failures', 'unexpected_successes')))
    exit_code = process.returncode or (0 if unchanged and clean else 1)
    receipt = {
        'started_utc': started.isoformat(), 'finished_utc': datetime.now(timezone.utc).isoformat(),
        'command': command, 'cwd': str(args.skill_root.parent), 'skill_root': str(args.skill_root),
        'selector': args.test or {'discover_pattern': args.pattern},
        'runtime': {'executable': sys.executable, 'version': sys.version},
        'exit_code': exit_code, 'test_exit_code': process.returncode, 'elapsed_seconds': elapsed,
        'outcomes': outcomes, 'clean_outcomes': clean, 'skill_tree_unchanged': before == after,
        'runner_unchanged': runner_before == runner_after,
        'runner_sha256': runner_before, 'runner_after_sha256': runner_after,
        'snapshot_before_sha256': digest((output / 'snapshot-before.json').read_bytes()),
        'snapshot_after_sha256': digest((output / 'snapshot-after.json').read_bytes()),
        'outcomes_sha256': digest(outcome_path.read_bytes()) if outcomes else None,
        'log_sha256': digest(log.read_bytes()),
    }
    write_json(output / 'receipt.json', receipt)
    print(json.dumps({'receipt': str(output / 'receipt.json'), **receipt}, indent=2))
    return exit_code


if __name__ == '__main__':
    raise SystemExit(main())
