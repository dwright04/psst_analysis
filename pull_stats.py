import MySQLdb
import pyfits
import utils, datetime, sys
import numpy as np
from os import listdir
from os.path import isfile, join
from astropy.time import Time

PATH = "/psdb2/tc_logs/ps13pi/"
THRESHOLD1 = 0.469
THRESHOLD2 = 0.436
DATE_CHANGE = datetime.datetime(2015, 5, 25, 00, 00, 00)
START_DATE = datetime.datetime(2015, 3, 16, 00, 00, 00)

def get_files(path):
    return [f for f in listdir(path) if isfile(join(path,f))]

def gen_dates(start_date):
    for n in range(int((datetime.datetime.today() - start_date).days)):
        yield start_date + datetime.timedelta(days=n)

def extract_ml_stats_sql(conn, date):

    d1 = date + datetime.timedelta(days=1)
    if date < DATE_CHANGE:
        threshold = THRESHOLD1
    else:
        threshold = THRESHOLD2
    try:                                                                                       
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)                                       
        cursor.execute("""select count(*) from tcs_transient_objects where date_inserted >=\'%s\' and date_inserted < \'%s\' and confidence_factor is not NULL"""  % (str(date), str(d1)))
        resultSet1 = cursor.fetchone()                                                         
        cursor.close ()                                                                        
    except MySQLdb.Error, e:                                                                   
        print "Error %d: %s" % (e.args[0], e.args[1])                                          
        sys.exit(1)

    try:
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("""select count(*) from tcs_transient_objects\
                           where date_inserted >=\'%s\' and date_inserted < \'%s\'\
                           and confidence_factor < %s""" \
                           % (str(date), str(d1), threshold))
        resultSet2 = cursor.fetchone()
        cursor.close ()
    except MySQLdb.Error, e:
        print "Error %d: %s" % (e.args[0], e.args[1]) 
        sys.exit(1)
    try:
        return float(resultSet1["count(*)"]), float(resultSet2["count(*)"]), threshold
    except ZeroDivisionError:
        return 0

def extract_ml_stats(files):
    ml_stats = {}
    for file in files:
        if "machine_learning" in file:
            if not ml_stats.has_key(file.split("_")[2]):
                ml_stats[file.split("_")[2]] = \
                {"total":0,"rejected":0, "threshold":0}
            input = open(PATH+file,"r")
            for line in input.readlines():
               if "TOTAL OBJECTS TO UPDATE" in line:
                   total = float(line.split(" ")[-1])
                   ml_stats[file.split("_")[2]]["total"] += total
               if "Number of objects below RB Factor of" in line:
                   rejected = float(line.split(" ")[-1])
                   threshold = float(line.split(" ")[7])
                   ml_stats[file.split("_")[2]]["rejected"] += rejected
                   ml_stats[file.split("_")[2]]["threshold"] = threshold
    return ml_stats

def extract_ghosts_sql(conn, date):
    d1 = date + datetime.timedelta(days=1)

    try:                                                                                       
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)                                       
        cursor.execute("""select count(*) from tcs_transient_objects where date_inserted >= \'%s\' and date_inserted < \'%s\' and local_comments like \'%s\';"""  % (str(date), str(d1), "%Ghost%"))
        resultSet1 = cursor.fetchone()                                                         
        cursor.close ()                                                                        
    except MySQLdb.Error, e:                                                                   
        print "Error %d: %s" % (e.args[0], e.args[1])                                          
        sys.exit(1)

    try:
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("""select count(*) from tcs_transient_objects where date_inserted >= \'%s\' and date_inserted < \'%s\' and local_comments like \'%s\'and observation_status = \'mover\';""" % (str(date), str(d1), "%Ghost%"))
        resultSet2 = cursor.fetchone()
        cursor.close ()
    except MySQLdb.Error, e:
        print "Error %d: %s" % (e.args[0], e.args[1]) 
        sys.exit(1)

    return float(resultSet1["count(*)"]), float(resultSet2["count(*)"])

def extract_ghosts(files):
    ghost_stats = {}
    for file in files:
        if "ghost_checker" in file:
            if not ghost_stats.has_key(file.split("_")[2]):
                ghost_stats[file.split("_")[2]] = {"total":0,"movers":0}
            input = open(PATH+file,"r")
            for line in input.readlines():
                if "mover" in line and "True" in line:
                    ghost_stats[file.split("_")[2]]["movers"] += 1
                if "Number of ghosts trashed" in line:
                    total = float(line.split(" ")[-1])
                    ghost_stats[file.split("_")[2]]["total"] += total
    return ghost_stats

def extract_movers_sql(conn, date):
    d1 = date + datetime.timedelta(days=1)

    try:                                                                                       
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)                                       
        cursor.execute("""select count(*) from tcs_transient_objects where date_inserted >= \'%s\' and date_inserted < \'%s\' and observation_status = \'mover\';"""  % (str(date), str(d1)))
        resultSet1 = cursor.fetchone()                                                         
        cursor.close ()                                                                        
    except MySQLdb.Error, e:                                                                   
        print "Error %d: %s" % (e.args[0], e.args[1])                                          
        sys.exit(1)

    return float(resultSet1["count(*)"])

def extract_movers(files):
    movers_stats = {}
    for file in files:
        if "ephemerides_check" in file:
            if not movers_stats.has_key(file.split("_")[2]):
                movers_stats[file.split("_")[2]] = {"total":0}
            input = open(PATH+file,"r")
            for line in input.readlines():
                if "TOTAL NUMBER OF MOVERS" in line:
                    total = float(line.split(" ")[-1])
                    movers_stats[file.split("_")[2]]["total"] += total
    return movers_stats

def extract_list(conn, date, l):

    d1 = date + datetime.timedelta(days=1)

    try:
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("""select count(*) from tcs_transient_objects\
                           where date_inserted >=\'%s\' and date_inserted < \'%s\'\
                           and detection_list_id = %s and observation_status != \'mover\'""" \
                           % (str(date), str(d1), l))
        resultSet = cursor.fetchone()
        cursor.close ()
    except MySQLdb.Error, e:
        print "Error %d: %s" % (e.args[0], e.args[1]) 
        sys.exit(1)

    return resultSet["count(*)"]

def extract_eyeball_movers(conn, date, l):

    d1 = date + datetime.timedelta(days=1)
    try:
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("""select count(*) from tcs_transient_objects\
                           where date_inserted >=\'%s\' and date_inserted < \'%s\'\
                           and detection_list_id = %s and observation_status=\'mover\'""" \
                           % (str(date), str(d1), l))

        resultSet = cursor.fetchone()
        cursor.close ()
    except MySQLdb.Error, e:
        print "Error %d: %s" % (e.args[0], e.args[1]) 
        sys.exit(1)
    return resultSet["count(*)"]

def extract_eyeballing(conn,dates):
    lists = ["1", "2", "3", "5"]
    eyeballing_stats = {}
    for date in dates:
        if not eyeballing_stats.has_key(date):
            eyeballing_stats[date] = {"promoted":0, "atticpossible":0, "movers":0}
        for l in lists:
            if l == "1" or l =="2":
                eyeballing_stats[date]["promoted"] += extract_list(conn,date,l)
            elif l == "3" or l == "5":
                eyeballing_stats[date]["atticpossible"] += extract_list(conn,date,l)
                eyeballing_stats[date]["movers"] += extract_eyeball_movers(conn,date,l)
    return eyeballing_stats

def extract_seeing(dates):
    seeing_stats = {}
    for date in dates:
        seeing_stats[date] = {"seeing":0}
        
        t = Time(date,scale="utc")
        mjd = str(int(t.mjd)-1)
        
        path = "/psdb2/images/ps13pi/"
        try:
            files = get_files(path+mjd+"/")
        except OSError:
            print date, path+mjd+"/"
            continue
        seeing = []
        fits_files = []
        for file in files:
            if "fits" not in file or "diff" not in file:
                continue
            if "460000000" in file:
                continue
            fits_files.append(file)
        order = np.random.permutation(len(fits_files))
        fits_files = np.array(fits_files)[order][:100]
        for file in fits_files:
            hdulist = pyfits.open(path+mjd+"/"+file)
            seeing.append(float(hdulist[1].header["CHIP.SEEING"]))
        seeing_stats[date]["seeing"] += np.mean(seeing)
    return seeing_stats
    

def main():
    """
    stat_files = get_files(PATH)
    
    ml_stats = extract_ml_stats(stat_files)
    ghost_stats = extract_ghosts(stat_files)
    movers_stats = extract_movers(stat_files)
    """
    conn = utils.dbConnect("psdb2", "dew", "", "ps13pi")
    if not conn:
        print "Cannot connect to the database"
        exit(1)
    output = open("psst_machine_learning_stats.csv","w")                                       
    output.write("#date,total,ml_rejected,threshold,ghost_total,ghost_movers,total_movers,promoted,atticpossible,recoveredmovers,seeing\n")

    eyeballing_stats = extract_eyeballing(conn, gen_dates(START_DATE))
    seeing_stats = extract_seeing(gen_dates(START_DATE))

    for date in gen_dates(START_DATE):
        total, ml_rejected, threshold = extract_ml_stats_sql(conn,date)
        ghosts_total, ghost_movers = extract_ghosts_sql(conn, date)
        total_movers = extract_movers_sql(conn, date)
        try:
            promoted = eyeballing_stats[date]["promoted"]
        except KeyError:
            promoted = 0
        try:
            possible_attic = eyeballing_stats[date]["atticpossible"]
        except KeyError:
            possible_attic = 0
        try:
             recovered_movers = eyeballing_stats[date]["movers"]
        except KeyError:
             possible_movers = 0
        try:
            seeing = seeing_stats[date]["seeing"]
        except KeyError:
            seeing = 0

        output.write("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n"%(date,total,ml_rejected,\
        threshold,ghosts_total,ghost_movers,total_movers,promoted,possible_attic,\
        recovered_movers,seeing))
    output.close()
    """
    output = open("psst_machine_learning_stats.csv","w")
    output.write("#date,total,ml_rejected,threshold,ghost_total,ghost_movers,total_movers,promoted,atticpossible,recoveredmovers,seeing\n")
    for key in ml_stats.keys():
        print key
        total = ml_stats[key]["total"]
        ml_rejected = ml_stats[key]["rejected"]
        threshold = ml_stats[key]["threshold"]
        try:
            ghosts_total = ghost_stats[key]["total"]
        except KeyError:
            ghosts_total = 0
        try:
            ghost_movers = ghost_stats[key]["movers"]
        except KeyError:
            ghost_movers = 0
        try:
            total_movers = movers_stats[key]["total"]
        except KeyError:
            total_movers = 0
        try:
            promoted = eyeballing_stats[key]["promoted"]
        except KeyError:
            promoted = 0
        try:
            possible_attic = eyeballing_stats[key]["atticpossible"]
        except KeyError:
            possible_attic = 0
        try:
             recovered_movers = eyeballing_stats[key]["movers"]
        except KeyError:
             possible_movers = 0
        try:
            seeing = seeing_stats[key]["seeing"]
        except KeyError:
            seeing = 0

        output.write("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n"%(key,total,ml_rejected,threshold,ghosts_total,ghost_movers,total_movers,promoted,possible_attic,recovered_movers,seeing))
    output.close()
    """
if __name__ == "__main__":
    main()
