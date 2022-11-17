#!/bin/bash
set -ex

#sh scripts/setup.sh

python3 scripts/experiment.py testscenarios/scenario_delay_minRate.csv testscenarios/scenario_rate_cli.csv testscenarios/scenario_rate_both.csv testscenarios/scenario_rate_srv.csv testscenarios/scenario_rate_both_duplicate.csv

sh scripts/teardown.sh

python3 scripts/analyze.py results/rate_both_duplicate results/delay_minRate results/rate_both
