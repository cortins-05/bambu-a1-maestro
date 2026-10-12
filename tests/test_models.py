import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch

import trimesh

ROOT = Path(__file__).resolve().parents[1]


class GeometryTests(unittest.TestCase):
    def run_analysis(self, *args):
        return subprocess.run([sys.executable, str(ROOT / 'scripts/analyze_models.py'), *map(str, args)],
                              capture_output=True, text=True, encoding='utf-8', timeout=120)

    def test_same_name_models_generate_distinct_artifacts_and_preserve_originals(self):
        with tempfile.TemporaryDirectory(prefix='bambu geometry ') as tmp:
            base = Path(tmp)
            models = []
            for name, dimensions in [('a', [20, 10, 5]), ('b', [30, 15, 8])]:
                folder = base / name
                folder.mkdir()
                path = folder / 'piece.stl'
                trimesh.creation.box(extents=dimensions).export(path)
                models.append(path)
            hashes = [hashlib.sha256(p.read_bytes()).hexdigest() for p in models]
            out = base / 'custom-output'
            result = self.run_analysis(base, '--top', 1, '--out', out)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            reports = json.loads((out / 'report.json').read_text(encoding='utf-8'))
            self.assertEqual(len(reports), 2)
            self.assertNotEqual(reports[0]['views_png'], reports[1]['views_png'])
            for report in reports:
                self.assertTrue(report['watertight'])
                self.assertTrue(report['orientations'][0]['fits_A1'])
                self.assertGreater((out / report['views_png']).stat().st_size, 1000)
                oriented = trimesh.load(report['orientations'][0]['oriented_stl'])
                self.assertAlmostEqual(oriented.bounds[0, 2], 0, places=5)
            self.assertEqual(hashes, [hashlib.sha256(p.read_bytes()).hexdigest() for p in models])
            # A repeated directory scan must not treat generated STLs as new input.
            second = self.run_analysis(base, '--top', 1, '--out', out)
            self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
            self.assertEqual(len(json.loads((out / 'report.json').read_text(encoding='utf-8'))), 2)

    def test_bad_model_returns_failure_with_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'broken.stl'
            path.write_text('not a mesh', encoding='utf-8')
            result = self.run_analysis(path)
            self.assertNotEqual(result.returncode, 0)
            reports = json.loads((Path(tmp) / '_analisis_a1/report.json').read_text(encoding='utf-8'))
            self.assertIn('error', reports[0])

    def test_invalid_threshold_rejected(self):
        result = self.run_analysis('missing.stl', '--threshold', 95)
        self.assertEqual(result.returncode, 2)


class SlicerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location('bambu_slice', ROOT / 'scripts/bambu_slice.py')
        cls.slicer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.slicer)

    def test_exact_profile_of_other_machine_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            for kind in ('machine', 'process', 'filament'):
                (base / kind).mkdir()
            for name in ('0.20mm Standard @BBL A1', '0.20mm Standard @BBL A1 mini', '0.20mm Standard @BBL X1C'):
                (base / 'process' / (name + '.json')).write_text(json.dumps({'name': name}), encoding='utf-8')
            profiles = self.slicer.Profiles(str(base))
            self.assertEqual(profiles.pick('process', '0.20mm Standard', '0.4'), '0.20mm Standard @BBL A1')
            with self.assertRaises(SystemExit):
                profiles.pick('process', '0.20mm Standard @BBL X1C', '0.4')

    def test_gcode_measurements_and_effective_overrides(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'plate.gcode'
            path.write_text('; model printing time: 1m 2s; total estimated time: 7m 2s\n'
                            '; total layer number: 25\n; total filament weight [g] : 2.50\n'
                            '; CONFIG_BLOCK_START\n; wall_loops = 3\n; CONFIG_BLOCK_END\n', encoding='utf-8')
            self.assertEqual(self.slicer.parse_gcode(path)['total_time'], '7m 2s')
            self.assertEqual(self.slicer.read_gcode_config(path)['wall_loops'], '3')

    def test_failed_slice_and_override_mismatch_never_report_success(self):
        for return_code, effective, expected_exit in [(1, '3', 1), (0, '2', 2), (0, '3', 0)]:
            with self.subTest(return_code=return_code, effective=effective), tempfile.TemporaryDirectory() as tmp:
                base = Path(tmp)
                profiles = base / 'profiles'
                data = {'machine': {'name': 'Bambu Lab A1 0.4 nozzle'},
                        'process': {'name': '0.20mm Standard @BBL A1', 'wall_loops': '2'},
                        'filament': {'name': 'Bambu PLA Basic @BBL A1'}}
                for kind, value in data.items():
                    (profiles / kind).mkdir(parents=True)
                    (profiles / kind / 'profile.json').write_text(json.dumps(value), encoding='utf-8')
                model = base / 'piece.stl'
                model.write_text('mock slicer input', encoding='utf-8')
                output = base / 'output'

                def fake_slice(command, **kwargs):
                    work = Path(command[command.index('--outputdir') + 1])
                    (work / 'result.json').write_text(json.dumps({'return_code': return_code,
                        'sliced_plates': [{'id': 1, 'total_predication': 100}]}), encoding='utf-8')
                    (work / 'plate.gcode').write_text('; CONFIG_BLOCK_START\n; wall_loops = '
                        + effective + '\n; CONFIG_BLOCK_END\n', encoding='utf-8')
                    return subprocess.CompletedProcess(command, return_code, '', '')

                args = ['bambu_slice.py', str(model), '--outdir', str(output), '--set', 'wall_loops=3']
                with patch.object(sys, 'argv', args), patch.object(self.slicer, 'find_exe', return_value='fake'), \
                     patch.object(self.slicer, 'find_profiles', return_value=str(profiles)), \
                     patch.object(self.slicer.subprocess, 'run', side_effect=fake_slice), redirect_stdout(StringIO()):
                    if expected_exit:
                        with self.assertRaises(SystemExit) as raised:
                            self.slicer.main()
                        self.assertEqual(raised.exception.code, expected_exit)
                    else:
                        self.slicer.main()
                summary = json.loads((output / 'slice_summary.json').read_text(encoding='utf-8'))
                self.assertEqual(summary['ok'], expected_exit == 0)


if __name__ == '__main__':
    unittest.main()
