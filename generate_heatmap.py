#!/usr/bin/env python

import pylab as pl
import numpy as np
import os
import csv
import sys
sys.path.append("/home/szh41/oxford-svn/utility")
sys.path.append("/Users/joezhu/oxford-svn/utility")
sys.path.append("/home/joezhu/oxford-svn/utility")
import ms2something as ms


## @ingroup group_compare_psmc
def psmc_XYZ( prefix ):
    print "./grep_prob.sh " + prefix
    os.system("./grep_prob.sh " + prefix)
   
    spacing  = 50        
    site_file = open( prefix + "Site", 'r')
    site = []
    line_index = 0
    for line in site_file:
        if line_index % spacing == 0 : site.append(int(line.strip()))
        line_index += 1;
    site_file.close()    
    time_file = open( prefix + "Time", 'r')
    time = []
    for line in time_file:
        time.append(float(line.strip()))
    time_file.close()
    X, Y = np.meshgrid( site, time )
    Z = []
    probability_file = open( prefix + "probability", 'r')
    line_index = 0
    for line in probability_file:
        if line_index % spacing == 0 : Z.append([float(x) for x in line.split()]); #xticks.append(line_index)
        line_index += 1
    probability_file.close()
    myarray = np.asarray(Z).transpose()
    return X, Y, myarray, site, time



## @ingroup group_compare_psmc
def psmc_figure(cum_change, tmrca, position, prefix):
    X, Y, Z, site, time = psmc_XYZ( prefix )
    fig = pl.figure(figsize=(24,7)) 
    pl.pcolor(X, Y, Z, vmin=0, vmax=0.15)    
    my_axes = fig.gca()
    #ylabels = ["%.4g" % (float(y)*2 * default_pop_size) for y in my_axes.get_yticks()]
    ylabels = ["%.4g" % (float(y)) for y in my_axes.get_yticks()]
    my_axes.set_yticklabels(ylabels)
    
    pl.colorbar()   
    pl.step(cum_change, [x*2 for x in tmrca] , color = "red", linewidth=5.0) # becasue x is generated by ms, which is scaled to 4N0, psmc scale to 2N0. Thereofore, needs to multiply by 2
    #pl.step(cum_change, [x for x in tmrca] , color = "red", linewidth=5.0)    
    pl.plot(position, [0.9*max(time)]*len(position), "wo")
    pl.axis([0, max(site) , 0, max(time)])
    pl.title("PSMC heat map")
    pl.xlabel("Sequence base")
    #pl.ylabel("TMRCA (generation)")
    pl.ylabel("TMRCA (2N0)")
    pl.savefig(prefix + "psmc_heat" + ".png")
    print "done"
    pl.close()
    

## @ingroup group_compare_pfarg            
def read_pfARG_data( file_name ):
    pfARG_data = []
    base = []

    #pfARG_data_file = open(file_name, "r")    
    #for line in pfARG_data_file:
        #dummy = [float(x) for x in line.split("\t")]
        #print dummy
        #base.append(dummy.pop(0))
        #pfARG_data.append(dummy)        
    #pfARG_data_file.close()

    with open(file_name, 'rb') as csvfile:
        spamreader = csv.reader(csvfile, delimiter='\t')
        for row in spamreader:
            dummy = [float(x) for x in row]
            base.append(dummy.pop(0))
            pfARG_data.append(dummy)
    
    return pfARG_data, base


## @ingroup group_compare_pfarg            
def makeHeatmatrix(x, y, WEIGHT, TMRCA):
    xlength = len(x)
    ylength = len(y)
    WEIGHT = np.array(WEIGHT)
    TMRCA  = np.array(TMRCA)
    Z = []
    for xi in range(xlength):
        weight = []
        for wi in range(len(WEIGHT[0])):
            weight.append(WEIGHT[xi][wi])
        
        tmrca = []
        for ti in range(len(TMRCA[0])):
            tmrca.append(TMRCA[xi][ti])
                
        z = []
        zindx = ylength - 2
        upper = y[ zindx+1 ];
        
        while zindx >= 0 :
            lower = y[zindx]
            zcell_sum = 0
            for it in range(len(tmrca)):
                if lower < tmrca[it] <= upper:
                    zcell_sum += weight[it]
            z.append(float(zcell_sum))
            zindx=zindx-1;
            upper=lower;
        z.reverse()
        zcolsum = 0
        for zi in z: zcolsum += zi
        #z = [ (zi / zcolsum)**0.45 for zi in z] # For better presentation
        z = [ (zi / zcolsum) for zi in z]
        Z.append(z)
    return np.asarray(Z).transpose()


## @ingroup group_compare_pfarg            
def pfARG_XYZ( prefix ):
    WEIGHT, x = read_pfARG_data( prefix + "WEIGHT" )
    TMRCA, x  = read_pfARG_data( prefix + "TMRCA" )
    #default_pop_size = 10000
    #TMRCA_max = 10 * default_pop_size
    TMRCA_max = 2
    numof_y = 50; # number of grids on the TMRCA (y-axis)
    y = np.linspace(0, TMRCA_max, numof_y)
    Z = makeHeatmatrix(x, y, WEIGHT, TMRCA)
    X, Y = np.meshgrid( x, y )
    return X, Y, Z, x, y


## @ingroup group_compare_pfarg            
def pfARG_figure(cum_change, tmrca, position, prefix):
    X, Y, Z, site, time = pfARG_XYZ( prefix )
    
    fig = pl.figure(figsize=(24,7)) 
    pl.pcolor(X, Y, Z, vmin=0, vmax=0.15)
    my_axes = fig.gca()
    ylabels = ["%.4g" % (float(y)) for y in my_axes.get_yticks()]
    my_axes.set_yticklabels(ylabels)
    
    pl.colorbar()
    #pl.step(cum_change, [x*4*default_pop_size for x in tmrca] , color = "red", linewidth=5.0)
    pl.step(cum_change, tmrca , color = "red", linewidth=5.0)
    pl.plot(position, [0.9*max(time)]*len(position), "wo")    
    pl.axis([min(site), max(site) , 0, max(time)])
    pl.title("PFPSMC heat map")
    pl.xlabel("Sequence base")
    #pl.ylabel("TMRCA (generation)")
    pl.ylabel("TMRCA (4N0)")
    pl.savefig( prefix + "pfARG_heat" + ".png")
    pl.close()


def get_cum_change( file_name ):
    change_file = open( file_name, "r" )
    cum_change = [0]
    for line in change_file:
        cum_change.append( cum_change[len(cum_change)-1] + int(line.strip()))
    change_file.close()
    return cum_change    


def get_tmrca( file_name ):
    tmrca_file = open( file_name, "r")
    tmrca = [0]
    for line in tmrca_file:
        tmrca.append(float(line.strip())) 
    tmrca_file.close()
    return tmrca


## @ingroup group_compare_dical
def extract_diCal_time ( prefix ):
    file_name = prefix + "diCalout"
    dc_file = open( file_name, "r")
    for line in dc_file:
        if len( line.split() ) == 0: continue # Skipping the empty lines
        if ( line.split()[0] == "decoding" ) & (line.split()[1] == "hap" ):
            break
    site = []
    absorptionTime = []
    for line in dc_file:
        if ( line.split()[0] == "finished" ) & (line.split()[1] == "hap" ):
            break
        site.append ( float(line.split()[2]) ) 
        absorptionTime.append ( float(line.split()[3]) )     
    dc_file.close()
    return site, absorptionTime


## @ingroup group_compare_dical            
def diCal_figure (cum_change, tmrca, position, prefix):
    tmrca = [x*2 for x in tmrca] # convert tmrca from unit of 4Ne to 2Ne
    site, absorptionTime = extract_diCal_time ( prefix )
    maxtime = max( max(absorptionTime), max(tmrca) )
    
    fig = pl.figure(figsize=(24,7)) 
    pl.plot(site, absorptionTime, color = "green", linewidth=3.0)
    pl.step(cum_change, tmrca, color = "red", linewidth=5.0)
    pl.plot(position, [maxtime*1.05]*len(position), "bo")    
    pl.axis([min(site), max(site) , 0, maxtime*1.1])
    pl.title("Dical Absorption time (Green)")
    pl.xlabel("Sequence base")
    pl.ylabel("TMRCA (2N0)")
    pl.savefig( prefix + "diCal_absorption_time" + ".png")
    pl.close()


## @ingroup group_compare_dical
def diCal_lines (arg1, arg2):
    prefix = arg1
    seqlen = int(arg2)
    cum_change = get_cum_change ( prefix + "mschange" )
    tmrca = get_tmrca ( prefix + "mstmrca")
    position = ms.get_position ( seqlen, prefix + "position")
    diCal_figure(cum_change, tmrca, position, prefix)


## @ingroup group_compare_pfarg            
def pfARG_heat (arg1, arg2):
    prefix = arg1
    seqlen = int(arg2)
    cum_change = get_cum_change ( prefix + "mschange" )
    tmrca = get_tmrca ( prefix + "mstmrca")
    position = ms.get_position ( seqlen, prefix + "position")
    pfARG_figure(cum_change, tmrca, position, prefix)


def pfARG_survivor_XYZ( prefix ):
    Z, x = read_pfARG_data( prefix + "SURVIVOR" )
    numof_y = len(Z[0]); # number of grids on the (y-axis)
    y = range(numof_y)
    Z= np.array(np.transpose(Z))
    X, Y = np.meshgrid( x, y )
    return X, Y, Z, x, y

def pfARG_survivor ( prefix ):
    X, Y, Z, site, particles = pfARG_survivor_XYZ( prefix )    
    fig = pl.figure(figsize=(24,7)) 
    pl.pcolor(X, Y, Z)
    my_axes = fig.gca()
    pl.axis([min(site), max(site) , 0, max(particles)])
    pl.title("PFPSMC Survivors")
    pl.xlabel("Sequence base")
    #pl.ylabel("TMRCA (generation)")
    pl.ylabel("Particles")
    pl.savefig( prefix + "pfARG_survivor" + ".png")
    pl.close()


    
## @ingroup group_compare_psmc
def psmc_heat (arg1, arg2):
    prefix = arg1
    seqlen = int(arg2)
    cum_change = get_cum_change ( prefix + "mschange" )
    tmrca = get_tmrca ( prefix + "mstmrca")
    position = ms.get_position ( seqlen, prefix + "position")
    psmc_figure(cum_change, tmrca, position, prefix)    


if __name__ == "__main__":
    try:
        pfARG_heat (sys.argv[1], sys.argv[2])
        psmc_heat  (sys.argv[1], sys.argv[2])
    except:
        print "something wrong"
        sys.exit(1)
