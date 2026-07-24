import json, pathlib, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

LOG = r'C:\Users\DUC THINH\.gemini\antigravity-ide\brain\aeedb5ce-db54-43d4-9943-8d8e14c44e06\.system_generated\logs\transcript_full.jsonl'
lines = pathlib.Path(LOG).read_text(encoding='utf-8').splitlines()

# Tim step 173 de xem code thay doi Phase B
for i, line in enumerate(lines):
    try:
        obj = json.loads(line)
        step = obj.get('step_index', i)
        if step in [173, 174, 175, 176, 177, 178]:
            content = str(obj.get('content',''))
            print(f"=== STEP {step} ===")
            # Tim phan lien quan den astream
            if 'astream' in content or 'Phase B' in content or 'async for' in content:
                # Tim doan code
                idx = content.find('astream')
                if idx >= 0:
                    print(content[max(0,idx-200):idx+500])
                idx2 = content.find('Phase B')
                if idx2 >= 0:
                    print(content[max(0,idx2-100):idx2+600])
    except:
        pass
