from metrics import *

base_path = "./Experiments/"

topics = [
    '藻礁',
    '林智堅論文抄襲',
    '萊豬',
    '柬埔寨詐騙',
    '數位中介服務法'
]

files = [
    '自訂summary.txt',
    'kmeans_summary.txt',
    'openai_summary.txt',
    'azure_language_service_summary.txt',
    'naive_summary.txt',
]

for topic in topics:
    print(topic)
    with open(f"{base_path}{topic}/{files[0]}", "r") as fh:
        ans = fh.read().replace("\n", "").replace(" ", "")

        for f in files[1:]:
            with open(f"{base_path}{topic}/{f}", "r") as fh:
                summary = fh.read().replace("\n", "").replace(" ", "")
            f1_score = summary_f1_eval(summary, ans)
            print(f"{f[:-4]}: {f1_score}\n")
            summary = f"f1 score: {f1_score}\n" + summary
            with open(f"{base_path}{topic}/{f}", "w") as fh:
                fh.write(summary)
