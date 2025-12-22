from pathlib import Path
p = Path('dashboard/app_with_charts.py')
s = p.read_text(encoding='utf-8')
old = 'use_container_width=True'
new = "width='stretch'"
s = s.replace(old, new)
old2 = 'use_container_width=False'
new2 = "width='content'"
s = s.replace(old2, new2)
# Also replace instances in st.dataframe/st.image calls if still present
p.write_text(s, encoding='utf-8')
print('Replaced use_container_width occurrences in', p)
