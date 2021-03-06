import datetime
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import YearLocator, MonthLocator, DateFormatter
from matplotlib.patches import Rectangle
import pandas as pd

input = open("psst_machine_learning_stats.csv","r")

dates = []
totals = []
ml_rejected = []
rejected_fraction = []
ghost_total = []
ghost_movers = []
total_movers = []
#promoted = []
atticpossible = []
possibelemovers = []
recovered_movers = []
FPR = []
mean_seeing = []
tot_movers = []
rec_movers = []
for line in input.readlines():
    if "#" in line:
        continue
    info=line.split(",")
    date=info[0]
    #print date

    dates.append(datetime.datetime.strptime(date,"%Y-%m-%d %H:%M:%S"))
    totals.append(float(info[1]))
    if float(info[2]) == 0:
        dates.remove(dates[-1])
        continue
    ml_rejected.append(float(info[2]))
    mean_seeing.append(float(info[10]))
    try:
        rejected_fraction.append(float(info[2])/float(info[1]))
    except ZeroDivisionError:
        #rejected_fraction.append(0)
        dates.remove(dates[-1])
        mean_seeing.remove(mean_seeing[-1])
        continue
    try:
        if float(info[9])/(float(info[6]) - float(info[5])) > 1 or float(info[9])/(float(info[6]) - float(info[5])) < 0:
            rejected_fraction.remove(rejected_fraction[-1])
            dates.remove(dates[-1])
            mean_seeing.remove(mean_seeing[-1])
            continue
        recovered_movers.append(float(info[9])/(float(info[6]) - float(info[5])))
        tot_movers.append(float(info[6]))
        rec_movers.append(float(info[9]))
    except ZeroDivisionError:
        #recovered_movers.append(0)
        rejected_fraction.remove(rejected_fraction[-1])
        dates.remove(dates[-1])
        mean_seeing.remove(mean_seeing[-1])
        continue
    to_eyeball = float(info[1]) - float(info[2]) - float(info[4]) - float(info[9])
    #print to_eyeball
    promoted = float(info[7])
    #print promoted
    possible_attic = float(info[8])
    #print possible_attic
    try:
        fpr = (to_eyeball - promoted - possible_attic) / (float(info[1]) + (to_eyeball - promoted - possible_attic))
        if fpr < 0:
            fpr = 0
        FPR.append(fpr)
    except ZeroDivisionError:
        #FPR.append(0)
        rejected_fraction.remove(rejected_fraction[-1])
        recovered_movers.remove(recovered_movers[-1])
        dates.remove(dates[-1])
        mean_seeing.remove(mean_seeing[-1])
print np.mean (rejected_fraction)
"""
print len(dates)
print len(rejected_fraction)
print len(recovered_movers)
print len(FPR)
"""
c1 = "#AA4472"
c2 = "#8CBA80"
c3 = "#658E9C"
c4 = "#4D5382"
c5 = "#514663"
output = [list(x) for x in zip(*sorted(zip(dates, FPR), key=lambda pair: pair[0]))]
output1 = [list(x) for x in zip(*sorted(zip(dates, recovered_movers), key=lambda pair: pair[0]))]
#output2 = [list(x) for x in zip(*sorted(zip(dates, rejected_fraction), key=lambda pair: pair[0]))]

font = {"size"   : 26}
plt.rc("font", **font)
plt.rc("legend", fontsize=22)
#plt.rc('text', usetex=True)
plt.rc('font', family='serif')

fig = plt.figure()
#ax =fig.add_subplot(211)
ax =fig.add_subplot(111)
#ax.plot(dates,totals,"o",color="#3A86FF",markeredgecolor="none")
#ax.plot(dates,ml_rejected,"o",color="#FF006E",markeredgecolor="none")

ax.set_ylim(ymin=-0.02,ymax=1.02)
plt.xticks(rotation=50)


ax2 = ax.twinx()
#print len(dates)
#print len(mean_seeing)
seeing = [list(x) for x in zip(*sorted(zip(dates, mean_seeing), key=lambda pair: pair[0]))]

d1 = [d for d in dates if d<=datetime.datetime(2015,05,25,00,00,00)]
seeing1 = [seeing[1][i] for i in range(len(seeing[0])) if seeing[0][i] <= datetime.datetime(2015,05,25,00,00,00)]
l4 = ax2.plot([d1[0],d1[-1]],[np.median(seeing1),np.median(seeing1)],color=c4, lw=3, label="median seeing")

ax2.add_patch(Rectangle((np.min(d1),np.mean(seeing1)-np.std(seeing1)), (datetime.datetime(2015,05,25,00,00,00)-np.min(d1)).days, 2*np.std(seeing1), color=c3, alpha=0.25))

d2 = [d for d in dates if d>=datetime.datetime(2015,05,25,00,00,00)]
seeing2 = [seeing[1][i] for i in range(len(seeing[0])) if seeing[0][i] >= datetime.datetime(2015,05,25,00,00,00)]
print len(seeing[0])
print len(seeing2)
index = seeing2.index(0)
print index
seeing2.remove(seeing2[index])
d2.remove(d2[index])
ax2.plot([d2[0],d2[-1]],[np.median(seeing2),np.median(seeing2)],color=c4, lw=3)

ax2.add_patch(Rectangle((np.min(d2),np.mean(seeing2)-np.std(seeing2)), (np.max(d2) - datetime.datetime(2015,05,25,00,00,00)).days, 2*np.std(seeing2), color=c3, alpha=0.25))

ax2.plot(d1,seeing1,"o",color=c4,markeredgecolor="none",ms=10)
ax2.plot(d2,seeing2,"o",color=c4,markeredgecolor="none",ms=10)

ax2.set_ylim(-0.1,10)

ax.plot([datetime.datetime(2015,05,25,00,00,00),datetime.datetime(2015,05,25,00,00,00)],[-0.1,1.1],"k--")
#ax.plot([np.min(dates),datetime.datetime(2015,05,25,00,00,00)], [0.1,0.1], "k--", color=c1, lw=2)
ax.plot([datetime.datetime(2015,05,25,00,00,00),max(dates)], [0.05,0.05], "k--", color=c1, lw=2)
#ax.plot([np.min(dates),datetime.datetime(2015,05,25,00,00,00)], [0.961,0.961], "k--", color=c2, lw=2)
ax.plot([datetime.datetime(2015,05,25,00,00,00),max(dates)], [0.968,0.968], "k--", color=c2, lw=2)

ax.plot(dates,recovered_movers,"o",color=c2,markeredgecolor="none", ms=10)
l1 = ax.plot(output1[0],output1[1],"-",color=c2,label="fraction recovered movers",lw=3)

#ax.plot(dates,rejected_fraction,"o",color=c5,markeredgecolor="none", ms=10)
#l2 = ax.plot(output2[0],output2[1],"-",color=c5,label="fraction rejected by ML",lw=3)

ax.plot(dates,FPR,"o",color=c1,markeredgecolor="none", ms=10)
l3 = ax.plot(output[0],output[1],"-",color=c1,label="FPR",lw=3)

ax.set_ylabel("Normalised Counts")
ax.set_xlabel("Date")
ax2.set_ylabel("Seeing [pixels]")
lines = l1+l3+l4
labels = [l.get_label() for l in lines]
plt.legend(lines, labels,bbox_to_anchor=(0.3, 0.25), loc=5, borderaxespad=0.)

start = min(dates)
stop = max(dates)
date_list = pd.date_range(start, stop, freq="W").tolist()
date_list.append(min(dates))
date_list.append(max(dates))
#date_list.remove(datetime.datetime(2015,8,02,00,00,00))
ax.xaxis.set_ticks(date_list)
for tick in ax.xaxis.get_major_ticks():
    tick.label.set_fontsize(22)

ax.text(datetime.datetime(2015,05,23,00,00,00), 0.3, "2015-05-25", rotation=90, size=22)
#ax.text(datetime.datetime(2015,03,18,00,00,00), 0.11, "0.1", color=c1, size=22)
ax.text(datetime.datetime(2015,05,27,00,00,00), 0.06, "0.05", color=c1, size=22)
#ax.text(datetime.datetime(2015,04,21,00,00,00), 0.971, "0.961", color=c2, size=22)
ax.text(datetime.datetime(2015,05,28,00,00,00), 0.978, "0.968", color=c2, size=22)
ax2.text(datetime.datetime(2015,03,18,00,00,00), np.median(seeing1)+0.1, "%.3f" % np.median(seeing1),color=c4, size=22)
ax2.text(datetime.datetime(2015,05,28,00,00,00), np.median(seeing2)+0.1, "%.3f" % np.median(seeing2),color=c4, size=22)

yearsFmt = DateFormatter('%Y-%m-%d')
ax.xaxis.set_major_formatter(yearsFmt)
"""
ax =fig.add_subplot(212)
#ax.plot(dates,totals,"o",color="#3A86FF",markeredgecolor="none")
#ax.plot(dates,ml_rejected,"o",color="#FF006E",markeredgecolor="none")
ax.plot(dates,mean_seeing,"o",color="#FB5607", markeredgecolor="none")
ax.plot(dates, 4.425*np.ones((len(dates,))),ls="-",color="#FB5607") #4.425 mean from 3pi training set
ax.plot([datetime.datetime(2015,05,25,00,00,00),datetime.datetime(2015,05,25,00,00,00)],[0,8],"k--")
yearsFmt = DateFormatter('%Y-%m-%d')
ax.xaxis.set_major_formatter(yearsFmt)
plt.xticks(rotation=70)
"""
plt.show()

fig = plt.figure()

ax1 = fig.add_subplot(111)
index1 = [dates.index(d) for d in d1]
index2 = [dates.index(d) for d in d2]
#ax1.scatter(seeing1, np.array(recovered_movers)[index1], color="#3A86FF")
#ax1.scatter(seeing2, np.array(recovered_movers)[index2], color="#FF006E")
ax1.scatter(seeing1, np.array(FPR)[index1], color="#3A86FF", label="classifier1")
ax1.scatter(seeing2, np.array(FPR)[index2], color="#FF006E", label="classifier2")
ax1.plot([3.5,3.5],[-0.2,0.4],"k--", lw=3)
ax1.set_xlabel("seeing [pixels]")
ax1.set_ylabel("FPR")
ax1.set_ylim(-.05,.15)
plt.legend()
#ax2 = fig.add_subplot(212)
#ax2.scatter(seeing1+seeing2,output1[1])

#fig1 = plt.figure()
#ax1 = fig1.add_subplot(211)
#ax1.scatter(tot_movers,recovered_movers)
plt.show()
