###############################################################################
###############################################################################
##
## PyHART - Rev 3.3
##
## MODULO DEMO
##
## REQUISITI
##  OS indipendent
##  installare python 3.6 o superiore
##  via pip installare la libreria pySerial che non è inclusa di default in python
##  ed eventualmente altre librerie mancanti.
##  Visualizzare questo modulo in formato UTF-8.
##
###############################################################################
###############################################################################


"""
###############################################################################
1) IMPORT SECTION
"""
import sys
sys.path.append('./COMMUNICATION') # INDICARE LA PATH DELLA FOLDER COMMUNICATION

import time # usato per una sleep nel file...

import Comm     # MANDATORY - modulo all'interno della folder communication.
import CommCore # MANDATORY - modulo all'interno della folder communication.

import Types    # OPTIONAL - solo se si usano le funzioni di encode/decode dei tipi hart - modulo all'interno della folder communication.
                #            questo modulo contiene funzioni per trasformare facilmente in bytearray o viceversa i dati ricevuti o da inviare.
                #            vengono gestiti tutti i tipi hart: int (1, 2, 3, 4 bytes), float, packAscii, date, time, ...
                
import Utils    # OPTIONAL - solo se si utilizzano le funzioni definite in Utils - modulo all'interno della folder communication.
                #            questo modulo contiene una serie di funzioni di utilità generale. Di seguito ne viene utilizzata qualcuna.
                
import Device   # OPTIONAL - solo se interessa conoscere in dettaglio le caratteristiche del device - modulo all'interno della folder communication.

import Packet   # OPTIONAL - solo se si usano le informazioni contenute in un pacchetto hart, preamboli, delimiter, address eccetera... 
                #          - modulo all'interno della folder communication.

# Print PyHART revision (revisione corrente 3.0)
# Successivamente verrà spiegato come PyHART esegue il log. Queste funzioni, chiamte prima del costruttore,
# non seguono le regole di log di PyHART. La revisione viene visualizzata nel terminale.
print("\nPyHART revision " + Utils.PyHART_Revision() + "\n")

# Lista delle COM ports e selezione di una COM port.
# Successivamente verrà spèiegato come PyHART esegue il log. Queste funzioni, chiamte prima del costruttore,
# non seguono le regole di log di PyHART. Le porte vengono visualizzate nel terminale.

# Questa funzione elenca solamente le COM ports
count, listOfComPorts = Utils.ListCOMPort(False)
print("\n")

# Questa procedura permette di selezionare una COM port
count, listOfComPorts = Utils.ListCOMPort(True)
comport = None
selection = 0
while (comport == None) and (selection != (count + 1)):
    print ("\nSelect the communication port. Insert related number and press enter.")
    try:
        selection = int(input())
    except:
        selection = 0
    comport = Utils.GetCOMPort(selection, listOfComPorts)
    print("Invalid Selection")
    
if (selection == (count + 1)):
    print("Leaving application...")
    sys.exit()

"""
###############################################################################
2) COME INSTANZIARE LA CLASSE DI COMUNICAZIONE HART
   
   Classe "HartMaster"
   
   MANDATORY PARAMETERS
   - port: la porta di comunicazione COM o TTY in formato stringa
   
   PROTOCOL PARAMETERS
   - masterType: indica se si vuole simulare un primary o un secondary master 
                 (CommCore.MASTER_TYPE.PRIMARY, CommCore.MASTER_TYPE.SECONDARY - SE OMESSO VIENE USATO IL DEFAULT PRIMARY)
   - num_retry: numero di tentativi in caso di fallimento (SE OMESSO VIENE USATO IL DEFAULT 3 che significa 1 tentativo + 3 retries) 
                Quando num_retry è specificato, indica 1 tentativo più numero di retry inserito. 
                Volendo se non si vogliono retries si mette zero e fa solo la prima comunicazione. 3 è il massimo accettabile.
   - retriesOnPolling: indica se i retries devono essere effettuati anche sul comando zero con short address. spesso se si polla su molti polling addresses
     è comodo non avere i retries. Se omesso i retries vengono effettuati altrimenti si specifica True o si mette False se non si vogliono.
   
   LOG PARAMETERS
   - autoPrintTransactions: è possibile decidere se loggare automaticamente tutte le transazioni (domanda + risposta) di tutti i 
                            comandi hart eseguiti senza dover esplicitamente richiamare le funzioni di log.
                            (SE OMESSO EQUIVALE A TRUE).
   - whereToPrint: quando si logga, sia in modo automatico che manuale, o comunque quando si esegue una qualsiasi funzione "print",
                   si può scegliere se loggare su terminale soltanto, su file soltanto o su entrambi. (WhereToPrint.BOTH, WhereToPrint.FILE, WhereToPrint.TERMINAL)
                   (SE OMESSO SIGNIFICA SOLO TERMINALE)
   - logFile: indica il nome del file dove loggare quando "whereToPrint" è BOTH o FILE. Se specificato ma con "whereToPrint" uguale a TERMINAL, 
              il file non viene gestito. Il file viene aperto in append e ogni sessione è inizializzata con uno stamp del date/time corrente.
   
   SYSTEM PARAMETERS
   - rt_os: (True o False) indica se si sta eseguendo su un real time operating system. (SE OMESSO è COME SE FOSSE SETTATO a False)
            Ad esempio è stato utilizzato su Raspberry Pi3 dove c'era un OS con kernel compilato come real time, è inutile su windows. 
            Più che altro va in accoppiata con il prossimo parametro.
            Lo si usa per chiudere l'RTS immediatamente dopo la trasmissione dell'ultimo byte. Altrimente l'RTS viene abbassato dopo un tempo indeterminato.
   - manageRtsCts: (True o False) indica se pyHART deve gestire i segnali RTS e CTS della seriale, è inutile con i modem ABB che gestiscono l'RTS da se. 
                   (SE OMESSO è COME SE FOSSE SETTATO a False)
"""
hart = Comm.HartMaster(comport, CommCore.MASTER_TYPE.PRIMARY, num_retry = 0, retriesOnPolling = False, autoPrintTransactions = True, whereToPrint = Comm.WhereToPrint.BOTH, logFile = "terminalLog.log", rt_os = None, manageRtsCts = None)


"""
###############################################################################
3) START
   Lo Start è obbligatorio, è un equivalente di port open.
   Oltre ad aprire la porta fa partire il thread di monitor della rete hart che fa da sniffer di quello che passa.
   Ad esempio si supponga uno strumento in burst o delle comunicazioni fatte con un altro master, si mette un modem
   in parallelo, si crea l'oggetto Comm.HartMaster, si fa Start e le comunicazioni vengono loggate (se autoPrintTransactions = True).
"""
hart.Start()


"""
###############################################################################
3) LET KNOW DEVICE
   Questa funzione esegue un command zero con short address.
   L'unico parametro è il polling address.
   Nell'esempio seguente pollo su più poll addresses e interrompo il ciclo di polling al primo device trovato.
"""
FoundDevice = None
pollAddress = 0

# polling da 0 a 4
while (FoundDevice == None) and (pollAddress < 5):
    # esegue il comando zero con short address
    # Tutte le transizioni domanda e eventuali risposte vengono loggate in terminale e file automaticamente in quanto autoPrintTransactions = True.
    # Non c'è quindi bisogno di esplicitare nessun log dei frames trasmessi e ricevuti.
    CommunicationResult, SentPacket, RecvPacket, FoundDevice = hart.LetKnowDevice(pollAddress)
    pollAddress += 1

if (FoundDevice is not None):
    # utility per loggare le informazioni di un device
    # questo log finirà sia su terminale che su file in quanto whereToPrint = WhereToPrint.BOTH e logFile = "terminalLog.log".
    Utils.PrintDevice(FoundDevice, hart)


"""
###############################################################################
4) CAPIRE I VALORI DI RITORNO DELLE FUNZIONI CHE ESEGUONO DEI COMANDI HART
# La funzione precedente ha eseguito il comando zero e ha ritornato CommunicationResult, SentPacket, RecvPacket e FoundDevice
#
# CommunicationResult: esito della comunicazione
#              Ok: La comunicazione è andata a buon fine (indipendentemente dal response code ricevuto che sia "ok" o no)
#      NoResponse: Il master non ha ricevuto risposta a fronte di una domanda (dopo un timeout).
#   ChecksumError: Il master ha riscontrato un errore di checksum nel frame di risposta ricevuto dallo slave device.
#      FrameError: Il frame ricevuto è inconsistente.
#            Sync: I byte ricevuti vengono scartati dal master finchè sula rete non viene vista una valida sequenza di preamboli
#                  che indicano l'inizio di un frame. Ad esempio quando si ascolta una rete, dopo lo start può darsi che 
#                  il master veda dei bytes che si trovano a metà di un frame che sta passando in quel momento e quindi li scarta 
#                  dicendo che si trova in sincronizzazione.
#
# SentPacket e RecvPacket: sono i pacchetti trasmessi e ricevuti durante una transazione.
#   i pacchetti sono delle classi definite nel modulo "Packet" nella folder "COMMUNICATION".
#   Gli attributi sono i campi di un frame HART, preamboli, delimiter, address, command, dataLen, 
#   resCode, device status, data e checksum.
#   Da qui è quindi possibile verificare se un respons code vale "OK" o no.
#   In un sent packet, response code e device status non hanno un significato valido.
#
# FoundDevice: questo viene ritornato solo dalla funzione "LetKnowDevice(<poll-address>)".
#   Rappresenta il device trovato, è una classe definita nel modulo "Device" nella folder "COMMUNICATION".
#   Come già visto in precedenza esiste una utility per stamparne il contenuto.
#   Se si vuole comunicare con più device, una volta identificati i dispositivi attraverso "LetKnowDevice", è possibile
#   richiamare la funzione "hart.SetOnlineDevice(device)" per comunicare con uno o l'altro senza rieseguire il comando zero di polling.
#   "hart.OnlineDevice()" restituisce il device corrente con cui si sta comunicando.
#
# Di seguito vengono mostrate altre funzioni per eseguire i comandi HART.
# I valori di ritorno sono sempre gli stessi CommunicationResult, SentPacket e RecvPacket.
# Esiste anche una utility per eseguire un comando HART più facilmente, che ritorna un parametro in più. Verrà spiegato di seguito (punto 5).
"""
# Qui analizzo lo stato della comunicazione e il response code ricevuto
if (CommunicationResult == CommCore.CommResult.Ok) and (RecvPacket.resCode == 0):
    print("Tutto ok!")


"""
###############################################################################
5) ESECUZIONE DEI COMANDI HART IN DUE MODI DIVERSI
   - con metodo della classe
   - attraverso una utility
"""
## ESEMPIO 01 - con metodo della classe
# In questo esempio viene inviato il comando 15.
CommunicationResult, SentPacket, RecvPacket = hart.PerformTransaction(15, None) # None perchè il comando 15 non 
                                                                                # richiede che vengano inviati dei dati
if (CommunicationResult == CommCore.CommResult.Ok):
    if (RecvPacket.resCode == 0):
        # Non stampo i due pacchetti ricevuti e trasmessi in quanto lo fa già il modulo hart in automatico! (se nel costruttore autoPrintTransactions = True)
        # mi faccio dare solo i valori del range e la unit
        URV = Types.BytearrayToFloat(RecvPacket.data[3:7]) # utilizzo le funzioni definite nel modulo "Types"
        LRV = Types.BytearrayToFloat(RecvPacket.data[7:11])
        Unit = RecvPacket.data[2]
        
        print("read URV: {0}, read LRV: {1}".format(URV, LRV))
        print("read Unit: " + Utils.GetUnitString(Unit) + "\n") # uso una funzione di Utils che gestisce le unità HART
    else:
        print("command 15 wrong response code: {0}".format(RecvPacket.resCode))
else:
    # Comoda funzione nel modulo Utils per stampare la stringa di testo relativa ad un codice errore
    print(Utils.GetCommErrorString(CommunicationResult) + "\n")

## ESEMPIO 02 - attraverso una utility
# Esiste una utility per inglobare la gestione e log del communication result e check del response code. 
# Quindi quello fatto prima può semplicemente essere fatto come segue in meno righe.
# Qui c'è il parametro in più "retStatus".
# Non loggo più nulla in caso di communication error o response code non zero; lo fa implicitamnete l'utility function.
retStatus, CommunicationResult, SentPacket, RecvPacket = Utils.HartCommand(hart, 15, None)
if (retStatus == True):
    URV = Types.BytearrayToFloat(RecvPacket.data[3:7])
    LRV = Types.BytearrayToFloat(RecvPacket.data[7:11])
    Unit = RecvPacket.data[2]        
    print("read URV: {0}, read LRV: {1}".format(URV, LRV))
    print("read Unit: " + Utils.GetUnitString(Unit) + "\n")

# Analogamente a Utils.PrintDevice(FoundDevice, hart) vista all'inizio dello script,
# esiste Utils.PrintPacket(packet, hart) per stampare un singolo pacchetto.
# Questo viene utile quando autoPrintTransactions = False e si vuole stampare uno specifico pacchetto trasmesso o ricevuto
# Per testare questa funzione mettiamo un attimo a false autoPrintTransactions e lo riabilitiamo immediatamente dopo.
hart.autoPrintTransactions = False

# Eseguo un comando 1 che ovviamnete non viene loggato in automatico e faccio le print
# attraverso Utils.PrintPacket
print ("\n::::::::::::::::::::::::::::: COMANDO 1 :::::::::::::::::::::::::::::")
retStatus, CommunicationResult, SentPacket, RecvPacket = Utils.HartCommand(hart, 1, None)
if (retStatus == True):
    print("---------------- TRANSMITTED ----------------")
    Utils.PrintPacket(SentPacket, hart)
    print("---------------- RECEIVED ----------------")
    Utils.PrintPacket(RecvPacket, hart)

hart.autoPrintTransactions = True

"""
###############################################################################
6) ESEMPI CON ALTRI COMANDI E ALTRE UTILITY E FUNZIONI SUI TIPI
   - comandi con dati da trasmettere.
   - i dati trasmessi e ricevuti sono sempre dei bytearray.
"""
# Qui eseguo un comando 35 dove uso delle funzioni sui float e una utility sulle unità di misura
txdata = bytearray(9)
txdata[0] = Utils.GetUnitCode("Kilopascal") # è possibili consultare tutte le unità in formato testuale nel modulo Utils
txdata[1:] = Types.FloatToBytearray(120.43)
txdata[5:] = Types.FloatToBytearray(-120.43)
retStatus, CommunicationResult, SentPacket, RecvPacket = Utils.HartCommand(hart, 35, txdata)
if (retStatus == True):
    print("CALIBRATION DONE\n")

# Qui eseguo un comando 18 dove codifico il tag e la data
txdata = bytearray(21)
txdata[0:] = Types.PackAscii("NEW TAG")
txdata[6:] = bytearray([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
txdata[18:] = Types.DateStringToBytearray("05/11/2016")
retStatus, CommunicationResult, SentPacket, RecvPacket = Utils.HartCommand(hart, 18, txdata)
if (retStatus == True):
    # Qui eseguo un comando 13 dove decodifico il tag e la data
    retStatus, CommunicationResult, SentPacket, RecvPacket = Utils.HartCommand(hart, 13, None)
    if (retStatus == True):
        tag = Types.UnpackAscii(RecvPacket.data[0:6])
        date = Types.BytearrayToDateString(RecvPacket.data[18:21])                
        print("read tag: [{0}], read date: [{1}]\n".format(tag, date))


"""
###############################################################################
7) NUMERO DI COMANDO SOPRA IL 255
"""
# Qui eseguo un comando 1280 cioè > 255
# Lo si invia allo stesso modo degli altri comandi.
txData = bytearray(1)
txData[0] = 0
retStatus, CommunicationResult, SentPacket, RecvPacket = Utils.HartCommand(hart, 1280, txData)
print("Vedi il log...")


"""
###############################################################################
8) INVIO DI BROADCAST FRAMES
"""
# Alcuni comandi come l'11 o il 21 possono essere inviati anche con il broadcast address.
# Non è prevista la forma Utils.HartCommand.

# In questo esempio non mi interessa inserire un valore corretto per il long tag del comando 21.
# Basta che siano 32 bytes. Quello che voglio fare vedere è l'uso del broadcast address.
txdata = bytearray(32) 
CommunicationResult, SentPacket, RecvPacket = hart.PerformBroadcastTransaction(21, txdata)

"""
###############################################################################
9) INVIO DI FRAME CUSTOM.
    Alle volte, ad esempio a scopo di test, è comodo lavorare sui bytes di un frame
    non direttamente correlati a un comando e i suoi dati.
    Si vuole quindi agire su address, checksum, data lenght, delimiter o sequenze di bytes casuali.
    Si può quindi inviare un buffer di byte a piacere.
"""
# In questo esempio invio un comando zero con short address e polling address zero.
# in questo specifico caso questa operazione equivale a chiamere la funzione LetKnowDevice(0)
txFrame = bytearray([0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x02, 0x80, 0x00, 0x00, 0x82])
CommunicationResult, SentPacket, RecvPacket = hart.SendCustomFrame(txFrame)

# Quando si vuole inviare un frame custom viene più comodo utilizzare la classe Packet che 
# include il calcolo del checksum in automatico.
pkt = Packet.HartPacket()
pkt.preamblesCnt = 8
pkt.delimiter = 0x82
pkt.address = bytearray([0x80, 0x00, 0x00, 0x00, 0x00]) # Broadcast address
pkt.command = 21
pkt.dataLen = 32
pkt.resCode = 0
pkt.devStatus = 0
pkt.data = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
pkt.checksum = pkt.ComputeChecksum() # Il checksum lo faccio calcolare al pacchetto stesso.

# Prima di inviare il pacchetto devo convertirlo in frame (bytearray).
txFrame = pkt.ToFrame()
CommunicationResult, SentPacket, RecvPacket = hart.SendCustomFrame(txFrame)

# Anche qui utilizzo la classe Packet che 
# Per l'address uso l'OnlineDevice cioè il device su cui è stato eseguito il comando zero (LetKnowdevice())
# include il calcolo del checksum in automatico.
pkt = Packet.HartPacket()
pkt.preamblesCnt = 8
pkt.delimiter = 0x82
if (hart is not None) and (hart.OnlineDevice() is not None): 
    pkt.address = hart.OnlineDevice().longAddress[:] # non è broadcast ma uso l'indirizzo del device correntemente "online"
else:
    pkt.address = bytearray([0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
pkt.command = 21
pkt.dataLen = 32
pkt.resCode = 0
pkt.devStatus = 0
pkt.data = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
pkt.checksum = pkt.ComputeChecksum() # Il checksum lo faccio calcolare al pacchetto stesso.

# Prima di inviare il pacchetto devo convertirlo in frame (bytearray).
txFrame = pkt.ToFrame()
CommunicationResult, SentPacket, RecvPacket = hart.SendCustomFrame(txFrame)

"""
###############################################################################
10) STOP
    Lo stop fa la close della porta e la kill (pulita) del thread di network monitor.
    dopo lo stop si può fare di nuovo Start() senza dover instanziare la classe HartMaster nuovamente.
"""
hart.Stop()


"""
###############################################################################
11) SNIFFER DI RETE
    Collegare un modem in parallelo a quello su cui è connesso il device.
    Mettere il field device in burst 
    o mettere più field devices in multidrop eccetera.
    Decommentare per eseguire.
"""
"""
# Start monitoring again
hart.Start()

# CTRL+C è solo un modo sporco per bloccare il while infinito e lo script in esecuzione
print("Press CTRL+C to exit.")

print("\nNetwork Listening...")
while True:
    time.sleep(0.250)

hart.Stop()
"""


