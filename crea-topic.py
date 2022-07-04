#
from crea_topic_lib import *

#
import sys
import getopt
import configparser
#
argv = sys.argv[1:]
# per test, da commentare per runtime su SO
argv = '-e LOCAL -p 2 -r 2 -i LDH -s 604800000 -t LDH_asas_sasa_rere_DEFAULT'.split()
#

#inserire gestione riciclo errore file in base alla dim. > 1000000


LOGNAME_curr = CTRL_FilE_LOG()
#
write_log(" | INFO | Inizio processo di creazione topic Kafka...",LOGNAME_curr)

#
#
if len(argv) > 1:
    try:
        opts, argv = getopt.getopt(argv, "e: p: r: i: s: t:")
    except getopt.error as msg:
        sys.stdout = sys.stderr
        write_log(" | ERROR | Eccezione getopt Opzione non valida.",LOGNAME_curr)
        #
        usage_msg(LOGNAME_curr)
        exit()
    except getopt.GetoptError as msg:

        write_log(" | ERROR | getopt.GetoptError "+str(opts), LOGNAME_curr)

    ENVIRONMENT =None
    PARTITIONS =  None
    REPLICATION_FACTOR = None
    INFRASTRUCTURE = None
    RETENTION_MS = None
    TOPIC_NAME = None


    for o, a in opts:
        if o == '-e':
            print("-e", a)
            ENVIRONMENT = a
        if o == '-p':
            PARTITIONS = a
            print("-p", a)
        if o == '-r':
            REPLICATION_FACTOR = a
            print("-r",a)
        if o == '-i':
            INFRASTRUCTURE = a
            print("-i",a)
        if o == '-s':
            RETENTION_MS = a
            print("-s",a)
        if o == '-t':
            TOPIC_NAME = a
            print("-t",a)
        if o !='-e' and o !='-p' and o !='-r' and o !='-i' and o !='-s' and o !='-t':
            write_log(" | ERROR | Opzione "+o+" non valida.",LOGNAME_curr)

else:
    print(" senza parametri ---usage.....")

# validazione input

if ENVIRONMENT == None or INFRASTRUCTURE == None or TOPIC_NAME == None:
    write_log(" | ERROR | Una o piu' opzioni obbligatorie sono assenti.", LOGNAME_curr)
    usage_msg(LOGNAME_curr)
    exit()

#se l'utente inserisce un numero di partizioni, valida che sia un numero intero
if PARTITIONS != None:
    try:
        PARTITIONS = int(PARTITIONS)
    except ValueError as msg:
        None
#
    if type(PARTITIONS) != int:
        write_log(" | ERROR | Il parametro -p "+str(PARTITIONS)+" deve essere un numero intero.", LOGNAME_curr)
        usage_msg(LOGNAME_curr)
        exit()
    #
    if PARTITIONS > 0:
        write_log(" | INFO | Sono state selezionate "+str(PARTITIONS)+" partizioni.", LOGNAME_curr)
        FLAG_PARTITIONS = 1
else:
   write_log("  | INFO | Non sono state selezionate partizioni. Si procedera' con il default.", LOGNAME_curr)
   FLAG_PARTITIONS = 0

#se l'utente inserisce un numero di repliche, valida che sia un numero intero
if REPLICATION_FACTOR != None:
    try:
        REPLICATION_FACTOR = int(REPLICATION_FACTOR)
    except ValueError as msg:
        None
#
    if type(REPLICATION_FACTOR) != int:
        write_log(" | ERROR | Il parametro -r "+str(REPLICATION_FACTOR)+" deve essere un numero intero.", LOGNAME_curr)
        usage_msg(LOGNAME_curr)
        exit()
    #
    if PARTITIONS > 0:
        write_log(" | INFO | Sono state selezionate "+str(REPLICATION_FACTOR)+"  repliche per partizioni.", LOGNAME_curr)
        FLAG_REPLICATION = 1
else:
   write_log("  | INFO | Non sono state selezionate repliche per le partizioni. Si procedera' con il default.", LOGNAME_curr)
   FLAG_REPLICATION = 0

#se l'utente inserisce una retention, valida che sia un numero intero
if RETENTION_MS != None:
    try:
        RETENTION_MS = int(RETENTION_MS)
    except ValueError as msg:
        None
#
    if type(RETENTION_MS) != int:
        write_log(" | ERROR | Il parametro -s "+str(RETENTION_MS)+" deve essere un numero intero.", LOGNAME_curr)
        usage_msg(LOGNAME_curr)
        exit()
    #
    if RETENTION_MS > 0:
        write_log(" | INFO | E' stata selezionata una retention dei dati di "+str(RETENTION_MS)+" ms.", LOGNAME_curr)
        FLAG_RETENTION = 1
else:
   write_log("  | INFO | Non e' stata selezionata la retention dei dati. Si procedera' con il default.", LOGNAME_curr)
   FLAG_RETENTION = 0


# validate_topic_name
ret = validate_topic_name(TOPIC_NAME,LOGNAME_curr,INFRASTRUCTURE)
if ret > 0:
   exit()
#Validazione ambiente/infrastruttura e impostazione variabili di default per ambiente
#
config = configparser.RawConfigParser()
file_ini = "crea-topic.ini"
config.read(file_ini)
# Controllo valori ambiente
ENV_LIST = config.get('COMMON', 'ENV_LIST')
ENV_LIST = ENV_LIST.split(",")
#
ce=0
for s_env in ENV_LIST:
    if ENVIRONMENT == s_env:
        ce=ce+1
if ce==0:
    write_log(" | ERROR | Il parametro -e " + str(ENVIRONMENT) + " deve essere una valore compreso in  ""+ENV_LIST+"" .", LOGNAME_curr)
    write_log(" | ERROR | Ambiente  " + str(ENVIRONMENT) + " non riconosciuto.",LOGNAME_curr)
    usage_msg(LOGNAME_curr)
    exit()
#


ZOOKEEPER = config.get(INFRASTRUCTURE, ENVIRONMENT+'_ZOOKEEPER')

if ZOOKEEPER.strip() == '':
    write_log(" | ERROR | Ambiente "+ENVIRONMENT+" non disponibile su infrastruttura "+INFRASTRUCTURE+".",LOGNAME_curr)
    usage_msg(LOGNAME_curr)
    exit()

if FLAG_REPLICATION == 0:
    REPLICATION_FACTOR = config.get(INFRASTRUCTURE, ENVIRONMENT+'_REPLICATION')
if FLAG_RETENTION == 0 or INFRASTRUCTURE == "LDH":
    if INFRASTRUCTURE == "LDH" and TOPIC_NAME.find("DEFAULT"):
        RETENTION_MS = config.get(INFRASTRUCTURE, ENVIRONMENT + '_RETENTION_DEF1')
    else:
        RETENTION_MS = config.get(INFRASTRUCTURE, ENVIRONMENT + '_RETENTION_DEF2')
    if  INFRASTRUCTURE != "LDH":
        RETENTION_MS = config.get(INFRASTRUCTURE, ENVIRONMENT+'_RETENTION')
if FLAG_PARTITIONS == 0:
   PARTITIONS = config.get(INFRASTRUCTURE, ENVIRONMENT+'_PARTITIONS')

#Creazione topic

#
SHELL_CRE_TOPIC = config.get('COMMON', 'SHELL_CRE_TOPIC')
COM_CRE_TOPIC = SHELL_CRE_TOPIC+" --zookeeper "+ZOOKEEPER+ \
              " --create --topic "+TOPIC_NAME+ \
              " --partitions "+str(PARTITIONS)+ \
              " --replication-factor "+str(REPLICATION_FACTOR)+ \
              " --config retention.ms="+str(RETENTION_MS)

write_log(" | INFO | "+COM_CRE_TOPIC,LOGNAME_curr)
# COM_CRE_TOPIC da eseguire con comando lib os.system() oppure subprocess.run 


write_log(" | INFO | Fine processo di creazione topic Kafka...",LOGNAME_curr)










