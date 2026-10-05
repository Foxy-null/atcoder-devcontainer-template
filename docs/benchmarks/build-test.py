#!/usr/bin/env python3
"""Read-only build investigation: temporary sources/outputs, three warm samples.

Normal use (inside the repository's pinned dev container):
  python3 build-test.py --output /tmp/atcoder-build-results.json
Supplemental use only (other compiler, no official extra link libraries):
  python3 build-test.py --fallback --acl /path/to/ac-library --output /tmp/results.json

Use docker run --rm --cpus=2 --memory=4g outside this script for resource limits.
This script does not modify solutions, build tasks, configuration, or caches.
It only compiles synthetic programs in a TemporaryDirectory and runs local samples.
"""
import argparse
import hashlib
import json
import os
import platform
from pathlib import Path
import resource
import shutil
import statistics
import subprocess
import tempfile
import time

TEMPLATE = """#include <atcoder/all>
#include <bits/stdc++.h>
using namespace std;
#define int long long
void testcase() {}
int32_t main() {
  ios::sync_with_stdio(false);
  cin.tie(0);
  cout.tie(0);
  testcase();
  return 0;
}
"""
BODY = r"""int main() {
  std::ios::sync_with_stdio(false);
  std::cin.tie(nullptr);
  int n, q;
  if (!(std::cin >> n >> q)) return 0;
  atcoder::fenwick_tree<long long> fw(n);
  for (int i = 0; i < n; ++i) {
    long long a; std::cin >> a; fw.add(i, a);
  }
  for (int i = 0; i < q; ++i) {
    int t, a; long long b;
    std::cin >> t >> a >> b;
    if (t == 0) fw.add(a, b);
    else std::cout << fw.sum(a, static_cast<int>(b)) << '\n';
  }
}
"""
FULL_HEADERS = '#include <atcoder/all>\n#include <bits/stdc++.h>\n'
TRIM_HEADERS = '#include <iostream>\n#include <atcoder/fenwicktree>\n'
SAMPLES = [
    ('5 5\n1 2 3 4 5\n1 0 5\n0 2 10\n1 1 4\n1 2 3\n1 0 0\n', '15\n19\n13\n0\n'),
    ('1 3\n9\n1 0 1\n0 0 -2\n1 0 1\n', '9\n7\n'),
    ('3 1\n0 0 0\n1 0 3\n', '0\n'),
]


def capture(command):
    try:
        p = subprocess.run(command, text=True, stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT, timeout=30)
        return {'command': command, 'exit_code': p.returncode, 'output': p.stdout}
    except (OSError, subprocess.TimeoutExpired) as e:
        return {'command': command, 'error': str(e)}


def flags_array(path, name):
    p = subprocess.run(['bash', '-c', 'source "$1"; printf "%s\\0" "${' + name + '[@]}"',
                        '--', str(path)], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       check=True)
    return [v.decode() for v in p.stdout.split(b'\0') if v]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--repeats', type=int, default=3)
    parser.add_argument('--fallback', action='store_true')
    parser.add_argument('--acl', type=Path)
    args = parser.parse_args()
    if args.repeats < 3:
        parser.error('Use at least three measurements per case.')
    notes = ['Each case has one unreported warmup and then repeated wall-time samples.',
             'Absolute times depend on CPU/storage/virtualization and source complexity.',
             'The script runs synthetic local samples; this is not a user solution benchmark.']
    official_flags = Path('/opt/atcoder/gcc/share/atcoder/flags.sh')
    if args.fallback:
        if not args.acl or not (args.acl / 'atcoder/all').is_file():
            parser.error('--fallback requires --acl pointing to an AC Library root.')
        compiler = shutil.which('g++')
        wrapper = None
        compile_flags = ['-DATCODER', '-DNOMINMAX', '-DONLINE_JUDGE', '-DOR_PROTO_DLL=',
                         '-DPROTOBUF_USE_DLLS', '-DUSE_BOP', '-DUSE_CBC', '-DUSE_CLP',
                         '-DUSE_GLOP', '-DUSE_LP_PARSER', '-DUSE_MATH_OPT', '-DUSE_PDLP',
                         '-DUSE_SCIP', '-I' + str(args.acl.resolve()), '-O2', '-Wall', '-Wextra',
                         '-fconstexpr-depth=1024', '-fconstexpr-loop-limit=524288',
                         '-fconstexpr-ops-limit=2097152', '-ftrivial-auto-var-init=zero',
                         '-march=native', '-pthread', '-std=gnu++23', '-Wl,--as-needed', '-fopenmp']
        link_flags = []
        notes += ['SUPPLEMENTAL FALLBACK: compiler/architecture differ from the pinned image.',
                  'Official external libraries/link search paths and -fmodules are absent.',
                  'Full-library linker performance and pinned GCC 15.2 behavior are NOT measured.']
    else:
        compiler = '/opt/atcoder/gcc/bin/g++'
        wrapper = shutil.which('atcoder-g++')
        if not official_flags.is_file() or not wrapper or not Path(compiler).is_file():
            parser.error('Run in the pinned dev container, or explicitly use --fallback.')
        compile_flags = flags_array(official_flags, 'COMPILE_FLAGS')
        link_flags = flags_array(official_flags, 'LINK_FLAGS')
    lld = shutil.which('ld.lld')
    oj = shutil.which('oj')
    environment = {
        'fallback': args.fallback, 'platform': platform.platform(),
        'architecture': platform.machine(), 'logical_cpus': os.cpu_count(),
        'cpu_affinity': sorted(os.sched_getaffinity(0)) if hasattr(os, 'sched_getaffinity') else None,
        'compiler': capture([compiler, '--version']),
        'linker_bfd': capture([shutil.which('ld.bfd') or 'ld', '--version']),
        'address_space_limit_bytes': resource.getrlimit(resource.RLIMIT_AS),
        'linker_lld': capture([lld, '--version']) if lld else {'unavailable': True},
        'oj': capture([oj, '--version']) if oj else {'unavailable': True},
        'compile_flags': compile_flags, 'link_flags': link_flags,
        'extra_library_count': len(link_flags),
        'flags_sha256': hashlib.sha256(official_flags.read_bytes()).hexdigest()
                       if official_flags.is_file() and not args.fallback else None,
        'cpuinfo_excerpt': Path('/proc/cpuinfo').read_text()[:2500],
    }
    for filename in ('cpu.max', 'memory.max'):
        path = Path('/sys/fs/cgroup') / filename
        environment[filename] = path.read_text().strip() if path.is_file() else None
    report = {'environment': environment, 'notes': notes, 'repeats': args.repeats,
              'sources': {'template': TEMPLATE, 'full': FULL_HEADERS + BODY,
                          'trimmed': TRIM_HEADERS + BODY}, 'results': {}}
    # GCC 15 cannot consume a traditional PCH while modules are enabled.
    pch_extra = ['-fno-modules'] if any(
        flag in compile_flags for flag in ('-fmodules', '-fmodules-ts')) else []
    report['PCH_extra_flags'] = pch_extra
    if pch_extra:
        notes.append('PCH cases disable modules for both creation and use; '
                     'plain no-modules cases isolate this configuration change.')
    args.output.parent.mkdir(parents=True, exist_ok=True)

    def save():
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')

    with tempfile.TemporaryDirectory(prefix='atcoder-build-benchmark-') as directory:
        work = Path(directory)
        template = work / 'template.cpp'
        full = work / 'full.cpp'
        trimmed = work / 'trimmed.cpp'
        pch_body = work / 'pch-body.cpp'
        pch_header = work / 'common.hpp'
        binary = work / 'answer'
        obj = work / 'answer.o'
        template.write_text(TEMPLATE)
        full.write_text(FULL_HEADERS + BODY)
        trimmed.write_text(TRIM_HEADERS + BODY)
        pch_body.write_text(BODY)
        pch_header.write_text(FULL_HEADERS)
        tests = work / 'test'
        tests.mkdir()
        for i, (input_text, output_text) in enumerate(SAMPLES, start=1):
            (tests / f'sample-{i}.in').write_text(input_text)
            (tests / f'sample-{i}.out').write_text(output_text)
        report['temporary_directory'] = str(work)

        def command(source=full, extra=(), libs=None, compile_only=False):
            flags = compile_flags + list(extra)
            if compile_only:
                return [compiler] + flags + ['-c', str(source), '-o', str(obj)]
            return [compiler] + flags + [str(source), '-o', str(binary)] + (
                link_flags if libs is None else libs)

        def run_one(commands):
            elapsed, user, system = 0.0, 0.0, 0.0
            outputs = []
            for cmd in commands:
                before = resource.getrusage(resource.RUSAGE_CHILDREN)
                start = time.perf_counter()
                try:
                    p = subprocess.run(cmd, cwd=work, text=True, stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT, timeout=180)
                except (OSError, subprocess.TimeoutExpired) as e:
                    return {'error': str(e), 'wall_s': time.perf_counter() - start,
                            'outputs': outputs, 'failed_command': cmd}
                elapsed += time.perf_counter() - start
                after = resource.getrusage(resource.RUSAGE_CHILDREN)
                user += after.ru_utime - before.ru_utime
                system += after.ru_stime - before.ru_stime
                outputs.append({'command': cmd, 'exit_code': p.returncode,
                                'output': p.stdout[-12000:]})
                if p.returncode:
                    return {'wall_s': elapsed, 'outputs': outputs, 'exit_code': p.returncode}
            return {'wall_s': elapsed, 'user_s': user, 'system_s': system,
                    'exit_code': 0, 'outputs': outputs}

        def measure(name, commands):
            warmup = run_one(commands)
            runs = [run_one(commands) for _ in range(args.repeats)] if warmup.get('exit_code') == 0 else []
            good = [r['wall_s'] for r in runs if r.get('exit_code') == 0]
            report['results'][name] = {
                'warmup': warmup, 'runs': runs,
                'median_wall_s': statistics.median(good) if len(good) == args.repeats else None,
            }
            print(name + ': ' + str(report['results'][name]['median_wall_s']), flush=True)
            save()

        baseline = [wrapper, str(full), '-o', str(binary)] if wrapper else command()
        measure('template_full_O2', [command(template)])
        measure('answer_full_O2', [baseline])
        measure('answer_trimmed_header_O2', [command(trimmed)])
        if lld:
            measure('answer_full_lld_O2', [command(extra=['-fuse-ld=lld'])])
        measure('answer_full_O0', [command(extra=['-O0'])])
        measure('answer_full_O1', [command(extra=['-O1'])])
        measure('compile_only_full_O2', [command(compile_only=True)])
        measure('compile_only_trimmed_header_O2', [command(trimmed, compile_only=True)])
        # Same full-header object for every linker case; compile/setup is outside the timing.
        setup = run_one([command(compile_only=True)])
        report['linker_object_setup'] = setup
        if setup.get('exit_code') == 0:
            measure('link_only_full_BFD', [command(obj, extra=['-fuse-ld=bfd'])])
            measure('link_only_ordinary_libraries_BFD', [command(obj, extra=['-fuse-ld=bfd'], libs=[])])
            if lld:
                measure('link_only_full_lld', [command(obj, extra=['-fuse-ld=lld'])])
                measure('link_only_ordinary_libraries_lld', [command(obj, extra=['-fuse-ld=lld'], libs=[])])
            else:
                report['results']['link_only_full_lld'] = {'skipped': 'ld.lld not installed'}
        measure('answer_full_ordinary_libraries_O2', [command(libs=[])])
        if pch_extra:
            measure('answer_full_no_modules_O2', [command(extra=pch_extra)])
        pch_command = [compiler] + compile_flags + pch_extra + ['-x', 'c++-header', '-c', str(pch_header),
                                                    '-o', str(pch_header) + '.gch']
        measure('PCH_create_O2', [pch_command])
        report['PCH_file_size_bytes'] = Path(str(pch_header) + '.gch').stat().st_size if Path(str(pch_header) + '.gch').is_file() else None
        pch_options = pch_extra + ['-include', str(pch_header), '-Werror=invalid-pch']
        verification = run_one([command(pch_body, extra=pch_options + ['-H'], compile_only=True)])
        report['PCH_verification'] = verification
        pch_used = verification.get('exit_code') == 0 and any(
            line.lstrip().startswith('!') and '.gch' in line
            for output in verification.get('outputs', [])
            for line in output['output'].splitlines())
        report['PCH_used'] = pch_used
        if pch_used:
            measure('answer_PCH_O2', [command(pch_body, extra=pch_options)])
            measure('compile_only_PCH_O2', [command(pch_body, extra=pch_options, compile_only=True)])
        else:
            report['results']['answer_PCH_O2'] = {'skipped': 'A usable .gch was not confirmed by -H'}
        setup = run_one([baseline])
        report['oj_binary_setup'] = setup
        if oj and setup.get('exit_code') == 0:
            test_command = [oj, 'test', '-c', str(binary), '-t', '2', '-d', str(tests)]
            measure('oj_startup_help', [[oj, 'test', '--help']])
            measure('oj_test_three_samples', [test_command])
            measure('build_and_test_full_O2', [baseline, test_command])
            if lld:
                measure('build_and_test_full_lld_O2', [command(extra=['-fuse-ld=lld']), test_command])
            measure('build_and_test_trimmed_header_O2', [command(trimmed), test_command])
            if pch_extra:
                measure('build_and_test_full_no_modules_O2', [command(extra=pch_extra), test_command])
            if pch_used:
                measure('build_and_test_PCH_O2', [command(pch_body, extra=pch_options), test_command])
        else:
            report['results']['oj_test_three_samples'] = {'skipped': 'oj unavailable or baseline failed'}
        save()
    print('JSON: ' + str(args.output.resolve()), flush=True)


if __name__ == '__main__':
    main()
