#01010011 01100101 01111001 01101000 01100001 01101110 00100000 01011001 01001001 01001100 01000100 01001001 01011010
#53 65 79 68 61 6e 20 59 49 4c 44 49 5a
#Frluna LVYQVM
#

__author__ = 'sTaRs'
__database__ = 'statistic.db'
__checkTime__ = 5 #saniye
__checkLimit__ = 40 #__checkTime__ de artabilecek en yüksek tekil ip bağlantı sayısı
__checkMaxConnection__ = True #En yüksek kurulabilecek bağlantıya limit koymak için true, yoksa false
__maxConnection__ = 250 #en yüksek bağlantı kurabilecek tekil ip bağlantı sayısı
__standalone__ = False #tek başına çalışma durumu python parametre almıyor ise
__osSense__ = False #işletim sistemi duyarlılığı True iken windows işletim sisteminde başlaması engellenir.Debug için False kalması önerilir windowsta zaten çalışmaz
__checkCommand__ = "netstat -nta | awk '{print $5}' | cut -d: -f1 | sort | uniq -c | sort -n" #tarama komutu
__banCommand__ = "ipfw add deny ip from %s to me" #banlama komutu %s string cinsinden ipx adresinin aldığı değişkendir