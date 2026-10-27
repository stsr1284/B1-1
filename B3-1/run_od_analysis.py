"""Run current B3-1 OD pipeline; acquire originals separately if absent."""
import argparse
import os
import subprocess
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def main():
    p=argparse.ArgumentParser();p.add_argument('--from-tables',action='store_true',help='Recreate figures/report using included compact analysis tables');args=p.parse_args()
    os.environ.setdefault('POLARS_MAX_THREADS','4');os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'tmp/matplotlib_od'))
    steps=['report'] if args.from_tables else ['prepare','audit_aliases','audit_presence','prepare','analyze','report','verify']
    for module in steps:
        subprocess.run([sys.executable,'-m',f'od_analysis.{module}'],cwd=ROOT,check=True)
    print('완료: REPORT.md 및 outputs/od_preview.html')
if __name__=='__main__':main()
