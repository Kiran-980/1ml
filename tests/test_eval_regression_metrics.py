"""Independent competition metric must match log, not log1p, semantics."""
import math
import unittest

from evals.harness.regression_metrics import log_rmse, constant_log_prediction


class LogMetricTests(unittest.TestCase):
    def test_exact_logs_differ_from_log1p(self):
        self.assertAlmostEqual(log_rmse([1., 4.], [2., 2.]), math.log(2.))
        self.assertEqual(log_rmse([1., 4.], [1., 4.]), 0.)

    def test_constant_baseline_uses_development_labels_only(self):
        self.assertAlmostEqual(constant_log_prediction([1., 4.]), 2.)
        self.assertNotEqual(constant_log_prediction([1., 4.]), 2.5)

    def test_invalid_inputs_fail_instead_of_broadcasting_or_clipping(self):
        for observed, predicted in (([], []), ([1., 2.], [1.]), ([0.], [1.]),
                                    ([1.], [-1.]), ([1.], [float('inf')]),
                                    ([float('nan')], [1.]), ([[1.]], [1.])):
            with self.subTest(observed=observed, predicted=predicted):
                with self.assertRaises(ValueError):
                    log_rmse(observed, predicted)


if __name__ == '__main__':
    unittest.main()
