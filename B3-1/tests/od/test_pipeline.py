import unittest
import polars as pl
from od_analysis.prepare import process_day
from od_analysis.common import HOURS

class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.mapping = pl.DataFrame({'raw_id': ['a','aa','b'], 'region': ['A','A','B'], 'stable_seoul_name':[True,True,True]})

    def run_rows(self, rows):
        text = 'header\n' + '\n'.join(','.join(map(str,r)) for r in rows) + '\n'
        return process_day(text.encode(), ['20230101'], self.mapping)

    def row(self, o, d, n): return ['20230101',o,d,n]+['']*23

    def test_aliases_do_not_double_count_and_blanks_stay_null(self):
        data, audit = self.run_rows([self.row('a','b',5),self.row('aa','b',5)])
        self.assertEqual(audit['identical_alias_duplicates_removed'],1)
        self.assertEqual(audit['internal_passenger_sum'],5)
        self.assertTrue(audit['conservation_passed'])
        inbound = data.filter(pl.col('scope')=='internal_in')
        self.assertEqual(inbound['h01'].null_count(),1)

    def test_conflicting_alias_values_are_not_summed(self):
        data,audit=self.run_rows([self.row('a','b',5),self.row('aa','b',8),self.row('b','a',2)])
        self.assertEqual(audit['conflicting_alias_rows_excluded'],2)
        self.assertEqual(audit['internal_passenger_sum'],2)

    def test_missing_id_and_negative_row_excluded(self):
        data,audit=self.run_rows([self.row('','b',5),self.row('b','a',-2),self.row('a','b',3)])
        self.assertEqual(audit['null_id_rows'],1)
        self.assertEqual(audit['negative_rows'],1)
        self.assertEqual(audit['internal_passenger_sum'],3)

    def test_bad_numeric_cell_is_fatal(self):
        with self.assertRaises(pl.exceptions.ComputeError): self.run_rows([self.row('a','b','oops')])

    def test_intrazonal_is_separate(self):
        data,audit=self.run_rows([self.row('a','aa',7),self.row('a','b',2)])
        self.assertEqual(audit['within_passenger_sum'],7)
        self.assertEqual(audit['internal_passenger_sum'],2)


class ComparisonTests(unittest.TestCase):
    def test_missing_weekday_stratum_blocks_comparison(self):
        import pandas as pd
        from od_analysis.analyze import standardize
        rows=[]
        for day in [5,6]:
            for n in range(2):
                rows.append({'year':2025,'month':1,'weekday':day,'date':f'202501{day+n*7:02}', 'regular':True,
                             'scope':'internal_in','region':'A','weekend_day':10.0,'weekend_core':10.0,'weekday_morning':10.0})
        complete=standardize(pd.DataFrame(rows),'test',[1],2025)
        self.assertTrue(complete[complete.window=='weekend_day'].eligible.iloc[0])
        self.assertEqual(complete[complete.window=='weekend_day'].value.iloc[0],10.0)
        missing=standardize(pd.DataFrame(rows[:2]),'test',[1],2025)
        self.assertFalse(missing[missing.window=='weekend_day'].eligible.iloc[0])

if __name__=='__main__':unittest.main()
