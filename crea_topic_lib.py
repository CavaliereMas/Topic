#
#
def usage_msg(file_log):

    #import os.path

    usage_msg_txt = "Lo script va lanciato con utenza root. Inserire le seguenti opzioni (i parametri tra *asterischi* sono obbligatori):"+"\n" \
    + "-e *<ENVIRONMENT>* - Ambiente Kafka nel quale si desidera creare il topic, come censito su GSS (es. SVIL, TEST, PROD)" + "\n" \
    + "-p <PARTITIONS> - Numero di partizioni desiderato per il topic" + "\n" \
    + "-r <REPLICATION_FACTOR> - Numero di repliche desiderato per ciascuna partizione " + "\n" \
    + "-i *<INFRASTRUCTURE>* - Infrastruttura target su cui si desidera creare il topic (DRH/SDH/LDH) -> TODO: TRK" + "\n" \
    + "-s <RETENTION_MS> - Retention (in millisecondi) dei dati contenuti su Kafka" + "\n" \
    + "-t *<TOPIC>* - Nome del topic" + "\n"
    print(usage_msg_txt)

    write_log(" | INFO | "+usage_msg_txt,file_log)

    write_log(" | ERROR | Uno o piu' vincoli di esecuzione non sono stati rispettati. Si prega di rieseguire lo script con i parametri corretti in input.",file_log)

    return usage_msg_txt
#
def validate_topic_name(topic_name,file_log,INFRASTRUCTURE):

    import configparser
    #
    config = configparser.RawConfigParser()
    file_ini = "crea-topic.ini"
    config.read(file_ini)
    NUMBER_OCC_FIND_CAR = int(config.get('COMMON', 'NUMBER_OCC_FIND_CAR'))
    FIND_CAR = config.get('COMMON', 'FIND_CAR')
    LIST_CAR = config.get('COMMON', 'LIST_CAR')

    #il nome del topic deve contenere esattamente 4 underscore "_"
    #
    cc=0
    cp=0
    cv=0
    # cicla la lista dei caratteri da ricercare per l'esclusione
    for a in topic_name:
        if a == FIND_CAR:
            cc = cc+1

        if LIST_CAR.find(a) >= 0:
           #print("tovato car: ",a,LIST_CAR.find(a))
           cp = cp+1
    if cc != NUMBER_OCC_FIND_CAR:
        #print("cc",cc,NUMBER_OCC_FIND_CAR)
        write_log(" | ERROR | Il nome del topic non contiene "+str(NUMBER_OCC_FIND_CAR)+" caratteri "+'"_"'+". Rivedere lo standard di nomenclatura.",file_log)
    #
    # il nome del topic non puo' contenere punti "."
    #
    if cp > 0:
        write_log(" | ERROR | Il nome del topic contiene il caratteri speciali " + '"'+LIST_CAR+'"' + ". Rivedere lo standard di nomenclatura.",file_log)
    #
    #il nome del topic deve iniziare con il nome infrastruttura
    #
    len_inf = len(INFRASTRUCTURE)
    sub_inf = topic_name[0:len_inf]
    if sub_inf != INFRASTRUCTURE:
        cv=1
        write_log(" | ERROR | Il nome del topic non inizia per il nome dell'infrastruttura." + " Rivedere lo standard di nomenclatura.",file_log)

    if (cp+cv) > 0 or cc != NUMBER_OCC_FIND_CAR:
        usage_msg(file_log)

    return cp+cv

#
def open_log(file_log):

    import os.path
    #

    if os.path.isfile(file_log):
        # log esiste
        f = open(file_log, "a", newline="\r\n")
    else:
        # log non esiste
        f = open(file_log, "w", newline="\r\n")

    return f

def date_log():

    from datetime import datetime
    cur_date_time = datetime.now()
    date_format_log = cur_date_time.strftime("%d-%m-%Y  %T")

    return date_format_log

def write_log(msg_log, file_log):

    f = open_log(file_log)
    #
    f.write(date_log() + msg_log + "\n")
    f.close()
    print(date_log() + msg_log + "\n")

    return 0

def CTRL_FilE_LOG():
    from pathlib import Path
    import os.path
    import shutil
    import configparser

    config = configparser.RawConfigParser()
    file_ini = "crea-topic.ini"
    config.read(file_ini)
    # gestione logs
    LOGPATH = config.get('COMMON', 'LOGPATH')
    LOGNAME1 = config.get('COMMON', 'LOGNAME1')
    LOGNAME2 = config.get('COMMON', 'LOGNAME2')
    LOGNAME3 = config.get('COMMON', 'LOGNAME3')
    MAX_DIM_FILE_BYTE = int(config.get('COMMON', 'MAX_DIM_FILE_BYTE'))

    if not os.path.exists(LOGPATH + LOGNAME1):
        Path(LOGPATH + LOGNAME1).touch()

    size_log  = os.path.getsize(LOGPATH + LOGNAME1)
    if size_log > MAX_DIM_FILE_BYTE:
        if os.path.exists(LOGPATH + LOGNAME3):
            os.remove(LOGPATH + LOGNAME3)
            shutil.move(LOGPATH + LOGNAME2,LOGPATH + LOGNAME3)
            shutil.move(LOGPATH + LOGNAME1, LOGPATH + LOGNAME2)
        elif  os.path.exists(LOGPATH + LOGNAME2):
            shutil.move(LOGPATH + LOGNAME2, LOGPATH + LOGNAME3)
            shutil.move(LOGPATH + LOGNAME1, LOGPATH + LOGNAME2)
        elif  os.path.exists(LOGPATH + LOGNAME1):
            shutil.move(LOGPATH + LOGNAME1, LOGPATH + LOGNAME2)
        else:
            Path(LOGPATH + LOGNAME1).touch()


        #size_f = os.path.getsize(file_log)
        # os.remove(file_log)

    # inserire gestione riciclo errore file in base alla dim. > 1000000
    LOGNAME_curr = LOGPATH + LOGNAME1

    return LOGNAME_curr