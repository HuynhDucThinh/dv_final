import sys, io, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from app.api.analysis_chat import _is_data_calculation_query, _auto_generate_pandas_code, _get_cached_df
import pandas as pd, numpy as np
print('=== RUNNING TIER 3 TEST ===')
df = _get_cached_df()
print(f'Loaded CSV: {len(df)} rows')
q = 'tính trung bình số km xe Dầu đi được so với xe Xăng theo từng năm sản xuất từ 2018-2023'
print('Intent check:', _is_data_calculation_query(q))
code = _auto_generate_pandas_code(q)
print('Code generated:', bool(code))
buf = io.StringIO()
old = sys.stdout
sys.stdout = buf
exec(code, {'df': df.copy(), 'pd': pd, 'np': np})
sys.stdout = old
res = buf.getvalue()
print(res)
print('Checks:')
print('44,957.6 in output:', '44,957.6' in res)
print('58,460.7 in output:', '58,460.7' in res)
