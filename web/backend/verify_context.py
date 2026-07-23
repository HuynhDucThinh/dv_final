import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'd:\TU HOC\DV_Final\web\backend')

from app.api.analysis_chat import ANALYSIS_SYSTEM_PROMPT

print('[OK] analysis_chat imported successfully')
print(f'[OK] System prompt length: {len(ANALYSIS_SYSTEM_PROMPT):,} chars')

checks = {
    'ROLE block': '[ROLE' in ANALYSIS_SYSTEM_PROMPT,
    'CIRCUMSTANCE block': '[CIRCUMSTANCE' in ANALYSIS_SYSTEM_PROMPT,
    'RULES block': '[RULES' in ANALYSIS_SYSTEM_PROMPT,
    'Row count 33,848': '33,848' in ANALYSIS_SYSTEM_PROMPT,
    'File path CSV': 'car_detail_processed.csv' in ANALYSIS_SYSTEM_PROMPT,
    'Column name real': 'VND' in ANALYSIS_SYSTEM_PROMPT,
    'Null warning': '66.' in ANALYSIS_SYSTEM_PROMPT,
}

for check, result in checks.items():
    status = '[OK]' if result else '[FAIL]'
    print(f'{status} {check}')

print()
print('=== STRUCTURE PREVIEW ===')
lines = ANALYSIS_SYSTEM_PROMPT.split('\n')
for i, line in enumerate(lines[:50]):
    if line.strip().startswith('#') or 'ROLE' in line or 'CIRCUMSTANCE' in line or 'RULES' in line or '33,848' in line or 'car_detail' in line:
        print(f'  L{i+1}: {line}')
