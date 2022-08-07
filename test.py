from datetime import tzinfo
import arrow

date='2022/06/25 14:44'
date=arrow.get(date).replace(tzinfo='local')
date.format('YYYY/MM/DD HH:mm')
print(date.format('YYYY/MM/DD HH:mm'))
