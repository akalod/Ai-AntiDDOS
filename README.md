# Ai-AntiDDOS
Bağlantı artışını konfigüre edilen sürede kontrol edip konfigüresine göre nasıl davranacağına karar veren istatistiksel betik  
ilk sürümü 50satır gibi kısa ve fonksiyonel bir methodolojide minimal olarak mySQL veritabanı kullanmaktaydı. (whitelist için) 
o zamanlar metin2 serverına ve web serverlarına gelen isteklerin saldırı olup olmadığını anlayabilmesi için geliştirilmişti.
Geleneksel anti-ddos scriptleri 1dk süreyle ayarlandığı maximum bağlantı sayısına ulaşan ip adreslerini engelliyordu.
bunun dez avantajları şöyle denilebilir.
1- 1dk tepki vermek için çok uzun bir süre ( port bazlı saldırılarda özellikle yoğun olan mySQL 3306 gibi bir porta yapılıyorsa, bu süreç içerisinde sunucu kaynağı daralacağı için yeterli değildi)
2- internet cafe gibi paylaşımlı ip adresi kullanan yerlerde bu hesaplama gereksiz yere erişimleri engellemekteydi
3- kendi ağında veri akışı yapan serverlarda kurban verebilmekteydi (:

#rev2 de değişiklikler
ilk versionu ne zaman hazırladığımı hatırlamıyorum o kadar uzun zaman oldu bu versionu 4 mayıs 2015 te hazırlamışım (arada askerlik iş güç filan girdiğini düşünürsek) 2013 olabilir.
2.version nesne tabanlı olarak hazırlandı ve mySQL yerine SQLlite üzerinde çalışıyor. ayarlar dosyası dışarıdan çağırılıyor. python 2.7 de geliştirilmişti 3 sürümlerinde denenmedi. (ayarlar dosyası yada yerel veritabanı dosyası yoksa kendisi oluşturuyor)


derlenerek çalıştırmalarda standalone ayarı ile  parametre sekmesi önleniyor.


``` python 
  if 'help' in sys.argv:
      print "Komutlar // Commands:"
      print "|_whiteList #kontrol disi tutulan ayricaliklilarin listesi"
      print "|_addWhiteList #beyazListeye ekleme  'python ai.py addWhiteList ipAdresi'"
      print "|_removeWhiteList #beyazListeden silme 'python ai.py removeWhiteList ipAdresi'"
      print "|_blackList #banlananlarin listesi"
```

WhiteListe ekleme (istatistiği takip edilmeyeceklere ekleme)
``` shell
python ai.py addWhiteList ipAdresi 
```
