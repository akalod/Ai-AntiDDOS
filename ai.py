# -*-coding: utf-8-*-
import time
import sys
import sqlite3
import os.path
import codecs
from commands import getoutput

settingsFile = 'settings.py'

# ayarlar dosyasinin kontrolü ve gerekirse varsayilan olarak yeniden olusturulmasi
if not os.path.isfile(settingsFile):
    #dosyanin olusturulmasi
    file = open(settingsFile, 'w')

    data = """#01010011 01100101 01111001 01101000 01100001 01101110 00100000 01011001 01001001 01001100 01000100 01001001 01011010
#53 65 79 68 61 6e 20 59 49 4c 44 49 5a
#Frluna LVYQVM

__author__ = 'sTaRs'
__database__ = 'statistic.db'
__checkTime__ = 5 #saniye
__checkLimit__ = 40 #__checkTime__ de artabilecek en yüksek tekil ip baglanti sayisi
__checkMaxConnection__ = True #En yüksek kurulabilecek baglantiya limit koymak için true, yoksa false
__maxConnection__ = 250 #en yüksek bağlanti kurabilecek tekil ip baglanti sayisi
__standalone__ = False #tek basina çalisma durumu python parametre almiyor ise
__osSense__ = True #isletim sistemi duyarliligi True iken windows isletim sisteminde baslamasi engellenir.Debug için False kalmasi önerilir windowsta zaten çalismaz
__checkCommand__ = "netstat -nta | awk '{print $5}' | cut -d: -f1 | sort | uniq -c | sort -n" #tarama komutu
__banCommand__ = "ipfw add deny ip from %s to me" #banlama komutu %s string cinsinden ipx adresinin aldigi degiskendir"""
    file.write(codecs.BOM_UTF8)
    file.write(data)
    file.close()

#tekrar dahil edilmesi
import settings


class antiDDOS:
    """ Startup  """
    loop = True
    __connectedIP = list

    def __connectDB(self):
        return sqlite3.connect(settings.__database__)

    def __checkDatabeTables(self):
        db = self.__connectDB();
        sql = db.cursor();
        # white List Kontrolü
        try:
            sql.execute("select count(*) as count,* from whiteList")
        except sqlite3.Error as e:
            # Tablo Yok yeniden olusturulmasi
            print 'whiteList tablosu yeniden olusturuluyor'
            sql.execute('''CREATE TABLE whiteList (ipx UNIQUE)''')
        # black List Kontrolü
        try:
            sql.execute("select count(*) as count,* from blackList")
        except sqlite3.Error as e:
            # Tablo Yok yeniden olusturulmasi
            print 'blackList tablosu yeniden olusturuluyor'
            sql.execute('''CREATE TABLE blackList (ipx,connectedCount INT,date date default CURRENT_TIMESTAMP )''')
        # aiStats
        try:
            sql.execute("select count(*) as count,* from aiStats")
        except sqlite3.Error as e:
            # Tablo Yok yeniden olusturulmasi
            print 'aiStats tablosu yeniden olusturuluyor'
            sql.execute('''CREATE TABLE aiStats (ipx UNIQUE,connectedCount INT,timeStamp)''')

        sql.close()

    def __checkConnectedIPs(self):
        #bagli iplerin toplaminin diziye döndürüldügü kisim
        try:
            data = getoutput(settings.__checkCommand__)
        except Exception, e:
            print "HATA!!! Komut çalistirilamadi"
            return None
        list = data.split("\n")
        return list

    def __banIpAdress(self, address, count):
        # ip adresini banlama islemini yapicak zimbirti
        command = settings.__banCommand__ % address  # komut çagirip ip adresi degistirilerek uygulama islemi yapiliyor
        self.__oneQuery('INSERT OR REPLACE INTO blackList (ipx,connectedCount) VALUES ("' + str(address) + '",' + str(
            count) + ')')  # database e log kayidi
        try:
            data = getoutput(command)
        except Exception, e:
            print "HATA!!! Komut çalistirilamadi"
            return None
        print("BLOCK:[" + str(count) + "]>" + address)
        return True

    def __makeCheckIP(self, dizi):
        # banlama islemleri ve whitelist kontrollerini yapicak islem blogu
        dizi = dizi.split(" ")
        count = len(dizi)
        i = 0
        ipCount = ipAdress = None
        db = self.__connectDB();
        sql = db.cursor();
        while i < count:
            if dizi[i].isdigit():
                ipCount = dizi[i]
                ipAdress = dizi[i + 1]
                # ip adresi whiteListemi Diye kontrol edilisi
                try:
                    sql.execute("select count(*) as count,* from whiteList where ipx='" + ipAdress + "'")
                    result = sql.fetchone()[0]
                    if not result:
                        # white list'te degilse yapilacak islem ve kontroller
                        # En yüksek baglanti kurulum ayarinin kontrolü ve limiti geçmis ise yapilacak islemler
                        if settings.__checkMaxConnection__ and int(ipCount) > settings.__maxConnection__:
                            self.__banIpAdress(ipAdress, ipCount)
                        else:
                            # limit kapali yada geçmemis ise yapilacak islemler serisi
                            sql.execute("select count(*) as count,* from aiStats where ipx='" + ipAdress + "'")
                            result = sql.fetchone()
                            # ilk istatistik alinisi ip adresinin
                            if not result[0]:
                                sql.execute(
                                    "INSERT INTO aiStats VALUES ('" + ipAdress + "',%d,%d)" % (
                                        int(ipCount), time.time()))
                                db.commit()

                            # daha önceden baglanti kurulmus ise
                            else:
                                # verilerin ayiklanmasi
                                # result[0] --rowCount
                                # result[1] --ipx
                                # result[2] --connectionCount
                                # result[3] --timeStamp
                                # giris süresi içerisindeki baglanti sayisi ile yeni baglanti arasindaki sürenin zaman asimi kontrolü
                                # ban baglanti durumu asinmasi halinde banlama kontunun çagirilmasi
                                if (int(result[3]) + settings.__checkTime__) > time.time() and \
                                        time.time() and ipCount > result[2] + settings.__checkLimit__:
                                    self.__banIpAdress(ipAdress, ipCount)  # banliyoruz
                                    # bilgileri güncelliyoruz
                                    query = "UPDATE aiStats set connectedCount='%d', timeStamp='%d' where ipx='%s'" % \
                                            (ipCount, time.time(), ipAdress)
                                    db.execute(query)
                                    db.commit()

                except sqlite3.Error as e:
                    print '!!! Hata:' + e.args[0]

                break
            i += 1
        newRaw = [ipCount, ipAdress]
        sql.close()
        return newRaw

    def __connectedIP(self):
        # private netstat -nta | awk '{print $5}' | cut -d: -f1 | sort | uniq -c | sort -n
        # debug modu deneme için girilmis dizi listeme fonksyionundan dönecektir.
        totalData = self.__checkConnectedIPs()

        totalDataCount = len(totalData)
        i = 0
        while i < totalDataCount:
            self.__makeCheckIP(totalData[i])
            i += 1


    def startUp(self):
        is_windows = hasattr(sys, 'getwindowsversion')
        if self.loop != True:
            sys.exit()
        if is_windows and settings.__osSense__:
            print "POSIX Uyumlu isletim sistemleri için tasarlanmistir.\nHizmet Durdu."
            sys.exit()

        print " ----------------------------------------------------"
        print "|              A.I. Anti DDOS System (reBorn) Rev:2  |"
        print "|                                                    |"
        print "|  type for help command:                            |"
        print "|  python {fileName} help                            |"
        print "|                                                    |"
        print "|                  a code by Seyhan \"sTaRs\" YILDIZ   |"
        print "|                          www.seyhanyildiz.com.tr   |"
        print " ----------------------------------------------------"
        print "| Sistem baslatildi"
        print "| Veritabani kontrol ediliyor.."

        self.__checkDatabeTables()

    # Aktif baglantilarin kontrolü
    def doCheck(self):
        print('Kontrol stamp: %d' % time.time())
        self.__connectedIP()
        time.sleep(settings.__checkTime__)

    def doStop(self):
        self.loop = False
        print "Hizmet durduruldu."

    def __oneQuery(self, query):
        db = self.__connectDB()
        sql = db.cursor()
        sql.execute(query)
        db.commit()
        db.close()


    def __commandAddWhiteList(self, ipx):
        self.__oneQuery('INSERT OR REPLACE INTO whiteList VALUES ("' + ipx + '")')
        print(str(ipx) + " adresi ayrıcaliklar listesine eklendi..")

    def __commandRemoveWhiteList(self, ipx):
        self.__oneQuery('DELETE FROM whiteList WHERE ipx="' + ipx + '"')
        print(str(ipx) + " adresi ayrıcaliklar listesinden cikarildi..")

    def __commandWhiteList(self):
        self.__checkDatabeTables()
        print "|_white List Command"
        db = self.__connectDB();
        sql = db.cursor();
        sql.execute("select count(*) as count from whiteList")
        resultCount = sql.fetchone()[0]

        sql.execute("select * from whiteList")

        i = 0
        while i < resultCount:
            result = sql.fetchone()
            i += 1
            print str(i) + ". | " + result[0]


    def checkArguments(self):
        # Python parametresi almasi yada almadan çalismasinin kontrolü
        if (settings.__standalone__):
            startArgument = 0
        else:
            startArgument = 1

        try:
            command = sys.argv[startArgument].lower()
            self.loop = False;
        except:
            command = False

        if 'help' in sys.argv:
            print "Komutlar // Commands:"
            print "|_whiteList #kontrol disi tutulan ayricaliklilarin listesi"
            print "|_addWhiteList #beyazListeye ekleme  'python ai.py addWhiteList ipAdresi'"
            print "|_removeWhiteList #beyazListeden silme 'python ai.py removeWhiteList ipAdresi'"
            print "|_blackList #banlananlarin listesi"

        if command and command == "whitelist":
            self.__commandWhiteList()

        if command and command == "addwhitelist":
            try:
                parametre = sys.argv[startArgument + 1]
            except:
                print("--Eksik parametre")
                return False

            self.__commandAddWhiteList(parametre)

        if command and command == "removewhitelist":
            try:
                parametre = sys.argv[startArgument + 1]
            except:
                print("--Eksik parametre")
                return False

            self.__commandRemoveWhiteList(parametre)


ai = antiDDOS()

# arguman kontrolü
ai.checkArguments()

# baslangiç verileri
ai.startUp()


# döngü
while ai.loop:
    try:
        ai.doCheck()
    except KeyboardInterrupt:
        ai.doStop()
        sys.exit()
