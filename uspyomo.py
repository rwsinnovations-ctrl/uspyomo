#source ~/flaskproject/flaskprojectenv/bin/activate
# #export FLASK_APP=us.py
#export FLASK_ENV=development
#sudo password is ir2113 for apt-get
#chrome.exe --user-data-dir="C:/Chrome dev session" --disable-web-security
#The old hard drive wsl files are readable at:
#"E:\Users\RWS\AppData\Local\Packages\CanonicalGroupLimited.UbuntuonWindows_79rhkp1fndgsc\LocalState\rootfs\home\rws\"
 
#from flask_session import Session#april 28 2021
#june 6 2021 to run in windows:  ./venv/scripts/activate
#set FLASK_APP=us-39-load_supp.py
#2022-05-20 call tree 
#US1 page load with user directory
#   UScplex1
#       refreshconsdf
#       get_chosen_foods() - also loads nut_data only when cache miss on chosenfoods
#           load_supplements_chosenfoods
#           trimdb
#       refreshnpt
#           load_supplements_npt
#           load_oxalates
#        trimdb
#            mask-chosenfoods1 file read, cache mask
#       refreshconsdf
#       load_supplements
#       load_oxalates
#   refreshnpt if nec
#       trimdb if nec
#       trimdb
#       slackscplex

#US2 ajax call
#   UScplex
#exclude ajax call
#   loaddataset
#   get_chosen_foods    
#pickleexclude ajax call
# from copy import deepcopy
# from socket import SO_EXCLUSIVEADDRUSE
import sys
solver =None
import numpy as np
import pandas as pd# ;print("pandas version=",pd.__version__,"np.vers=",np.__version__)
#import clpy - windows version using cylp

# import flask#; print("flask version",flask.__version__)
# from flask import Flask
# from flask_cors import CORS, cross_origin#may 13 2021 so that I dont have to run chrome with security disabled. added CORS(app )below as well

import pickle
import warnings
# warnings.simplefilter("error")
# warnings.simplefilter("ignore",PendingDeprecationWarning)
# warnings.simplefilter("ignore",FutureWarning)
# vd='./';2020-05-06 15:23:34 everythong goes to windows side to simplify manual directory ops.


vdroot='c:/Users/Rwsin/Google Drive/US/'
#was vdwin #2020-05-06 09:45:42  the root dir for person file, and html output files respectively
vdroot='g:/My Drive/US/'#was vdwin #2020-05-06 09:45:42  the root dir for person file, and html output files respectively
vdwin2=''

import os
pd.set_option('display.max_colwidth', 1000)#pd.set_option('display.max_colwidth',-1)#pd.set_option('display.max_colwidth',-1 )
pd.set_option('display.max_rows', 400)
usda_home='./sr28asc/'# todo, put this under the root in the windows area 2020-05-06 15:27:09
import json
import pandas as pd
from inspect import currentframe, getframeinfo
pd.options.mode.chained_assignment = 'raise'
pd.options.mode.chained_assignment = None
collist=['NDB_No','FdGrp_Desc','Long_Desc','min_d','max_d','amounts','allmeas','cost']#G2020-06-06 keeping it more simple for now
AMPM=False#check cysteine_deficit slack

chosenfoods=None
chosenfoods_cplex=None
una=None
npt=None
consdf=None
vdwin=None

def get_vdwin():
    if vdwin is None:#try:
    #    vdwin
    #except NameError:
        return(request.args.get('vd'))
    else:
        return vdwin


def load_oxalates():#from jupyter dataframe hacking notebook
    global chosenfoods,chosenfoods_cplex,npt,una
    import pandas as pd
    vdox=vdwin#'G:/My Drive/US/oxalate/'#2022-11-30 putting everything in one dir

    with open(get_vdwin()+"Oxalate Spreadsheet dtd 28 Sep 2019.xlsx", 'rb') as f:
        ox=pd.ExcelFile(f,engine='openpyxl')


        #2023-04-07 need to open as read-only, just caused a days headache having the file open online.next line removed.also its now an xlsx not xls (whytf now ?)
        #ox=pd.ExcelFile(vdox+"Oxalate Spreadsheet dtd 28 Sep 2019.xls")#,engine='xlrd')#ox=pd.read_excel(vd+"Oxalate Spreadsheet dtd 28 Sep 2019.xlsx",engine=None,na_values=['-','Negligible'],sheet_name=None,convertors={'NDB_No':object,'Total Oxalate (mg) per 100g':float})#,dtype={'Total Oxalate (mg) per 100g':float,'NDB_No':object})
        vdfo = pd.concat(ox.parse(ox.sheet_names[1:18],na_values=['','-','Negligible'],dtype={'Total Oxalate (mg) per 100g':float,'NDB_No':object,'Total Soluble Oxalate (mg) per 100g':float}),sort=False)#2024-2-1 sort=False now#april 25 2021 added sort=true to silence warning#.astype({'Total Oxalate (mg) per 100g':float})
    vdfo['NDB_No']=vdfo['NDB_No'].astype({'NDB_No':str})
    vdfo['NDB_No']=vdfo['NDB_No'].str.replace('nan','',regex=False)#;pd.Series.str.replace()#1=vdf.fillna({'NDB_No':''})
    print("vdfo duplicates:",vdfo[vdfo.index.duplicated()])
    vdf1=vdfo[vdfo['NDB_No']!=''].set_index('NDB_No',verify_integrity=True)#)#.index#)#.index#[vdf['NDB_No']!='']['NDB_No']
    #vdf1['TotalOxalate']=vdf1['Total Oxalate (mg) per 100g']
    vdf1['TotalOxalate']=vdf1['Total Oxalate (mg) per 100g']#2023-04-21 calling it what it is, and importing the soluble so that the data is available in the drilldown for food prep

    #2022-04-18 soluble oxalate is actually the problem Total Soluble Oxalate (mg) per 100g
    #vdf1.drop(columns=['Total Oxalate (mg) per 100g'],inplace=True)
    vdf1.drop(columns=['Total Oxalate (mg) per 100g'],inplace=True)

    #print("loading oxalates..",vdf1)
    #vdf[vdf.duplicated(subset=['Item','Serving Size','Serving (g)'],keep='last')]#diagnostic
    #The following line is actually good verification of manual data entry (assigning NDB_No to oxalate spreadsheet food items)
    #print(vdf1[['Item','TotalOxalate']].merge(food_des['Long_Desc'],left_index=True,right_on='NDB_No'))#compare the description side-by-side, ensure correct NDB_No chosen 2021-02-26 15:12:52 todo use confid to assist in that selection
    #imputation
    #print(type(chosenfoods))
    #chosenfoods,chosenfoods_cplex,una=
    get_chosen_foods()#2022-03-13
    npt.drop(columns=['TotalOxalate'],inplace=True)#2023-04-23 npt.update below isnt working bc this column already exists ??

    #thevegs=chosenfoods[chosenfoods['FdGrp_Cd']=='1100'].index.to_list()#june 15 2021 changed ['NDB_No'] to .index for all these
    #npt.loc[npt.index.isin(thevegs),"TotalOxalate"]=0.0;npt.loc[npt.index.isin(thevegs),'Total Soluble Oxalate (mg) per 100g']=0.0#500.0#using maxfromgroups make it feasible to update data incrementally according to relevance
    #thenuts=chosenfoods[chosenfoods['FdGrp_Cd']=='1200'].index.to_list();npt.loc[npt.index.isin(thenuts),"TotalOxalate"]=0.0;npt.loc[npt.index.isin(thenuts),'Total Soluble Oxalate (mg) per 100g']=0.0#100.0
    #thelegs=chosenfoods[chosenfoods['FdGrp_Cd']=='1600'].index.to_list();npt.loc[npt.index.isin(thelegs),"TotalOxalate"]=0.0;npt.loc[npt.index.isin(thelegs),'Total Soluble Oxalate (mg) per 100g']=0.0#10.0#2023-04-21 eyeball average across the spreadsheet
    #thegrains=chosenfoods[chosenfoods['FdGrp_Cd']=='2000'].index.to_list();npt.loc[npt.index.isin(thegrains),"TotalOxalate"]=0.0;npt.loc[npt.index.isin(thegrains),'Total Soluble Oxalate (mg) per 100g']=0.0#30.0
    #some refinement possible here
    #thefruits=chosenfoods[chosenfoods['FdGrp_Cd']=='900'].index.to_list();npt.loc[npt.index.isin(thefruits),"TotalOxalate"]=0.0;npt.loc[npt.index.isin(thefruits),'Total Soluble Oxalate (mg) per 100g']=0.0#10.0
    npt['TotalOxalate']=0.0;npt["Total Soluble Oxalate (mg) per 100g"]=0.0#2024-5-12 next 3 lines for pandas 2.0.3
    npt.update(vdf1["TotalOxalate"])#,errors='raise')
    npt.update(vdf1["Total Soluble Oxalate (mg) per 100g"])#,errors='raise')

    npt['Total Soluble Oxalate (mg) per 100g'].fillna(npt['TotalOxalate'])#2023-04-21 tricky imputation
    npt['TotalOxalate'].fillna(npt['Total Soluble Oxalate (mg) per 100g'])
    npt.fillna({'TotalOxalate':0.0},inplace=True)
    npt.fillna({'Total Soluble Oxalate (mg) per 100g':0.0},inplace=True)

#@app.route('/')
RATIOMETRICS=True
#@app.route('/refreshnpt')#2022-03-14removed from direct access#2021-12-15 moved here from refreshcondf
def refreshnpt():   #feb 1 2021
    global st,chosenfoods,npt,person,AMconsdf,PMconsdf,consdf,una,vdwin,ratiosf,AMPM,nptfull
    #2020-06-10 added read from csv. some loss of precision, and datatypes converted from object to float in many cases
    #npt=pd.read_csv(get_vdwin()+'npt.csv',index_col=0);chosenfoods=pd.read_csv(get_vdwin()+'chosenfoods.csv',index_col=0);consdf=pd.read_csv(get_vdwin()+'consdf.csv',index_col=0);una=pd.read_csv(get_vdwin+'una.csv',index_col=0);st=pd.read_csv(get_vdwin+'st.csv',index_col=0)
    npt=pd.read_csv(get_vdwin()+'npt.csv',index_col=None,dtype={'NDB_No':str});npt.set_index('NDB_No',inplace=True)
    npt['cost']=0.0#2022-06-05 need somethin
    #print("refreshnpt.")
    #consdf=pd.read_excel(get_vdwin +'consdf.xls',engine='openpyxl',index_col=0)#may 10 2021 newest version only opens xls files!
    #refreshconsdf()#moved up -
    
    
    
    #import pdb;pdb.set_trace()
    
    if SUPPLEMENTS:
        load_supplements_npt()#2021-12-15 moved this to before loading ratiometrics
    #return npt#2022-04-13 let the ampm be reachable
    
    
    
    npt.loc['09150','citrate']=192*64.7*1e-4#citrate in grams#lemon
    npt.loc['09152','citrate']=192*64.7*1e-4#citrate in grams#lemon
    npt.loc['09153','citrate']=192*64.7*1e-4#citrate in grams#lemon
    npt.loc['09112','citrate']=192*64.7*1e-4#citrate in grams#grapefuit
    npt.loc['09160','citrate']=192*64.7*1e-4#citrate in grams#lime, not the same as lemon by pretty close
    
    npt.loc['09200','citrate']=192*47.6*1e-4#orange
    npt.loc['09202','citrate']=192*47.6*1e-4#orange
    npt.loc['09205','citrate']=192*47.6*1e-4#orange
    
    npt.loc['09112','citrate']=192*41.57*1e-4#pineapple
    
    npt.loc['02054','786']=104.29#capers kaempferol
    npt.loc['02014','786']=38.6#cumin kaempferol
    npt.loc['02005','786']=38.6#caraway kaempferol
    
    npt.loc['14058','503']=2.0/32*100#isoleucine of whey isolate.
    npt.loc['14058','505']=2.9/32*100#lycine of whey isolate.
    npt.loc['14058','512']=0.6/32*100#histidineof whey isolate.
    npt.loc['14058','504']=3.3/32*100#leucine of whey isolate.
    npt.loc['14058','501']=0.5/32*100#tryptophan of whey isolate.
    npt.loc['14058','502']=2.0/32*100#threonine of whey isolate.
    npt.loc['14058','510']=1.9/32*100#valine of whey isolate.
    npt.loc['14058','mpc']=(0.7+0.8)/32*100#methionine plus cysteine of whey isolate.
    npt.loc['14058','ppt']=(1.1+1.0)/32*100#phenyl + tyrosne of whey isolate.
    
    #npt.loc['48052']['503']=4.1#vital wheat gluten
    #npt.loc['48052']['505']=1.4
    #npt.loc['48052']['512']=1.7
    #npt.loc['48052']['504']=7.2
    #npt.loc['48052']['501']= #tryp
    #npt.loc['48052']['502']=2.8
    #npt.loc['48052']['510']=5.4
    #npt.loc['48052']['mpc']=3.5
    #npt.loc['48052']['ppt']=7.2


#Assessment of the protein quality of the smooth muscle myofibrillar and connective tissue proteins of chicken gizzard
    npt.loc['05024','503']=3.603#chicken gizzard isoleu
    npt.loc['05024','505']=5.279#lys
    npt.loc['05024','512']=1.541#histi
    npt.loc['05024','504']=5.363#leuc
    npt.loc['05024','501']=0.684 #tryp
    npt.loc['05024','502']=3.519#threo
    npt.loc['05024','510']=3.424#valine
    
    npt.loc['05024','506']=2.003#methio
        
    npt.loc['05024','507']=2.004#cyst

    npt.loc['05024','mpc']=4.007
    #phenyl
    npt.loc['05024','ppt']=3.179+2.323
    #Molybdenum
    npt.loc['05028','Mo']=38*100/45#chicken liver 38 ug per 45g
    npt.loc['13327','Mo']=28*100/30# beef liver per 30g
    
    
    #https://nutritionandmetabolism.biomedcentral.com/articles/10.1186/1743-7075-9-67/tables/3
    new_data = {
    'Amino Acid': ['Alanine', 'Arginine', 'Aspartate', 'Cysteine', 'Glutamate + Glutamine', 'Glycine', 'Histidine', 'Isoleucine', 'Leucine', 'Lysine', 'Methionine', 'Phenylalanine', 'Proline', 'Serine', 'Threonine', 'Tryptophan', 'Tyrosine', 'Valine'],
    'Vital Wheat Gluten1': [3.1, 4.7, 4.0, 1.9, 31.7, 3.8, 1.8, 3.0, 6.8, 2.8, 1.9, 4.4, 9.4, 3.9, 2.6, 1.3, 2.4, 4.5],
    'Soy Protein Isolate2g/100 g Protein': [4.0, 7.5, 11.5, 1.3, 19.2, 4.1, 2.5, 4.8, 8.0, 6.3, 1.3, 5.2, 5.2, 5.4, 3.8, 1.2, 4.8, 4.7],
    'Egg White Solids3': [6.1, 5.8, 10.3, 4.4, 13.1, 3.5, 2.3, 5.3, 8.8, 6.5, 3.8, 5.9, 3.8, 6.9, 4.5, 1.6, 4.0, 6.8],
    'Whey Protein Isolate4': [4.9, 2.4, 10.6, 2.5, 16.9, 1.8, 2.0, 6.2, 10.9, 9.1, 2.0, 3.3, 5.6, 4.7, 6.4, 1.7, 3.0, 6.0]
    }
    new_data = {
        'Amino Acid': ['507', '511', '504', '506', '510', '515', '512', '503', '504', '505', '506', '514', '515', '516', '502', '501', '514', '510'],
        'Vital Wheat Gluten1': [3.1, 4.7, 4.0, 1.9, 31.7, 3.8, 1.8, 3.0, 6.8, 2.8, 1.9, 4.4, 9.4, 3.9, 2.6, 1.3, 2.4, 4.5],
        'Soy Protein Isolate2g/100 g Protein': [4.0, 7.5, 11.5, 1.3, 19.2, 4.1, 2.5, 4.8, 8.0, 6.3, 1.3, 5.2, 5.2, 5.4, 3.8, 1.2, 4.8, 4.7],
        'Egg White Solids3': [6.1, 5.8, 10.3, 4.4, 13.1, 3.5, 2.3, 5.3, 8.8, 6.5, 3.8, 5.9, 3.8, 6.9, 4.5, 1.6, 4.0, 6.8],
        'Whey Protein Isolate4': [4.9, 2.4, 10.6, 2.5, 16.9, 1.8, 2.0, 6.2, 10.9, 9.1, 2.0, 3.3, 5.6, 4.7, 6.4, 1.7, 3.0, 6.0]
    }
    new_data = {
        'Amino Acid': ['503', '505', '512', '504', '501', '502', '510', 'mpc', 'ppt'],
        'Vital Wheat Gluten1': [3.0, 2.8, 1.8, 3.0, 4.4, 3.0, 4.5, 1.9, 5.2],  # Corrected ppt value
        'Soy Protein Isolate2g/100 g Protein': [4.8, 6.3, 2.5, 5.2, 1.2, 3.8, 4.7, 1.9, 5.2],  # Corrected ppt value
        'Egg White Solids3': [6.1, 6.5, 2.3, 8.8, 1.6, 4.5, 6.8, 1.9, 5.2],  # Corrected ppt value
        'Whey Protein Isolate4': [6.2, 9.1, 2.0, 10.9, 1.7, 6.4, 6.0, 1.9, 5.2]  # Corrected ppt value
    }
    #df = pd.DataFrame(data)
    new_df = pd.DataFrame(new_data)
    
    # Now, let's add this new data to your existing DataFrame 'npt'
    # You can iterate over the rows of the new DataFrame and add them to 'npt' using .loc
    for index, row in new_df.iterrows():
        amino_acid = row['Amino Acid']
        npt.loc['48052',amino_acid] = row['Vital Wheat Gluten1']  # Adjust the column name as needed
        print ("npt.loc['48052',", amino_acid," = ",row['Vital Wheat Gluten1'])


# Assuming '14058' is the index you've been using, adjust it accordingly if it's different
    
  
    
    
    #2024-6-8 todo move to getchosenfoods
    comp=pd.read_excel(get_vdwin()+'composite.xlsx',engine='openpyxl',dtype={'NDB_No':str,'component':str}).fillna(method='ffill')
    comp2=comp.set_index(['NDB_No','component'])#[['step']]
    comp1=comp2.to_dict(orient='index')
    newrows=pd.DataFrame();newfoodrows=pd.DataFrame()
    for nidx,n in comp2.groupby(level='NDB_No'):
        newndb=n.index[0][0];        #print(n.index[0][0])
        newld=n.values[0][1]
        c0=np.zeros(npt.shape[1])#; print("len c0=",len(c0))
        newrow=pd.DataFrame({'Long_Desc':newld },index=[newndb])
        newfoodrow=pd.DataFrame({'Long_Desc':newld,"cost":0.0,'min_d':0.0,'max_d':2.0 },index=[newndb])#2023-01-22
        newrows=pd.concat([newrows,newrow])
        for midx,m in n.groupby(level='component'):
            #print (midx,m.values[0][0])
            c=npt.loc[midx]*m.values[0][0]
            c0=c0+c.values
        npt.loc[newndb]=c0
        newfoodrows=pd.concat([newfoodrows,newfoodrow],ignore_index=False)
    
    
    #import pdb;pdb.set_trace()
    
    global chosenfoods
    npt.update(chosenfoods)#2024-5-30 because chosenfoods will have some extra nutrients and those have to be preferenced
    
    #2024-5-26 bypassing supplements.xlsx
    common_columns = npt.columns.intersection(chosenfoods.columns)
    # Select rows in df2 that are not in df1
    extra_rows = chosenfoods.loc[~chosenfoods.index.isin(npt.index), common_columns]
    # Concatenate df1 with the extra rows
    npt = pd.concat([npt, extra_rows])
    # Fill NaN values with zero
    npt = npt.fillna(0)

    #npt = pd.concat([npt, chosenfoods1[common_columns]]).drop_duplicates(keep='last').fillna(0)

    
    npt.update(chosenfoods)#2024-5-15 doing this again to allow overrides of composites (for whatever reason), normally this does nothing
    #chosenfoods=pd.concat([chosenfoods,newfoodrows],ignore_index=False)#2023-01-22#2024-5-11 removed bc chosenfoods has manual entry with price and min/max

    
    #import pdb;pdb.set_trace()    
    if PIECEWISE:
        nptpw=npt.copy()
        nptpw.columns=nptpw.columns+'pw'
        npt=pd.concat([npt,nptpw],axis='columns',join='inner',ignore_index=False)#,verify_integrity=True,sort=True)#april 25 2021 added sort=true to silence warning        

    if RATIOMETRICS:#disable ratiometrics
        ratiosf=pd.read_excel(get_vdwin() +'ratios.xlsx',index_col=0,dtype={'numerator':str,'denominator':str})
        
 
        for index, row in ratiosf.iterrows():
            #print(index,row['Loratio'],type(row['numerator']),type(row['denominator']))
            #npt['mgratio']=npt['301']   - mgr*npt['304']#301=calcium, 304=magnesium
            #npt[index]=npt[row['numerator']]-row['ratio']*npt[row['denominator']]

            #All ratiometric constraints in the ratios spreadsheet, consdf spreadsheet strictly for nonratiometric
            #But the min and max here could be tweeked ? and I dont want to do that in source code?
            #Dude you are going to forget how to add a new ratiometric constraint in about 2 days!!! do this now.
            #OKay, but the slacks are intended to be programmable, so as to switch between absolute and ratiometrics,
            # so the loslack and hislack have to be in the ratio file...
            #BUT then I'm back to having to edit 2 files! But that's ok...?
            #The movtivation for this is that solfibratio and tfratio are fairly far out,the other ratios are bang on.jan 31 2021
            
            npt[index+'Hi']=npt[row['numerator']]-row['Hiratio']*npt[row['denominator']]
            npt[index+'Lo']=npt[row['numerator']]-row['Loratio']*npt[row['denominator']]
            assert npt.isnull().sum().sum()<1
            assert ~npt.isnull().values.any()
    
    load_oxalates()#feb 26 2021 migrating from jupyter
    assert ~npt.isnull().values.any();#print('return from load oxalates')
    np.set_printoptions(threshold=sys.maxsize)
    #load_supplements()2021-12-15 moved this to before loading ratiometrics
    assert ~npt.isnull().values.any()
    #2022-01-21 todo lazy load this for the foodlist page..dont need for slackscho
    #2021-08-03 Bringing confid in from jupyter, and merging with chosenfoods, so it can be filtered. also, the relevant data is defined by consdf, which is editable
    #nptfull=npt.copy()#2022-03-14 moved up to UScplex
    #return json.dumps({'success':True}), 200, {'ContentType':'application/json'}
    return npt

def load_supplements():#dont call this, keep doing this in the notebook may 21 2021 d(dataframe hacking)
    global chosenfoods,npt
    vds='c:/Users/Rwsin/Google Drive/US/'#2021-07-28 supplements xlsx file now in diet directory as I added arginine and plan to add more nutrients
    nf=pd.read_excel(get_vdwin() +'supplements.xlsx',index_col=0)#2021-07-28 vdwin instead of vds#2021 july 13 changed from xls, which getting wrong data from the NDB_No row in supplements. I just re-saved it as .xlsx and that part is now better
    nf = nf[nf.filter(regex='^(?!Unnamed)').columns]#2022-01-04 deleted lots of placeholder supps but somethings left over
    
    newrows=nf.transpose().iloc[1:,:1]#.loc['203'].values
    #newrows.loc[:,'min_d']=0;newrows.loc[:,'max_d']=2#july 10 2021 why didnt i copy this from jupyter in the first place ??
    newrows['FdGrp_Desc']='supplements'
    newrows.index.rename("NDB_No",inplace=True)
    #newrows.reset_index()#2021 july 6
    chosenfoods=chosenfoods[chosenfoods['FdGrp_Desc']!='supplements']
    chosenfoods=chosenfoods.append(newrows,ignore_index=False,verify_integrity=True)#2021 july 6 changed
    nfr=nf.iloc[1:,1:].transpose().astype(float)
    nfr.index.rename('NDB_No',inplace=True)
    assert ~nfr.isnull().values.any()

    # global nptfull
    # nptfull=npt.copy()
    
    npt=npt[~npt.index.str.contains('A')]#clear out old supplements data
    assert ~npt.isnull().values.any()
    #npt=npt.append(nfr,ignore_index=False,verify_integrity=True)#2022-02-18 append is deprecated (and its leaky)
    npt=pd.concat([npt,nfr],join='right')#2023-04-27 join from inner to right, want new nutrients from supps to go into npt without hacking npt as before
    #print("npt A0000=",npt.loc['A0000'])
    if npt.isnull().values.any():
        npt#assert failure deletes context.
    #2023-04-26 want to be able to add a nutrient and all its data by way of supplements. citrate.
    npt.fillna(0)#because npt doesnt have any rows for citrate and they will be nan.
    #some soft drinks use potassium citrate, but probably will be no data for that (maybe the potassium level can be used to infer it) 
    #assert ~npt.isnull().values.any() #2022-02-19 dont check this here. if it was called from ajax, npt will have fewer columns than nfr and the concat will include those columns and put nulls. 
    npt.index.rename('NDB_No',inplace=True)
#import ipdb

def load_supplements_npt():#2022-03-16 splitting out treatment of npt and chosen_foods, the de-cleverization of this shit code
    global chosenfoods,npt
    vds='c:/Users/Rwsin/Google Drive/US/'#2021-07-28 supplements xlsx file now in diet directory as I added arginine and plan to add more nutrients
    nf=pd.read_excel(get_vdwin() +'supplements.xlsx',index_col=0)#2021-07-28 vdwin instead of vds#2021 july 13 changed from xls, which getting wrong data from the NDB_No row in supplements. I just re-saved it as .xlsx and that part is now better
    #ipdb.set_trace()

    nf = nf[nf.filter(regex='^(?!Unnamed)').columns]#2022-01-04 deleted lots of placeholder supps but somethings left over
    assert nf.index.is_unique
    assert nf.columns.is_unique
    # newrows=nf.transpose().iloc[1:,:1]#.loc['203'].values
    # newrows.loc[:,'min_d']=0;newrows.loc[:,'max_d']=2#july 10 2021 why didnt i copy this from jupyter in the first place ??
    # newrows['FdGrp_Desc']='supplements'
    # newrows.index.rename("NDB_No",inplace=True)
    # #newrows.reset_index()#2021 july 6
    # chosenfoods=chosenfoods[chosenfoods['FdGrp_Desc']!='supplements']
    # chosenfoods=chosenfoods.append(newrows,ignore_index=False,verify_integrity=True)#2021 july 6 changed
    nfr=nf.iloc[1:,1:].transpose()#.astype(float)#2022-07-12 unit strings appended, strip later
    nfr.index.rename('NDB_No',inplace=True)
    assert ~nfr.isnull().values.any()

    # global nptfull
    # nptfull=npt.copy()
    
    npt=npt[~npt.index.str.contains('A')]#clear out old supplements data
    assert ~npt.isnull().values.any()
    #npt=npt.append(nfr,ignore_index=False,verify_integrity=True)#2022-02-18 append is deprecated (and its leaky)
    nfr.replace(to_replace='g',value='',regex=True,inplace=True)#2022-07-11 replace any units strings with nothing (strip)
    nfr.replace(to_replace='u',value='',regex=True,inplace=True)#2022-07-11 replace any units strings with nothing (strip)
    nfr.replace(to_replace='m',value='',regex=True,inplace=True)#2022-07-11 replace any units strings with nothing (strip)
    nfr.replace(to_replace='i',value='',regex=True,inplace=True)#2024-2-26 IU
    nfr=nfr.astype(float)

    #2022-07-18 bioavialability, first stab
    #blockingfactor=1.0
    
    #nfr[iron]=nfr[iron]-nfr[calcium]*blockingfactor
    #for now, just zero out iron since they all also have calcium (and selenium)
    #this doesnt belong here, but more generally, would have to split out heme iron
    #ie. imputed based on food group like for oxalates
    #but supplements, as a food group are non-heme iron ?
    
    #nfr['303']=0.0

    #lycopene doesnt count outside of food (nutritionfacts youtube)
    nfr['337']=0.0#2023-04-02
    #print(npt.head(),nfr.head())
    npt=pd.concat([npt,nfr],join='outer')#2023-04-27 inner to right for new nutrient in supplement
    npt.fillna(0,inplace=True)#only the supps will have any citrate data...

    #2022-12-28 put in load composite foods here

    #print("npt A0000=",npt.loc['A0000'])
    if npt.isnull().values.any():
        npt#assert failure deletes context.
    #assert ~npt.isnull().values.any() #2022-02-19 dont check this here. if it was called from ajax, npt will have fewer columns than nfr and the concat will include those columns and put nulls. 
    npt.index.rename('NDB_No',inplace=True)
    #2022-12-29 composite foods. augmenting both npt and chosenfoods all at once...
    #2023-04-07 movind composite file to vdwin where everything else is located
    


def load_supplements_chosenfoods():#2022-03-16 splitting out treatment of npt and chosen_foods, the de-cleverization of this shit code
    #2022-10-11 supplements.xlsx and chosenfoods1 must both be edited to add supplements
    global chosenfoods,npt
    vds='c:/Users/Rwsin/Google Drive/US/'#2021-07-28 supplements xlsx file now in diet directory as I added arginine and plan to add more nutrients
    nf=pd.read_excel(get_vdwin() +'supplements.xlsx',index_col=0)#2021-07-28 vdwin instead of vds#2021 july 13 changed from xls, which getting wrong data from the NDB_No row in supplements. I just re-saved it as .xlsx and that part is now better
    nf = nf[nf.filter(regex='^(?!Unnamed)').columns]#2022-01-04 deleted lots of placeholder supps but somethings left over
    #2022-03-20 todo nf.index.rename("cost",)
    #2022-06-01 newrows=nf.transpose().iloc[1:,:1]#.loc['203'].values
    newrows=nf.transpose().loc['A0000':,['cost','Long_Desc']]#.to_frame()#2022-06-01
    assert ~newrows.isnull().values.any()
    newrows.index.rename('NDB_No',inplace=True)
    #newrows.rename(columns={'goto':'cost'},inplace=True)#2022-03-20
    newrows.loc[:,'min_d']=0;newrows.loc[:,'max_d']=2#july 10 2021 why didnt i copy this from jupyter in the first place ??
    newrows['FdGrp_Desc']='supplements'
    #newrows.index.rename("NDB_No",inplace=True)
    #newrows.reset_index()#2021 july 6
    chosenfoods=chosenfoods[chosenfoods['FdGrp_Desc']!='supplements']
    
    chosenfoods = pd.concat([chosenfoods, newrows], ignore_index=False, verify_integrity=True)#2024-2-1 
    #chosenfoods=chosenfoods.append(newrows,ignore_index=False,verify_integrity=True)#2021 july 6 changed
    
    # nfr=nf.iloc[1:,1:].transpose().astype(float)
    # nfr.index.rename('NDB_No',inplace=True)
    # assert ~nfr.isnull().values.any()
#  documents@ctfs.com  case #d112475    subj    2022-09-15 

isinindex=0
def is_month_in_range(current, start, end):
    """
    Return True if the current month (1-12) falls within the season defined by start and end.
    If either start or end is missing (NaN), treat the item as available (in season).
    """
    # If either season column is missing, assume no seasonal restriction
    if pd.isna(start) or pd.isna(end):
        return True

    # Convert to integer in case they are floats (Excel often imports numbers as floats)
    start = int(start)
    end = int(end)

    if start <= end:
        # Standard range (e.g., April to September)
        return start <= current <= end
    else:
        # Wrap-around range (e.g., October to February)
        return current >= start or current <= end
        
from datetime import datetime
        
def trimdb():#2022-01-12 cplex allows max 1000 variables, but cplex as a sanity check for when coinor looks suspicious (recent mi bug)
    #this is an ongoing project in case mixed integer gets very slow (esp future semicontinuous) 
    # this should only get called in case of cache miss on chosenfoods  
    global chosenfoods,chosenfoods_whole ,vdwin,chosenfoods_cplex
    global chosenfoods1#2022-09-15 chosenfoods1 provides a nice spreadsheet for input of price data, even though it looks hairy here
    # chosenfoods_whole=chosenfoods.copy()#assuming this is what all the una bitmap are based on ; save it
    # print("cplex chosenfoods=",chosenfoods_cplex.shape)
    # chosenfoods=chosenfoods_cplex
    #2022-02-07 hand picked foods
    #load_supplements()#2022-03-06 deleted #2022-02-08#2022-02-19 this should be a precondition
    #chosenfoods1=pd.read_excel(get_vdwin() +'chosenfoods1.xlsx',dtype={'NDB_No':str}).set_index('NDB_No')#index_col=0)#load it up, edited OR NOT
    chosenfoods1=pd.read_excel(get_vdwin() +'chosenfoods1.xlsx',header=0,dtype={'NDB_No':str}).set_index('NDB_No')#index_col=0)#load it up, edited OR NOT

    chosenfoods1.fillna(value={'exclude':1},inplace=True)

    chosenfoods1.fillna(value={'min_d':0},inplace=True)#2024-5-12
    chosenfoods1.fillna(value={'max_d':10},inplace=True)
    #2023-03-28 try whole database
    current_month = datetime.now().month

    chosenfoods1['in_season'] = chosenfoods1.apply(lambda row: is_month_in_range(current_month, row['Season Start Month'], row['Season End Month']),    axis=1)
    #2025-2-9
    chosenfoods1 = chosenfoods1[((chosenfoods1['exclude'] == 0) | (chosenfoods1['exclude'] == 2)) &     (chosenfoods1['in_season'])]
    #chosenfoods1=chosenfoods1[(chosenfoods1['exclude']==0) |(chosenfoods1['exclude']==2) ]
    
    #exclude code=2 means possible but unlikely...
    #now load supps (again)
    #load_cplexsupplements("cplexsupps.xlsx",chosenfoods)
    global cplexmask,chosenfoods_cplex
    cplexmask=chosenfoods.index.isin(chosenfoods1.index)#to convert bitmaps in una

    #2022-10-09 dont use the mask if the .mps file is going to neos (dont need it)
    chosenfoods_cplex=chosenfoods[cplexmask]#2022-02-08,2022-10-24
    chosenfoods_cplex.update(chosenfoods1['max_d'])#2022-12-04 overriding una, and chosenfoods gradually. pandas dataframes are bs.
    chosenfoods_cplex.update(chosenfoods1['min_d'])#2022-12-11 Im taking ginger every night, should factor in..
    chosenfoods_cplex['Long_Desc']=chosenfoods_cplex['Long_Desc'] + " CPLEX"#' &#9745'

    chosenfoods1.fillna({'price':1.0},inplace=True)
    chosenfoods_cplex=chosenfoods_cplex.merge(chosenfoods1.price,left_index=True,right_index=True,how='left')#2022-09-15 one way of getting price, but it has to go into npt...
    chosenfoods_cplex=chosenfoods1#2024-5-12 going over to the spreadsheet as the master source 

    chosenfoods_cplex.price.fillna(1.0)
    
SUPPLEMENTS=True
def get_chosen_foods(c=None):#2022-04-07 changeover to explicit caching of chosenfoods so that exclude can re-write the cache for use by US2
    global chosenfoods,chosenfoods_cplex,una #2022-05-20 this is hacky as shit, fix
    if c is None:
        if chosenfoods is None:#try:#2022-06-06 this is not just a detail to function out, its core to how this is a web app
        #    chosenfoods
            #really you should make one of these cache managers for una, separate from chosenfoods, especially since una is small and is being rebuilt on the fly.
            # CPLEX is called in 3 distinct circumstances involving caache:
            # chosenfoods doesn't exist (server startup) and not cached
            # chosenfoods doesnnt exist (flask memory management) but is cached
            # chosenfoods exists, but ... it has been modified and cache is out of date now        
        
            #if you got here, do nothing
        #except NameError:
            # #2022-06-06 whoah check cache first ??
            # print("loading chosenfoods from file.")
            # #chosenfoods=cache.get("chosenfoods")#removed 2022-11-26
            # try:
            #     assert chosenfoods is not None#=cache.get("chosenfoods")
            # except AssertionError:

            print("loading chosenfoods from file.")
            #chosenfoods=pd.read_csv(get_vdwin()+'chosenfoods.csv',index_col=0,dtype={'NDB_No':'str','FdGrp_Cd':str});#chosenfoods=pd.read_csv(vdwin+'chosenfoods.csv',index_col=0,dtype={'NDB_No':'str'})
            chosenfoods=pd.read_excel(get_vdwin() +'chosenfoods1.xlsx',header=0,dtype={'NDB_No':str}).set_index('NDB_No')#horrible hacky cleanup of checkmarks that I had inserted into the model instead of the view...2022-03-21
            #chosenfoods['Long_Desc']=chosenfoods['Long_Desc'].str.replace('&#9745', '',regex=True)
            #chosenfoods['Long_Desc']=chosenfoods['Long_Desc'].str.replace(' CPLEX', '',regex=True)
            #chosenfoods.rename(columns={'goto':'cost'},inplace=True)#2022-05-31 getting rid of 'goto' key#.set_index('NDB_No')#june 15 2021 removed set_index

            #chosenfoods.min_d=0.0;chosenfoods.max_d=12.0#2022-06-02 temporary for repair of chosenfoods.csv
            #2022-04-15 
            # CPLEX conforms to these rules about variable names in the LP file format.
            # Variables can be named anything in LP format provided that the name does not exceed 255 characters,
            #  all of which must be alphanumeric (a-z, A-Z, 0-9) 
            # or one of these symbols: ! " # $ % & ( ) , . ; ? @ _ ÃƒÂ¢Ã¢â€šÂ¬Ã‹Å“ ÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢ { } ~. 
            # Longer names are truncated to 255 characters. 
            # A variable name can not begin with a number or a period.
            # The letter E or e, alone or followed by other valid symbols, or followed by another E or e, should be avoided as this notation is reserved for exponential entries. Thus, variables can not be named e9, E-24, E8cats, or other names that could be interpreted as an exponent. Even variable names such as eels or example can cause a read error, depending on their placement in an input line.
            #chosenfoods.Shrt_Desc=chosenfoods.Shrt_Desc.str.replace(r'[^\w]',"a",regex=True)
            #chosenfoods.loc[chosenfoods.Shrt_Desc.isna(),'Shrt_Desc'] =  'f' + chosenfoods[chosenfoods.Shrt_Desc.isna()].index
            
            if not SUPPLEMENTS:#2022-06-03 
                chosenfoods=chosenfoods[~chosenfoods.index.str.contains('A')]#2022-06-03
            #nut_data=pd.read_pickle(vdwin+'nut_data_final')#2022-11-29 vd_root gone now, consolidating code and data for colab
            #nut_data_relevant=nut_data[nut_data['Nutr_No'].isin(consdf.index)]
            #grouped=nut_data_relevant.groupby(['NDB_No'])
            #confid=grouped.count()['Nutr_No'].to_frame(name='confid').reset_index()#;pd.Series.to_frame()
            #confid.set_index('NDB_No',inplace=True)
            #print('chosenfoods cols=',chosenfoods.columns)
            #chosenfoods.drop(columns=['confid'],inplace=True)#2021-09-06
            #chosenfoods=chosenfoods.merge(confid,how='left',left_index=True,right_index=True)
            #if SUPPLEMENTS:
            #    load_supplements_chosenfoods()    
            #trimdb()#just to get chosenfoods_cplex
            # cache.set("chosenfoods",chosenfoods)
            # cache.set("chosenfoods_cplex",chosenfoods_cplex)
        # try:#its expected I'll be wiping out una
        #     una
        # except NameError:
        #     try:
        #         una=pd.read_pickle(get_vdwin()+'una');#june 4 2021 should report inability to set dtypes = bytes for bitmaps, if I cared.
        #     except FileNotFoundError:#EOFError:
        #         una=pd.DataFrame()
    
    # else:#2022-11-27 removing..am i saving or pickling this anywhere ??
        # cache.set("chosenfoods",c)
        # cache.set("una",una)#2022-04-07 sketchy as hell, 
        # cache.set("chosenfoods_cplex",chosenfoods_cplex)
        #but exclude is the single reason for caching and these two are the same,
        #so take una handling out of loaddataset and into get_chosen_foods.
    #return cache.get("chosenfoods"),cache.get("chosenfoods_cplex"),cache.get("una")
from pyomo.environ import *

def UScplex():#2022-10-03 spliting this out for neos offload
    loaddataset()
    UScplex1()
    #2022-10-04 todo check for the .slx solution file and wait...
    # I'm prioritizing the jupyter interface assuming it does caching for me
    return UScplex2()#should return all dataframes so jupyter can cache everything
    #the calling function makes them into html.

bincons=[];binvars=[];bv=[];constraints=[]





   
    
#RWS 2024-10-23 todo port this like maketrade    
def makeordinal(ndbarray):#list of 2 npt index values, the first being higher priority 
    global npt,fvars,bincons,binvars,mn_param,ordinals
    #20222-12-16 list of lists, ndbno, then multiplier amount (i.e. weight of one egg)
    #for i in range(len(ndbarray)):
    sv1=npt.columns.get_loc(ndbarray[0]) #solver.LookupVariable(i)
    sv2=npt.columns.get_loc(ndbarray[1]) #solver.LookupVariable(i)
    
    expr=prob.lsvars[sv2]*consdf['loslack2'].iloc[sv2] >= prob.lsvars[sv1] * consdf['loslack2'].iloc[sv1]
    
    prob.constraints.add(expr)
    
#    ordinals+=[lsvars[sv2]*consdf['loslack2'].iloc[sv2]>=lsvars[sv1]*consdf['loslack2'].iloc[sv1]]
    #lsvars,consdf['loslack2']
    #todo maybe a flag or someway to designate how usvars is treated, or if usvars and lsvars are compared
    #really the strongest tradeoff is the loslack of one against the uslack of multiple others.
    #bincons+=[(fvars[sv]==binvars[i]*ndbarray[i][1])]
    #assert ndbarray[i][1] > 0.0



#debugging purposes
lsvarstrade1=None
lsvarstrade2=None
slackslope1=None
slackslope2=None
sv1='sv1'
sv2='sv2'

#RWS ported 2024-10-22
def maketrade(ndbarray):#list of 2 npt index values, equates lowslack0 and hislack1 
    global npt,fvars,bincons,binvars,mn_param,ordinals,lsvarstrade1,lsvarstrade2,prob,lsvars,usvars,sv1
    #20222-12-16 list of lists, ndbno, then multiplier amount (i.e. weight of one egg)
    #for i in range(len(ndbarray)):
    sv1=npt.columns.get_loc(ndbarray[0]) #solver.LookupVariable(i)
    sv2=npt.columns.get_loc(ndbarray[1]) #solver.LookupVariable(i)
    #ordinals+=[lsvars[sv1]*consdf['loslack2'].iloc[sv1]==usvars[sv2]*consdf['hislack2'].iloc[sv2]]
    expr=prob.lsvars[sv1]*consdf['loslack2'].iloc[sv1] == prob.usvars[sv2] * consdf['hislack2'].iloc[sv2]
    
    #2024-10-23 RWS testing this
    lsvarstrade1=prob.lsvars[sv1]
    lsvarstrade2=prob.usvars[sv2]
    slackslope1=consdf['loslack2'].iloc[sv1]
    slackslope1=consdf['hislack2'].iloc[sv2]

    prob.constraints.add(expr)


def makebincons(ndbarray):
    global prob, fvars, bincons, binvars, mn_param
    
    # Iterate over ndbarray to create binary variables and constraints
    prob.binvars = Var(range(nf), initialize=0.0,domain=NonNegativeIntegers, name="binvars")
    for i in range(len(ndbarray)):
        sv = npt.index.get_loc(ndbarray[i][0])
        #binvar = Var(
        #prob.binvars.append(binvar)
        expr = prob.fvars[sv] == prob.binvars[i] * ndbarray[i][1]
        prob.constraints.add(expr)#,name="intcon"+ndbarray[i][0])
        assert ndbarray[i][1] > 0.0
        


def makemaxfromgroups(mn, ndbarray=None, groupname="", mfgex=[]):
    global prob, bv,fvars
    
    if ndbarray is None:
        ndbarray = chosenfoods_cplex.index.tolist()
    ndbarray = list(set(ndbarray) - set(mfgex))    
    
    ns = [groupname + 'isin' + str(ndbarray[i]) for i in range(len(ndbarray))]
    prob.bv=Var(range(len(ns)),domain=Boolean, name=groupname)

    for bn in range(len(ns)):
        sv = npt.index.get_loc(ndbarray[bn])
        prob.constraints.add(expr=prob.fvars[sv] <= prob.bv[bn] * chosenfoods_cplex.loc[ndbarray[bn], 'max_d'])
    # Add sum constraint to prob
    prob.constraints.add(expr=sum(prob.bv[i] for i in range(len(ns))) <= mn)    
A=None 
fvars=None
def UScplex1(to=120):#2023 generates the linear part of the problem, mixedint added later, then .mps generated#this just generates an .mps and a .slx solution file, locally or from neos if faster
    global chosenfoods_cplex, cplexmask
    global cplexmask,isinindex,una,A,slacks1,slacks2,st,obj,s,chosenfoods,nf,ncons,npt,consdf,AMconsdf,PMconsdf,A,collist,foodlist,cslack,solver
    global problem#2022-01-01 cplex max 1000 variables.could be more sophisticated based on leucine_deficit etc.
    global mn_param
   
    npt_whole=npt.copy()#2022-10-09
    commoncols=list(set(npt.columns.to_list()).intersection(consdf.index.to_list()))
    npt=npt[commoncols];consdf=consdf.loc[commoncols]
    #shouldnt this go in trimdb?
    commonrows=list(set(npt.index.to_list()).intersection(chosenfoods_cplex.index.to_list()))#added 2022-01-01, todo copy over to the coinor version
    #2022-10-09 expoit neos .but is this masking necessary for whole ?? skip for now
    commonrows_whole=list(set(npt.index.to_list()).intersection(chosenfoods.index.to_list()))#added 2022-01-01, todo copy over to the coinor version

    npt=npt.loc[commonrows];chosenfoods_cplex=chosenfoods_cplex.loc[commonrows]
    npt.sort_index(axis='index',inplace=True)
    npt.sort_index(axis='columns',inplace=True)
    #print ("npt.index=",npt.index,"npt.columns",npt.columns)
    #chosenfoods_cplex.sort_values('NDB_No',inplace=True)#2020-05-19 11:08:57 optimize by doing this only when these are modified
    chosenfoods_cplex.sort_index(inplace=True)#2023-01-23 wierdly changed
    consdf.sort_index(axis='index',inplace=True)
    #npt.sort_index(axis='columns',inplace=True)
    #todo also make sure consdf is filtered to what is in npt 
    
    nf=npt.shape[0];  ncons=npt.shape[1]
    assert consdf.index.shape[0]==npt.columns.shape[0]#jan 19 2021#jun 11 2021 make sure no formatted empty cells that openpyxl counts as data
    assert (consdf.index==npt.columns).all()#june 9 2021

    assert all(npt.isna()==False) #2021-09-05
    nptc=npt
    import numpy as np
    threshold = 1e-10#2024-2-8 
    npt[np.abs(npt) < threshold] = 0# Zero out elements smaller than the threshold

    #print("cvxpy version ",cvxpy.__version__)
    global lslacknames,uslacknames
    #2022-10-09 waste of time for cvxpy...use vectors
    lslacknames=[a+b for a,b in zip(['ls']*ncons,npt.columns.to_list())]#lslacknames=['ls'+ str(i) for i in range(0,ncons)];    
    uslacknames=[a+b for a,b in zip(['us']*ncons,npt.columns.to_list())]#uslacknames=['us'+ str(i) for i in range(0,ncons)]
    #names=(chosenfoods_cplex.Shrt_Desc).tolist()+lslacknames+uslacknames#nf+2*ncons
    names=(''+npt.index).tolist()
    
    lb=consdf['min'].values.astype(np.double); ub=consdf['max'].values.astype(np.double)#    
    A=np.array(npt,order='F'); #   A=np.concatenate((A,np.identity(npt.shape[1])),axis=0);    A=np.concatenate((A,-np.identity(npt.shape[1])),axis=0)
    noslacks=False
    if (noslacks):
        obj=npt.loc[:,'208']#.astype(np.float64)#consdf.copy();obj['objective']=0.0;obj.loc['208','objective']=1.0#2022-05-03
        row_lb=consdf['min'].astype(np.double).values;row_ub=consdf['max'].astype(np.double).values
        names=('f'+npt.index).tolist()
       
    global fvars,lsvars,usvars,vectorvars
    #fvars = [cvxpy.Variable(name=n) for n in names]#todo, no, use .loc as long as you have to loop like this
    vectorvars=True
    global prob    
    prob = ConcreteModel()
    prob.constraints = ConstraintList()

    import numpy as np
    if vectorvars:
        prob.lsvars = Var(range(ncons))#npt.columns)  # Assuming ncons is properly defined
        prob.usvars = Var(range(ncons))#npt.columns)  # Assuming ncons is properly defined
    nvs=0#number of variables. need to keep it under 1000 for cplex-should figure out an expression based on the size o chosenfoods, and the AM/PM data..
    nvs+=len(names);print("nf,ncons,nvs=",nf,ncons,nvs)

    #global MIXED
    #MIXED=True #2022-11-10
    global bv,constraints
    constraints=[]
    if vectorvars:
        prob.fvars = Var(range(nf))#npt.index, initialize=0.0,name='fvars')  # Assuming nf is properly defined
#from cplex import Cplex
#mn_param=cvxpy.Parameter( integer=True)

def UScplex1int(mixed=True,binconsl=None,mfg=None,mn=14,mfgex=[]):#mfg=none means all,unless mn=0 then no constraint
    #2022-12-08 mfgex list of food not to count in maxfromgroups
    global constraints,mn_param,A
    global obj,ordinals,lsvars,usvars,fcons,c1#2022-12-13 using these to call the solver locally in Uscplex2
    global chain,prob,data,inverse_data #2022-10-03

    global bincons,binvars,bv,constraints#2024-01-31 wipe out old binary variables every time this is called (the linear variables are left alone)
    

    bincons=[];binvars;bv=[];constraints=[]
    #prob.bincons=bincons;


    lb=consdf['min'].values.astype(np.double)#
    ub=consdf['max'].values.astype(np.double)#    
    if (binconsl is not None):
        makebincons(binconsl)
    if (mn>0):
        #mn_param.value=mn
        makemaxfromgroups(mn,None,"",mfgex=mfgex)#passing mn_param not working#makemaxfromgroups(mn,ndbarray=None,groupname="",mfgex=[])
    #2023-04-20 this would be for at most 1 multivitamin, or at most one meat or whatever
    if (mfg is not None):#mfg is a list of dictionaries, each one is n and the list of foods
        for idx,group in enumerate(mfg):
            makemaxfromgroups(group['list'],"g"+str(idx),group['n'],[])

    col_lb =chosenfoods_cplex['min_d'].astype(np.double).values
    col_ub = chosenfoods_cplex['max_d'].astype(np.double).values
    if vectorvars:
        prob.fcons = ConstraintList()
        for i in range(len(prob.fvars)):
            prob.fcons.add(expr=prob.fvars[i] >= col_lb[i])
            prob.fcons.add(expr=prob.fvars[i] <= col_ub[i])    
    try:
        assert all(col_lb<col_ub)
    except AssertionError:
        print(chosenfoods_cplex[~(chosenfoods_cplex['min_d']<chosenfoods_cplex['max_d'])])
    ordinals=[]
    #obj=cvxpy.Minimize(cvxpy.sum_squares(lsvars*consdf['loslack2']+usvars*consdf['hislack2']))#works but which solver ?#NOT sum(lsvars) + sum(usvars)  #@consdf['loslack2'])+sum(usvars@consdf['hislack2']))
    if vectorvars:#cvxpy.sum() 2022-11-03        #ordinals=[cvxpy.sum_squares(fvars)>=1]#not dcp        #ordinals=[cvxpy.Pnorm(fvars/1.1e-6,0.5)<=1e6]#not dcp
        #ordinals=[cvxpy.sum_squares(fvars)>=nf+1]#not dcp        #ordinals=[cvxpy.sum(fvars/1.1e-6)<=1e1]#dcp        #ordinals=[cvxpy.norm_inf(fvars/1.1e-6)<=1e1]#dcp
        ordinals=[]#2022-12-02'
        #obj=cvxpy.Minimize(-1e-9*cvxpy.pnorm(fvars/1.1e-6,0.5)+cvxpy.sum( cvxpy.multiply(lsvars,consdf['loslack2'])+cvxpy.multiply(usvars,consdf['hislack2'])))#NOT sum(lsvars) + sum(usvars)  #@consdf['loslack2'])+sum(usvars@consdf['hislack2']))
        #p=0.25 has too many variables for xpress
        #obj=cvxpy.Minimize(cvxpy.sum_squares( cvxpy.multiply(lsvars,consdf['loslack2'])+cvxpy.multiply(usvars,consdf['hislack2'])))#*cvxpy.pnorm(fvars/1e-7,0.5))#NOT sum(lsvars) + sum(usvars)  #@consdf['loslack2'])+sum(usvars@consdf['hislack2']))
        #obj=cvxpy.Minimize(cvxpy.sum( cvxpy.multiply(lsvars,consdf['loslack2'])+cvxpy.multiply(usvars,consdf['hislack2'])))
        #2024-2-2 sum_squares needs a qp solver that does mi. GLOP only does mi. GLOP also does time limits and warm start, and is maybe fast ? Nope that wasnt it, cvxpy just doesnt do mip via glop
    if vectorvars:#2022-09-11 its a mixed-int problem, does conditioning make a difference, and does vectorization make a difference ?
        prob.cons_indices = RangeSet(0, ncons-1)
        prob.cons_indices2 = RangeSet(0, ncons-1)

        #def ub_rule(prob, i):
        #    return sum(A[j, i] * prob.fvars[j] for j in range(nf))-prob.usvars[i] <= ub[i]
        #def lb_rule(prob, i):
        #    return sum(A[j, i] * prob.fvars[j] for j in range(nf))+ prob.lsvars[i] >= lb[i]
            
        #prob.constraint_ub = Constraint(prob.cons_indices, rule=ub_rule)
        #prob.constraint_lb = Constraint(prob.cons_indices2, rule=lb_rule)
        prob.constraint_ub = Constraint(prob.cons_indices)
        prob.constraint_lb = Constraint(prob.cons_indices2)
        for i in prob.cons_indices:
            prob.constraint_ub[i] = sum(A[j, i] * prob.fvars[j] for j in range(nf)) - prob.usvars[i] <= ub[i]
        
        for i in prob.cons_indices2:
            prob.constraint_lb[i] = sum(A[j, i] * prob.fvars[j] for j in range(nf)) + prob.lsvars[i] >= lb[i]

    if vectorvars:#c1=slacks,constraints=
        # Define variables
        
        # Define objective
        #def objective_rule(prob):
            # Compute the objective expression based on lsvars, usvars, and consdf
            #return sum((prob.lsvars[i] * consdf['loslack2'][i] + prob.usvars[i] * consdf['hislack2'][i]) ** 2 for i in prob.lsvars)
        #    return sum((prob.lsvars[i] * consdf['loslack2'][i] + prob.usvars[i] * consdf['hislack2'][i])  for i in prob.lsvars)


        #prob.obj = Objective(rule=objective_rule, sense=minimize)  # Or maximize if it's a maximization problem
        prob.obj = Objective(expr=sum((prob.lsvars[i] * consdf['loslack2'][i] + prob.usvars[i] * consdf['hislack2'][i]) for i in prob.lsvars), sense=minimize)  # Or maximize if it's a maximization problem

        #2024-12-19 
        #prob.obj = Objective(expr=sum((prob.lsvars[i] * consdf['loslack2'][i] + prob.usvars[i] * consdf['hislack2'][i])**2 for i in prob.lsvars),sense=minimize)
        
        
        # Add non-negativity constraints for lsvars and usvars
        prob.non_negativity_lsvars = ConstraintList()
        prob.non_negativity_usvars = ConstraintList()
        for i in range(ncons):
            prob.non_negativity_lsvars.add(expr=prob.lsvars[i] >= 0)
            prob.non_negativity_usvars.add(expr=prob.usvars[i] >= 0)
        
 
    global solver 
    #solver="CPLEX"#"XPRESS"
    
    #test problem 2024-2-14
    #x = cvxpy.Variable(10000)
    #objective = cvxpy.Minimize(cvxpy.sum(x))
    #constraints = [x >= 0, x <= 1]
    #prob = cvxpy.Problem(objective, constraints)
    #end test
    
    
    #if (mixed):#(MIXED):#2022-12-03
        #data, chain,inverse_data = prob.get_problem_data(solver)#data[s.C] are the variables, they are named sequentially to Cplex (from cplex_conif.py)
        #soln=chain.solve_via_data_1(prob,data, False, True)#: #for cplex
        #when this returns, check for the .slx file, if not there, it timed out so use the neos one.

def UScplex2local():#2024-01-25 uscplex1* called first to build problem
    global solver ,prob
    #solver="CPLEX"#"XPRESS"
    prob.solve(verbose=True,solver=solver)#"XPRESS")#,qcp=True)#"CPLEX")#,write_mps='hpw15.mps')

def solve_with_time_limit(model, time_limit):
    solver = SolverFactory('scip')
    solver.options['limits/time'] = time_limit
    solver.options['display/verblevel'] = 0
    solver.options['display/freq'] = -1
    solver.options['display/headerfreq'] = -1#15
    result = solver.solve(model, tee=True)

    # Return the optimization result
    return result

def UScplex2(neos=True,timelimit=1800):
    #2024-8-21 have to name the variables after the ndbno. already done somewhere
    global chain,prob,data,inverse_data,chain2,data2,inverse_data2,fvars,lsvars,usvars,vd #2022-10-03
    global  MIXED #2022-10-24
    import pandas as pd
    if (neos):#(MIXED):2022-12-03 see if colab is fast (GPU)
            #2024-2-23 taken from cplex_qpif.py
            # import xml.etree.ElementTree as ET #2022-11-27 works fine but gurobi preferred (below)
            # tree = ET.parse(vd+"soln.sol")#"/mnt/c/Users/Rwsin/myproject/soln.sol")
            # root = tree.getroot()
            # x=np.array([child.attrib['value'] for child in root[3]])

            #2022-11-01 if reading gurobi cplex output:
            import pandas as pd
            #cbcsol=pd.read_table(vd+"model.sol",index_col=None,sep=None,names=['NAME','CVX_xpress_qp'],dtype={'NAME':str,'CVX_xpress_qp':float},skiprows=2,engine='python')
            cbcsol=pd.read_table(vd+"model.sol",index_col=0,sep=None,names=['amounts'],dtype={'name':str,'amounts':float},skiprows=0,engine='python',on_bad_lines='skip')#,dtype={'NAME':str,'CVX_xpress_qp':float},

            fvars = cbcsol[cbcsol.index.str.startswith('fvars')]
            lsvars=cbcsol[cbcsol.index.str.startswith('lsvars')]
            usvars = cbcsol[cbcsol.index.str.startswith('usvars')]

            chosenfoods_cplex['amounts']=fvars.amounts.values#2024-8-27

    else:
        global obj,ordinals,fcons,c1
        #prob=cvxpy.Problem(obj,c1+ordinals+[lsvars>=0.0,usvars>=0.0]+fcons)
       # Create a solver object
    
        solver = SolverFactory('scip')
        solver.options['limits/time'] = timelimit
        result = solver.solve(prob, tee=True)

        print("status:", result.solver.status, result.solver.termination_condition)#,")# obj=",value(prob.objective))
        model_series = pd.Series({idx: value(prob.fvars[idx]) for idx in prob.fvars})#.reindex(uspyomo.chosenfoods_cplex.index)
        fvars=model_series.to_frame()
        chosenfoods_cplex['amounts']=model_series.values#.update(model_series.values)#chosenfoods_cplex[['amounts','Long_Desc']])#2022-04-09 Long_desc has "CPLEX" appended
        
        model_series = pd.Series({idx: value(prob.lsvars[idx]) for idx in prob.lsvars})#.reindex(uspyomo.chosenfoods_cplex.index)
        model_series.name="amounts"
        lsvars=model_series.to_frame()
        model_series = pd.Series({idx: value(prob.usvars[idx]) for idx in prob.usvars})#.reindex(uspyomo.chosenfoods_cplex.index)
        model_series.name="amounts"

        usvars=model_series.to_frame()


# if result.solver.termination_condition == TerminationCondition.maxTimeLimit:#2025-3-21 doesn't work anymore,skip it
        #     # Continue solving with a new time limit
            
        # # Set initial values of variables to previous solution
        
        #     for var in prob.component_data_objects(Var, active=True):
        #         var.set_value(result[var])

    #np.set_printoptions(threshold=sys.maxsize)
    #if vectorvars:
    
    #    chosenfoods_cplex.amounts = [value(prob.fvars[i]) for i in range(nf)]
    #    model_series = pd.Series({idx: value(model.fvars[idx]) for idx in model.fvars})
    #chosenfoods['amounts']=0.0#chosenfoods.drop('amounts',axis='columns',inplace=True)#2022-02-27 
    #chosenfoods['amounts'].update(model_series)#chosenfoods_cplex[['amounts','Long_Desc']])#2022-04-09 Long_desc has "CPLEX" appended
    chosenfoods['amounts']=0.0#chosenfoods.drop('amounts',axis='columns',inplace=True)#2022-02-27 
    chosenfoods.update(chosenfoods_cplex[['amounts','Long_Desc']])#2022-04-09 Long_desc has "CPLEX" appended

    #get_chosen_foods(chosenfoods)#2022-11-27 removing this,maybe incorrectly..I'm not

    if (AMPM):#2022-01-21 lazy load this in the solution page
        amndbarray='fam' + AMnpt.index;pmndbarray='fpm' + PMnpt.index
        chosenfoods_cplex.loc[:,'AMamounts']=problem.solution.get_values(amndbarray.tolist())
        chosenfoods_cplex.loc[:,'PMamounts']=problem.solution.get_values(pmndbarray.tolist())
        chosenfoods.update(chosenfoods_cplex[['amounts','AMamounts','PMamounts','Long_Desc']])#2022-04-09 Long_desc has "CPLEX" appended
    #chosenfoods.update(chosenfoods_cplex[['amounts','Long_Desc']])#2022-04-09 Long_desc has "CPLEX" appended

    collist4=['FdGrp_Desc','Long_Desc','min_d','max_d','amounts','confid']#2024-5-12

    #print('chosenfoods_cplex cols=',chosenfoods_cplex.columns)
    #foodlist=chosenfoods_cplex[collist3].merge(npt[['cost']],left_index=True,right_index=True)#june 15 2021 left_index=True
    #foodlist=chosenfoods[collist3].merge(nptfull[['cost']],left_index=True,right_index=True)#june 15 2021 left_index=True
    global foodlist
    foodlist=chosenfoods[collist4]#2022-03-10
    global nzf2
    nzf2=foodlist.copy()#2022-50-31 renamed upon loading#rename(columns={'goto':'cost'},inplace=False)
    #nzf2=foodlist#[foodlist['amounts']>-1e-11]#remove - to renable
    #nzf2.loc[:,'allmeas']=''#2020-01-21 16:54:07#jun 15 2021 removed, putting html in chosenfoods
    
    # 2021-08-03 merged in chosenfoods now. it makes filtering less danger to code change bc its a mess now
    # confid=pd.read_pickle(vdwin+'confid.csv')#Dataframe hacking jupyter notebook is where I built this
    # #nzf2=nzf2.merge(confid,how='left',left_on="NDB_No",right_index=True)#may 4 2020. is confid up-to-date? should be left join?
    # nzf2=nzf2.merge(confid,how='left',left_index=True,right_index=True)#2021 july 6 why did this error appear when I re-enabled load_supplements ??

    #june 6 2021 -the following is from /solution just to quickly file write the solution...

    #nzfz=nzf2[nzf2['amounts']>1e-6].sort_values('Long_Desc',inplace=False,ascending=True)
    nzfz=nzf2[nzf2['amounts']>1e-3].sort_values('amounts',inplace=False,ascending=True)#2023-05-01 1e-6 not aggressive enough filter

    #nzfz['Long_Desc_l']='<a href=http://localhost:5000/food?ndbno='+nzfz.index + '>'+nzfz['Long_Desc']+'</a>'#2023-05-05 #june 15 2021 nzfz.index instead of ndbno
    collist1=['Long_Desc','amounts','allmeas','goto','confid']#2022-03-10 cost->goto
    if RATIOMETRICS:# True:#2021 july 6 temporarily block out to trace, is it in load_supplements?
        # confid=pd.read_pickle(vdwin+'confid.csv')#Dataframe hacking jupyter notebook is where I built this
        # nzfz=nzfz.merge(confid,left_on="NDB_No",right_index=True)
        #jan 23 2021 removed because confid is added by US() so visible in the main foodlist
        cuznf=((npt['309']>0.001)&(npt['312']>0.001 )).to_frame(name="CuZn")
        #nzfz=nzfz.merge(cuznf,left_on="NDB_No",right_index=True)
        nzfz=nzfz.merge(cuznf,left_index=True,right_index=True)#2021 july 6
        collist1=['Long_Desc','amounts','allmeas','cost','confid','CuZn']
        #
        mgcaf=((npt['301']>0.001)&(npt['304']>0.001 )).to_frame(name="MgCa")
        #nzfz=nzfz.merge(mgcaf,left_on="NDB_No",right_index=True)
        nzfz=nzfz.merge(mgcaf,left_index=True,right_index=True)#2021 july 6
        collist1=['Long_Desc','amounts','allmeas','cost','confid','CuZn','MgCa']
        #
        solfibf=((npt['Soluble_Fibre']>0.001)&(npt['291']>0.001 )).to_frame(name="SolFibR")
        #nzfz=nzfz.merge(solfibf,left_on="NDB_No",right_index=True)
        nzfz=nzfz.merge(solfibf,left_index=True,right_index=True)#2021 July 6
    
        collist1=['Long_Desc','amounts','allmeas','cost','confid','CuZn','MgCa','SolFibR']
    #
    #print('nzfz cols=',nzfz.columns)
    global AMnzfz,PMnzfz
    # AMnzfz=nzfz.copy();
    # AMnzfz.update(s.primalVariableSolution['AMamounts']
    # PMnzfz=nzfz.copy
    #nzfz=nzf[nzf['amounts']>1e-6].sort_values('amounts',inplace=False,ascending=True)#2022-01-12 making easier comparison coinor
    #print('nzfz.columns=',nzfz.columns)
    
    # with open(get_vdwin()+'solution-cplex.html', 'w') as fo:#2022-04-16 removed, some bug here
    #     fo.write(flask.render_template('solution.html',title='cplexsolution',tables=[nzfz[collist1].to_html(index=False,escape=False,table_id='us',classes='fixhead')]))#2020-02-04 10:13:14 messing up scroll bar because this list becomes very large
    if (False):#not noaacks):
        slackscplex("slacks-cplex.html")
    #june 6 2021 should make a subdir and write out each of the foods in solution so they can be browsed offline 
    # (and then also each nutrient as well ? 
    # bc right now , all these depend on the model variable remaining in memory when you want to take it apart.
    #global nzfz
    #solution('solutioncplex.html')#2022-01-12 save this sorted for comparison with coinor
    #cache.add("nzf",nzf2)#2022-04-02
    #return (nzf2,una)#2022-04-02 cache result for delta in us2
    #return(get_nzf(nzf2),una)#2022-10-04 todo get_nzf should move up the call chain so that only flask calls invoke it..
    return(nzfz)#2023-05-01 change from nzf2  #2022-11-27

#slacks,measures
#nut_data_datasrc=pd.read_pickle('nut_data_datasrc')#todo lazy load
# @app.route('/slackscplex')
# def slackscplx(fname='slackscplex.html'):#2022-10-06 adding interface for jupyter as well as flask
#     global AMPM
#     obj,st=slackscplex(fname)
#     #do formatting for flask+datatables
#     if AMPM:
#         with open(get_vdwin()+fname, 'w') as fo:
#             fo.write(flask.render_template('viewst.html',title='cplexslacks',objective3=obj,tables=[st.to_html(index=True,escape=False,table_id='st'),AMst.to_html(index=True,escape=False,table_id='AMst'),PMst.to_html(index=True,escape=False,table_id='PMst')]))
#         return (flask.render_template('viewst.html',title='slacks',objective3=obj,tables=[st.to_html(index=True,escape=False,table_id='st'),AMst.to_html(index=True,escape=False,table_id='AMst'),PMst.to_html(index=True,escape=False,table_id='PMst')]))

#     else:
#         with open(get_vdwin()+fname, 'w') as fo:
#             fo.write(flask.render_template('viewst.html',title='cplexslacks',objective3=obj,tables=[st.to_html(index=True,escape=False,table_id='st')]))
#         return (flask.render_template('viewst.html',title='slacks',objective3=obj,tables=[st.to_html(index=True,escape=False,table_id='st')]))

        #print("slacks() file wrote.")
        #return (flask.render_template('viewst.html',title='slacks',objective3=obj,tables=[st.to_html(index=True,escape=False,table_id='st'),AMst.to_html(index=True,escape=False,table_id='AMst'),PMst.to_html(index=True,escape=False,table_id='PMst')]))

def slackscplex(fname='slackscplex.html'):#2022-01-12. the filename to write to. intended for slacks-cplex.html comparison to coinor output
    # 2022-10-06 returns obj,st
    #the slacks table is bascially consdf. for  ratiometric constraints, there will be 3 items (upper, lower, actual)
    #questioning the wisdom of this generalization - just because one stupid book expressed nutrient ratios as a range.
    #2021-09-07 also, sodium/potassium ratio idea conflicts with sodium sensitivity idea. that lots of sodium is only bad if you dont exercise or already have hi bp
    #global st #rebuild each time, dont load file june 27 2020
    # april 24 2020 two thoughts from here - 
    # the ratios that are added in (this function) can have low and high slack costs..maybe that caculation should 
    #happend after the ratio lines are added.
    #AND this idea of having two constraints auto generated out of a single one can simulat piecewise linear...
    # so that it will have a slight preference for more of a nutrient within the hard range set by iom etc.
    # so the upper will have a high upper slackslope, a small lower slackslope,
    # and the lower bound will have zero upper slackslope and high lower slackslope
    global AMAc,PMAc,A,s,obj,consdf,AMconsdf,PMconsdf,st,slacks1,slacks2,nzfz
    
    st=consdf[['NutrDesc','NutrDesc1','min','max','loslack2','hislack2']].copy()#april 25 2021 made st an explicit copy to avoid warning on .loc below#.merge(nutr_def[['NutrDesc']],left_index=True,right_index=True,how='left')
    global lslacknames,lsvars,usvars
    global prob
    global AMAc,PMAc,A
    global npt,AMnpt,PMnpt    
    A=np.matrix(npt)
    #if vectorvars:#2025-3-24
        #print("vectorvars.")
    st.loc[:,'-slacks']=lsvars.amounts.values#amounts.values# for i in range(len(lsvars))]
    st.loc[:,'+slacks']=usvars.amounts.values# for i in range(len(usvars))]
    # else:
    #     st.loc[:,'-slacks']=[lsvars[i].value for i in range(len(lsvars))]
    #     st.loc[:,'+slacks']=[usvars[i].value for i in range(len(usvars))]


#    st.loc[:,'-slacks']=problem.solution.get_values(lslacknames)#s.primalVariableSolution['slacks1']#sol[nf:nf+ncons] # importnt: st must be ordered like consdf

    if (AMPM):#2022-01-21 ampm disable for now bc cplex 
        global AMlslacknames,PMlslacknames
        global AMuslacknames,AMlslacknames
        global PMuslacknames,PMlslacknames
        AMst=AMconsdf[['NutrDesc','NutrDesc1','min','max','loslack2','hislack2']].copy()#april 25 2021 made st an explicit copy to avoid warning on .loc below#.merge(nutr_def[['NutrDesc']],left_index=True,right_index=True,how='left')
        PMst=PMconsdf[['NutrDesc','NutrDesc1','min','max','loslack2','hislack2']].copy()#april 25 2021 made st an explicit copy to avoid warning on .loc below#.merge(nutr_def[['NutrDesc']],left_index=True,right_index=True,how='left')
        AMAc=np.matrix(AMnpt);PMAc=np.matrix(PMnpt)
        AMst.loc[:,'-slacks']=problem.solution.get_values(AMlslacknames)
        PMst.loc[:,'-slacks']=problem.solution.get_values(PMlslacknames)
        AMst.sort_index(axis='index',inplace=True)
        AMst.loc[:,'loslack']=AMconsdf['loslack2'].values.astype(np.double)#obj[nf:nf+ncons]2020-02-02 11:58:41 the unnormalized value. for tweaking slack values on special nutrients like m+c
        AMst.sort_index(axis='index',inplace=True)
        AMst.loc[:,'+slacks']=problem.solution.get_values(AMuslacknames)#.primalVariableSolution['AMslacks2']#sol[nf+ncons:]
        AMst.sort_index(axis='index',inplace=True)
        AMst.loc[:,'hislack_n']=AMconsdf['hislack2']#obj[nf+ncons:]

        PMst.sort_index(axis='index',inplace=True)
        PMst.loc[:,'loslack']=PMconsdf['loslack2'].values.astype(np.double)#obj[nf:nf+ncons]2020-02-02 11:58:41 the unnormalized value. for tweaking slack values on special nutrients like m+c
        PMst.sort_index(axis='index',inplace=True)
        global PMuslacknames
        PMst.loc[:,'+slacks']=problem.solution.get_values(PMuslacknames)#s.primalVariableSolution['PMslacks2']#sol[nf+ncons:]
        PMst.sort_index(axis='index',inplace=True)
        PMst.loc[:,'hislack_n']=PMconsdf['hislack2']#obj[nf+ncons:]
        AMst.loc[:,'+slacks cost']=problem.solution.get_values(AMuslacknames)*AMconsdf['hislack2']# s.primalVariableSolution['AMslacks2']#sol[nf+ncons:]*obj[nf+ncons:]#feb 28 2021 putting this back. this indicates which nutrient is most responsible for distortion
        AMst.loc[:,'-slacks cost']=problem.solution.get_values(AMlslacknames)*AMconsdf['loslack2']#s.primalVariableSolution['AMslacks1']#sol[nf:nf+ncons]*obj[nf:nf+ncons]# april 24 2021 changed from st['-slacks cost']=sol[nf:nf+ncons]*obj[nf:nf+ncons] # i.e. setting on copy warning
        AMsoll=AMAc.transpose().dot(chosenfoods_cplex[['AMamounts']].values)#soll=A[:nf,:ncons].transpose().dot(chosenfoods_cplex[['amounts']].values)
        AMst.loc[:,'nuta']=AMsoll
        PMst.loc[:,'+slacks cost']=problem.solution.get_values(PMuslacknames)*PMconsdf['hislack2']#s.primalVariableSolution['PMslacks2']#sol[nf+ncons:]*obj[nf+ncons:]#feb 28 2021 putting this back. this indicates which nutrient is most responsible for distortion
        PMst.loc[:,'-slacks cost']=problem.solution.get_values(PMlslacknames)*PMconsdf['loslack2']#s.primalVariableSolution['PMslacks1']#sol[nf:nf+ncons]*obj[nf:nf+ncons]# april 24 2021 changed from st['-slacks cost']=sol[nf:nf+ncons]*obj[nf:nf+ncons] # i.e. setting on copy warning
        PMsoll=PMAc.transpose().dot(chosenfoods_cplex[['PMamounts']].values)#soll=A[:nf,:ncons].transpose().dot(chosenfoods_cplex[['amounts']].values)
        PMst.loc[:,'nuta']=PMsoll

    st.sort_index(axis='index',inplace=True)

    st.sort_index(axis='index',inplace=True)
    st.loc[:,'loslack']=consdf['loslack2'].values.astype(np.double)#obj[nf:nf+ncons]2020-02-02 11:58:41 the unnormalized value. for tweaking slack values on special nutrients like m+c
    st.sort_index(axis='index',inplace=True)
    #st.loc[:,'+slacks']=problem.solution.get_values(lslacknames)#s.primalVariableSolution['slacks2']#sol[nf+ncons:]
    st.sort_index(axis='index',inplace=True)
    st.loc[:,'hislack_n']=consdf['hislack2']#obj[nf+ncons:]


    #WHOAA 2020-02-12 14:54:57 what does values do here ? without it the data is corrupted. (although not in the jupyter notebook!!)
    #st.loc[:,'hislack']=consdf.loc[:,'hislack'].values.astype(np.double)#.copy()#obj[nf:nf+ncons]2020-02-02 11:58:41 the unnormalized value. for tweaking slack values on special nutrients like m+c
    #removed july 27 2020, 32 degrees hottest day of the year
    obj=0#prob.value#2024-8-28 whats this for ? #solver.Objective().Value()
    #soll=Ac.transpose().dot(chosenfoods_cplex[['amounts']].values)#soll=A[:nf,:ncons].transpose().dot(chosenfoods_cplex[['amounts']].values)
    soll=A.transpose().dot(chosenfoods_cplex[['amounts']].values)#soll=A[:nf,:ncons].transpose().dot(chosenfoods_cplex[['amounts']].values)
    st.loc[:,'nuta']=soll
    #add a parameter for the actual value of ratios, because the upper and lower are not individually as usefull
    if 'ratiosf' in globals():
        stratios=pd.DataFrame(index=ratiosf.index)
        for index, row in ratiosf.iterrows():
            stratios.loc[index,'nuta']=st.loc[row['numerator'],'nuta']/st.loc[row['denominator'],'nuta']
            stratios.loc[index,'min']=row['Loratio'];stratios.loc[index,'max']=row['Hiratio']
            stratios.loc[index,'NutrDesc1']=row['NutrDesc1']#todo npt only has the Hi and Lo as separate ratio targets...a simple fix would be just make Nutrdesc1 in the spreadsheet the name of either the Lo or the Hi....or maybe create yet another one which is the target between the midway point (presumably the ideal)
        
            stratios.loc[index,'hislack2']=st.loc[index+'Hi','hislack2']#2022-10-06
            stratios.loc[index,'loslack2']=st.loc[index+'Lo','loslack2']
            #shit, how is mgratio linked to mgratiohi (the +slacks i need) ??
            stratios.loc[index,'+slacks']=st.loc[index+'Hi','+slacks']#2022-10-06
            stratios.loc[index,'-slacks']=st.loc[index+'Lo','-slacks']
            
        #st=st.append(stratios,ignore_index=False,verify_integrity=True)
        st = pd.concat([st, stratios], ignore_index=False, verify_integrity=True)#2024-2-1

    st.loc[:,'+slacks cost']=st.loc[:,'+slacks']*st.loc[:,'hislack2']#2022-10-06 relocated this after ratiof patch
    st.loc[:,'-slacks cost']=st.loc[:,'-slacks']*st.loc[:,'loslack2']#use st, not consdf
       
    st['lomargin']=(st['nuta']-st['min'])/(st['max']-st['min'])# sort ascending; negative is deficient, larger is better. the marginal nutrients are the ones you want to ensure solid data.
    st['himargin']=(st['max']-st['nuta'])/(st['max']-st['min'])#2020-02-04 10:57:04 slacks arent accurate within bounds (they are constrained positive)
    st.sort_values('lomargin',ascending=True,inplace=True)
    st.fillna({'+slacks cost':'','-slacks cost':''},inplace=True)
  
    #print(stratios)
    #print("person=",person,"gotostuff=",consdf.loc['gotoratio'])
    #print(st['max'])print(st.to_html(table_id='st',escape=False))    
    #print(st.loc['gotoratio'])  #  print(st.loc['gotoratio','max'])
    
    #return (flask.render_template('viewst.html',tables=[st.style.set_table_attributes('table-layout="auto",id="st"').render()]))
    #st.to_html(vdwin+'lo slacks.html',index=True,classes='',table_id='slacks')
    return obj,st

# @app.route('/foodlist_nutdata')#/<nutrno>')#2021 july 5 this is not called. its a great example of how much data is actually not there or unreliable
# def foodlist_nutdata():
#     global foodlist,nut_data_datasrc
 
#  #Dec 24 2019 nut_data display (with meta merged in), and foodlist amounts as filter...
#  #intended to do complete background check on every solution 
#  # its a separate page because a single food could have any number of metadata on each nutrient,
#  #which should be looked at separately bc maybe the metadata is garbage and just more confusion...
#  #the problem comes back where the amounts have to match up with the foods...maybe the metadata should
#  # get merged with the foods, so that chosenfoods has more columns...or foodlist is just left joined to the datasrc
#     t=foodlist[foodlist['amounts']>1e-2].merge(nut_data_datasrc,on='NDB_No')#2021 July 5 todo fix
#     t=foodlist[foodlist['amounts']>1e-2].merge(nut_data_datasrc,left_index=True,right_on='NDB_No')#2021 July 5 todo fix

#     return (flask.render_template('viewnutfocus.html',title='foodlistnutdata',tables=[t[['Long_Desc','amounts','Nutr_No','ref','SrcCd_Desc','Deriv_Desc', 'Num_Data_Pts', 'Std_Error', 'Src_Cd'
#     ,'Add_Nutr_Mark', 'Num_Studies', 'Min', 'Max',
#        'DF', 'Low_EB', 'Up_EB', 'Stat_cmt', 'AddMod_Date', 'CC']].to_html(index=True,escape=False,table_id='foodlist')]))

# @app.after_request #added june 27 2020
# def add_header(response):
#     response.headers['X-UA-Compatible']='IE=Edge,chrome=1'
#     if ('Cache-Control' not in response.headers):
#         response.headers['Cache-Control']='public,max-age=600'
#     return response


# @app.route('/nutfocus')#/<nutrno>')#called from viewst.html (slacks table nutrient hyperlink)
# def nfp():
#     nutrno = request.args.get('nutrno');print('nutrno=',nutrno)
#     t,name=nutfocus(nutrno)
#     return (flask.render_template('viewnutfocus.html',title=name,tables=[t[['Long_Desc','amounts','nutrno='+nutrno,nutrno]].to_html(index=True,escape=False,table_id='foodlist')]))

def nutfocus(nutrno):
    global foodlist,nut_data_datasrc,st,npt#full
    # dec 18 2019 - I had put this off for a week when it became apparent there is some unbackedup work on the old hard Drive
    # and that this new laptop can take another one, so I can get access to it (and maybe some older HDs that had crashed??)
    # but the stupid cable that I had to special order is "in process" probably until january...so doing this because
    # I know there is no work in progress on this
    # This is just the foodlist, except with an extra column for the requested nutrient broken out,
    # and probably a few other columns removed. its a separate page so as not to interfere with 
    # the collist needed for datatables and regexing

    #Dec 26 this is to review literature specific to a nutrient (came out of b12 problem`)
    #t=foodlist[foodlist['amounts']>-1e-2][['NDB_No','Long_Desc','amounts']].merge(npt[['208',nutrno]],left_on='NDB_No',right_index=True) 
    #t=foodlist[foodlist['amounts']>-1e-2][['Long_Desc','amounts']].merge(npt[['208',nutrno]],left_index=True,right_index=True)#July 3 2021
    #npt=nptfull#2022-02-08 searching for superfoods...
    t=foodlist[foodlist['amounts']>-1e-2][['Long_Desc','amounts']].merge(npt[[nutrno]],left_index=True,right_index=True)#Dec 15 2021

    # foodlist=chosenfoods[collist].merge(npt[['208',nutrno]],left_on='NDB_No',right_index=True)
    #print("t.columns=",t.columns)
    t['nutrno='+nutrno]=t[nutrno]*t['amounts']
    # t['cals']=t['208']*t['amounts']
    t.sort_values('nutrno='+nutrno,inplace=True,ascending=False)#this is an arbitrary sort order ... 
    #print('nutfocus t shape=',t.shape)
    try:
        name=st.loc[nutrno,'NutrDesc']
    except KeyError:
        slacks()
    name=st.loc[nutrno,'NutrDesc']#remove temporary july 26

    #print('t.columns=',t.columns)
    return(t,name )
    #return (flask.render_template('viewnutfocus.html',title=name,tables=[t[['Long_Desc','amounts','nutrno='+nutrno,nutrno]].to_html(index=True,escape=False,table_id='foodlist')]))
    #return (flask.render_template('vnf2.html',title=name,tables=[t[['Long_Desc','amounts','nutrno='+nutrno,nutrno]].to_html(index=True,escape=False,table_id='foodlist')]))

# @app.route('/bshi')#/<nutrno>')
def bshi():
    #global solm #2020-02-08 16:29:00 added. the per-food nutrient amounts solution matrix, 
    # to be joined to sr28 metadata
    solm=npt.mul(chosenfoods[['amounts']].values)
    npt1=solm

    npt1t=npt1.transpose()# only the nutrients with metadata in nut_data
    npt1=npt1t[npt1t.index.isin(nutr_def1.index)].transpose()
    #npt1.columns#np22[np22.index.isin(nutr_def.index)]
    npt2=npt1/consdf.loc[consdf.index.isin(nutr_def1.index),'max']#.shape #todo another table for excessive nutrients (manganese, vitA, iron ...)
    
    #maybe next 3 lines not nec
    npt3=npt2.transpose()#unstack().reset_index()
    #print('npt3=',npt3.head())
    #npt3['nutsum']=npt3.agg('sum',axis='columns')# is this necessary, other than debugging see next cell -YES it gives you a header column for nice looking tabulator
    np33=npt3.agg('sum',axis='columns').to_frame()# use this to sort by merge later. todo set column name here.
    #print('np33=',np33.head())
    np22=npt2.unstack().to_frame().reset_index(level=1)#;pd.DataFrame.reset_index(level=0)
    #print('np22=',np22.head())
    np222=np22.merge(np33,left_index=True,right_index=True)
    #print('np222=',np222.head())
    #npu=np222.reset_index().rename(columns={'index':'Nutr_No','0_x':'contrib','0_y':'diet'}).set_index(['Nutr_No','NDB_No'])
    nput=np222.reset_index()
    #print("nput=",nput.head())
    npu=nput.rename(columns={'index':'nut','0_x':'contib','0_y':'diet'});npu#.set_index(['nut','NDB_No']);npu
    #print('npu=',npu.head())
    #print("pd.__version__=",pd.__version__)
    npu1=npu[npu['contib']>0]
    npu1.rename(columns={'nut':'Nutr_No'},inplace=True)
    #print('npu1=',npu1.head())

    # whoops, maybe to see zeros 2020-02-08 10:57:15 todo
    #2020-02-11 09:43:29 todo optimization : almost everything up to this point same for both low and high
    #maybe generate both tables side by side on a single page
    #should profile this
    npf=npu1.sort_values(['diet'],ascending=[False])#
    #npfc=npf[npf['contrib']>0]# whoops, maybe to see zeros 2020-02-08 10:57:15 todo
    #print('npf=',npf.head())
    npfc=npf.groupby(['Nutr_No'],sort=False)
    npfc1=npfc.apply(pd.DataFrame.nsmallest,50,'contib')#june 30 flipped from nsmallest to nlargest (but that was wrong)
    npfc11=npfc1.reset_index(drop=True)
    nddi=nut_data_datasrc.set_index(['Nutr_No','NDB_No'])# pickle this out
    nddi.sort_index(inplace=True)#.groupby('Nutr_No')
    ndds=nut_data_datasrc.stack()#set_index(['Nutr_No','NDB_No'])
    #print("nddi=",nddi.head())
    #print("npfc11=",npfc11.head())
    
    npd=npfc11.merge(nddi,how='left',left_on=['Nutr_No','NDB_No'],right_on=['Nutr_No','NDB_No'])
    nutr_def1.index.rename('Nutr_No',inplace=True)#reindex()names
    npd1=npd.merge(nutr_def1,left_on='Nutr_No',right_index=True,how='left')
    npd2=npd1.merge(chosenfoods[['NDB_No','Shrt_Desc']],left_on='NDB_No',right_on='NDB_No',how='left')
    npd3=npd2.set_index(['NutrDesc','Shrt_Desc'])#.index,nutr_def.index
    #todo footnotes etc

    #     with open('my_file.html', 'w') as fo:
    #     fo.write(tsod.to_html())
    #     47

    # You can use pandas.DataFrame.to_html().

    # Example:
    # >>> import numpy as np
    # >>> from pandas import *
    # >>> df = DataFrame({'foo1' : np.random.randn(2),
    #                     'foo2' : np.random.randn(2)})
    # >>> df.to_html('filename.html')
    # This will save the following html to filename.html.

    npd3.to_html(get_vdwin()+'bshi.html',index=True,classes='',table_id='bshi')

    # return (flask.render_template('viewnutfocus.html',title='BSHI',tables=[npd3.to_html(index=True,escape=False,table_id='foodlist')]))

    #This deal with uncertain of accuracy of food.  With missing data, the unaccuracy has another layer of uncertainty,
    #which is that the missing data might show this food would cause toxicity. as of jan 24 2021, those nutrients are:
    #I can add a lot of hasX in chosenfoods, it is basically a transposed and binarized npt.
    #Also confid can be added, and could be used along with food group to reduce database size for use
    # with semicontinuous variables and using free version of ibm solver. THen Im implicitly taking nutritional
    # advice from people who intentionally swapped cocoa data.
    # Confusion over the fact that adding cocoa doesnt create a copper problem.
    # As of jan 24 2021, I'm only low in calcium, but could I create new entries for mg and zn supplements?

# @app.route('/bs')#/<nutrno>')
def bs():
    #global solm #2020-02-08 16:29:00 added. the per-food nutrient amounts solution matrix, to be joined to sr28 metadata
    solm=npt.mul(chosenfoods[['amounts']].values)
    npt1=solm

    npt1t=npt1.transpose()# only the nutrients with metadata in nut_data
    npt1=npt1t[npt1t.index.isin(nutr_def1.index)].transpose()
    #npt1.columns#np22[np22.index.isin(nutr_def.index)]
    npt2=npt1/consdf.loc[consdf.index.isin(nutr_def1.index),'min']#.shape #todo another table for excessive nutrients (manganese, vitA, iron ...)
    
    #maybe next 3 lines not nec
    npt3=npt2.transpose()#unstack().reset_index()
    #print('npt3=',npt3.head())
    #npt3['nutsum']=npt3.agg('sum',axis='columns')# is this necessary, other than debugging see next cell -YES it gives you a header column for nice looking tabulator
    np33=npt3.agg('sum',axis='columns').to_frame()# use this to sort by merge later. todo set column name here.
    #print('np33=',np33.head())
    np22=npt2.unstack().to_frame().reset_index(level=1)#;pd.DataFrame.reset_index(level=0)
    #print('np22=',np22.head())
    np222=np22.merge(np33,left_index=True,right_index=True)
    #print('np222=',np222.head())
    #npu=np222.reset_index().rename(columns={'index':'Nutr_No','0_x':'contrib','0_y':'diet'}).set_index(['Nutr_No','NDB_No'])
    nput=np222.reset_index()
    #print("nput=",nput.head())
    npu=nput.rename(columns={'index':'nut','0_x':'contib','0_y':'diet'});npu#.set_index(['nut','NDB_No']);npu
    #print('npu=',npu.head())
    #print("pd.__version__=",pd.__version__)
    npu1=npu[npu['contib']>0]
    npu1.rename(columns={'nut':'Nutr_No'},inplace=True)
    #print('npu1=',npu1.head())

    # whoops, maybe to see zeros 2020-02-08 10:57:15 todo
    npf=npu1.sort_values(['diet'],ascending=[True])#y is the sum
    #npfc=npf[npf['contrib']>0]# whoops, maybe to see zeros 2020-02-08 10:57:15 todo
    #print('npf=',npf.head())
    npfc=npf.groupby(['Nutr_No'],sort=False)
    npfc1=npfc.apply(pd.DataFrame.nlargest,5,'contib')
    npfc11=npfc1.reset_index(drop=True)
    nddi=nut_data_datasrc.set_index(['Nutr_No','NDB_No'])# pickle this out
    nddi.sort_index(inplace=True)#.groupby('Nutr_No')
    ndds=nut_data_datasrc.stack()#set_index(['Nutr_No','NDB_No'])
    #print("nddi=",nddi.head())
    #print("npfc11=",npfc11.head())
    
    npd=npfc11.merge(nddi,how='left',left_on=['Nutr_No','NDB_No'],right_on=['Nutr_No','NDB_No'])
    nutr_def1.index.rename('Nutr_No',inplace=True)#reindex()names
    npd1=npd.merge(nutr_def1,left_on='Nutr_No',right_index=True,how='left')
    npd2=npd1.merge(chosenfoods[['NDB_No','Shrt_Desc']],left_on='NDB_No',right_on='NDB_No',how='left')
    npd3=npd2.set_index(['NutrDesc','Shrt_Desc'])#.index,nutr_def.index
    #todo footnotes etc
    npd3.to_html(get_vdwin()+'bs.html',index=True,classes='',table_id='bs')

    # return (flask.render_template('viewnutfocus-multiindex.html',title='BS',tables=[npd3.to_html(index=True,escape=False,table_id='foodlist',classes='fh')]))
#todo lazy load
#nutr_def1=pd.read_csv(usda_home+'NUTR_DEF.txt',header=None,names=['Nutr_No','Units','Tagname','NutrDesc','Num_Dec','SR_Order'],sep='^',dtype=str,engine='python',quotechar='~',encoding = "ISO-8859-1")#,index_col=0)
#nutr_def1.set_index('Nutr_No',inplace=True, verify_integrity=True)#food_des=pd.read_csv('FOOD_DES.txt',header=None,names=['NDB_No','FdGrp_Cd','Long_Desc','Shrt_Desc','ComName','ManufacName','Survey','Ref_desc','Refuse','SciName','N_Factor',' Pro_Factor','Fat_Factor','CHO_Factor'],sep='^',dtype=str,engine='python',quotechar='~',index_col=0)


#todo this, and nut_data should have new names at each stage of augmentation 2020-02-08 09:34:26 
# @app.route('/litfocus')#/<nutrno>')
def litfocus():
    #global foodlist
    # dec 20 this is to look at the literature references for the foods
    # would have done this in jupyter, but cannot view long tables, or dynamically sort like datatables
 #Dec 26 2019 this is a more general display with all foods, all nutrients, but only those with any (or a threshhold amount)
 #its really to see if the metadata seems reliable at all or usefull.
    nutrno = request.args.get('nutrno')
    t=nut_data_datasrc[nut_data_datasrc['Nutr_No']==nutrno]
    # return (flask.render_template('viewnutfocus.html',title='litfocus',tables=[t.to_html(index=True,escape=False,table_id='foodlist')]))

    # return (flask.render_template('viewnutfocus.html',tables=[chosenfoods.to_html(index=True,escape=False,table_id='foodlist')]))

#foodfootnotes=pd.read_pickle('./foodfootnotes')
#nutfootnotes=pd.read_pickle('./nutfootnotes')
#todo lazy load #allfootnotes=pd.read_pickle('./nut_data_datasrc_footnotes')#2020-03-03 17:46:53 new, pre-merged table, reduce reliance on slow script or risky c++
#todo lazy load nutr_def=pd.read_pickle('./nutr_def')

# @app.route('/food')#/<nutrno>')
# def ff():
#     ndbno = request.args.get('ndbno')
#     name,t=foodfocus(ndbno)
#     return (flask.render_template('viewnutfocus.html',title=name,tables=[t.to_html(index=True,escape=False,table_id='foodlist')]))
 
def foodfocus(ndbno):
    global st
    #2020-03-02 11:54:49 this needs to be processed for all foods into a static table. do the processing in python so that the c++ version of this
    #just does a table filter
    global allfootnotes,nutfootnotes,food_des,foodlist
    #drill down into specific food items arising in the diet. the nutrient composition, the percentage of requirements,
    #and all the footnotes (per food and per food.nutrient)
    #2020-03-03 17:43:10 stuff below is done in python, the goal being to just do lookups rather than have to call c++ or javascript and have to debug that too

    # t=nut_data_datasrc[nut_data_datasrc['NDB_No']==ndbno]#[['Nutr_No']]
    # t=t.merge(nutfootnotes[nutfootnotes.index==ndbno],how='outer',on='Nutr_No')
    # t=foodfootnotes[foodfootnotes.index==ndbno].append(t)
    #foodlist.to_pickle('./foodlist')

    #todo 2020-03-09 19:02:45 dropna doesnt do anything ...
    try:#2022-06-06
        st
    except NameError:
        st=pd.read_csv(get_vdwin()+'st.csv',index_col=0,keep_default_na=False)
    try:
        allfootnotes
    except NameError:
        allfootnotes=pd.read_pickle('./nut_data_datasrc_footnotes')#2020-03-03 17:46:53 new, pre-merged table, reduce reliance on slow script or risky c++

    t1=allfootnotes[allfootnotes['NDB_No']==ndbno].sort_values('fnl')
    t=t1.dropna(axis='columns',how='all')#really the table will be sorting also for the minratio, so just keep this
    t=t.merge(st[['min','max']],right_index=True,left_on='Nutr_No')# can this also be pre-merged? maybe st should go away and also be a lookup from this giant table
    #nzf2=get_nzf()
    try:
        #t['nutval*amount']=t['Nutr_Val']*foodlist.set_index('NDB_No').loc[ndbno,'amounts']#'solution amount'? #goto gives warning about setting value of slice 2020-03-07 09:35:26
        t['nutval*amount']=t['Nutr_Val']*nzf2.loc[ndbno,'amounts']#'solution amount'? #goto gives warning about setting value of slice 2020-03-07 09:35:26
        t['minratio']=t['nutval*amount']/t['min']
        t['maxratio']=t['nutval*amount']/t['max']
        
    except NameError:
        print("huh?")
    # t=nut_data_datasrc[nut_data_datasrc['NDB_No']==ndbno]
    nutr_def=pd.read_pickle('./nutr_def')
    t=t.merge(nutr_def,left_on='Nutr_No',right_index=True) #wy not set the index and columns of npt to the descriptions rather than the codes, and optimize all these pointless merges away
    # t=t.merge(foodfootnotes[foodfootnotes.index==ndbno],how='outer',on='Nutr_No')
    # t=t.merge(nutfootnotes[nutfootnotes.index==ndbno],how='outer',on='Nutr_No')

    tc=t.columns
    #t=t[    [  tc[26],tc[12],tc[9],tc[10],tc[13],tc[14],tc[16],tc[17],tc[19] ,tc[21],tc[22],tc[24],tc[32] ]    ]

    #	'NDB_No'    #'Nutr_No'	Src_Cd			,'NutrDesc'
    # 	'Tagname','Units','CC','Deriv_Cd'

    t=t[['NutrDesc','minratio','maxratio','nutval*amount','Nutr_Val','Num_Data_Pts','Num_Studies','Ref_NDB_No','AddMod_Date','Deriv_Desc','SrcCd_Desc','DF','Stat_cmt','Std_Error','Low_EB','Up_EB','Max','Min','Add_Nutr_Mark','min','max','Num_Dec','SR_Order']]#['nutrient']=t['NutrDesc']
    #os.chdir(vdwin)
    food_des=pd.read_pickle('food_desusda')#2022-11-29 good test of symlinks-just link data to code, so that the venv can be deleted and save cloud space without any actual code data physically in the venv

    name=food_des.loc[ndbno,'Shrt_Desc']

    #    t.to_html(vdwin+'food='+name+'.html',index=True,classes='',table_id=name)#2020-05-18 09:36:35 need to escape the food name "/" characters being used..
    return name,t

#from requests.utils import requote_uri 2022-11-17 removed - error
#@app.route('/slacks')
def slacks():#the slacks table is bascially consdf. for  ratiometric constraints, there will be 3 items (upper, lower, actual)
    #questioning the wisdom of this generalization - just because one stupid book expressed nutrient ratios as a range.
    #2021-09-07 also, sodium/potassium ratio idea conflicts with sodium sensitivity idea. that lots of sodium is only bad if you dont exercise or already have hi bp
    #global st #rebuild each time, dont load file june 27 2020
    # april 24 2020 two thoughts from here - 
    # the ratios that are added in (this function) can have low and high slack costs..maybe that caculation should 
    #happend after the ratio lines are added.
    #AND this idea of having two constraints auto generated out of a single one can simulat piecewise linear...
    # so that it will have a slight preference for more of a nutrient within the hard range set by iom etc.
    # so the upper will have a high upper slackslope, a small lower slackslope,
    # and the lower bound will have zero upper slackslope and high lower slackslope
    global AMAc,PMAc,Ac,s,obj,consdf,AMconsdf,PMconsdf,st,slacks1,slacks2
    #2019-02-11 14:28:50 python: ClpSimplex.cpp:3926: bool ClpSimplex::createRim(int, bool, int): Assertion `fabs(obj[i]) < 1.0e25' failed.
    #[I 14:27:48.150 NotebookApp] KernelRestarter: restarting kernel (1/5), keep random ports W
    #test
    # st['-slacks']=sol[nf:nf+ncons]
    # st['+slacks']=sol[nf+ncons:]
    # st['+slacks']=sol[nf:nf+ncons]*obj[nf:nf+ncons]
    # st['-slacks']=sol[nf+ncons:]*obj[nf+ncons:]
    
    st=consdf[['NutrDesc','NutrDesc1','min','max','loslack2','hislack2']].copy()#april 25 2021 made st an explicit copy to avoid warning on .loc below#.merge(nutr_def[['NutrDesc']],left_index=True,right_index=True,how='left')
    if (AMPM):
        AMst=AMconsdf[['NutrDesc','NutrDesc1','min','max','loslack2','hislack2']].copy()#april 25 2021 made st an explicit copy to avoid warning on .loc below#.merge(nutr_def[['NutrDesc']],left_index=True,right_index=True,how='left')
        PMst=PMconsdf[['NutrDesc','NutrDesc1','min','max','loslack2','hislack2']].copy()#april 25 2021 made st an explicit copy to avoid warning on .loc below#.merge(nutr_def[['NutrDesc']],left_index=True,right_index=True,how='left')
        # AMst.loc[:,'min']=consdf['Ammin'];AMst.loc[:,'max']=consdf['Ammax']#I already did this...
        # PMst.loc[:,'min']=consdf['Pmmin'];PMst.loc[:,'max']=consdf['Pmmax']
        print("AMconsdf=",AMconsdf)
        # AMconsdf.rename(index=lambda s: 'AM'+s,inplace=True)
        # PMconsdf.rename(index=lambda s: 'PM'+s,inplace=True)
        # st=st.append(AMconsdf[['NutrDesc','NutrDesc1','min','max','loslack2','hislack2']].copy(),ignore_index=False,verify_integrity=True)
        # st=st.append(PMconsdf[['NutrDesc','NutrDesc1','min','max','loslack2','hislack2']].copy(),ignore_index=False,verify_integrity=True)
        AMst.loc[:,'-slacks']=s.primalVariableSolution['AMslacks1']
        PMst.loc[:,'-slacks']=s.primalVariableSolution['PMslacks1']

    #st['NutrDesc1']='<a href=http://localhost:5000/nutfocus?nutrno='+st.index + '>'+st['NutrDesc']+'</a>'
    #print("st=",st,"npt['255']=",npt['255'])
    st.loc[:,'-slacks']=s.primalVariableSolution['slacks1']#sol[nf:nf+ncons] # importnt: st must be ordered like consdf
    
    st.sort_index(axis='index',inplace=True)

    #2020-05-19 11:12:51 do I have to re-sort this after each write ?? optimize by keeping everything numpy until just before to_html
    #may 10 2021 removed loslack_n - redundant ?
    #st.loc[:,'loslack_n']=consdf['loslack2']#obj[nf:nf+ncons]#2020-02-02 11:58:36 added 2020-02-12 11:14:34 .values.astype(np.double) must be added, AND this is redundant
    st.sort_index(axis='index',inplace=True)
    st.loc[:,'loslack']=consdf['loslack2'].values.astype(np.double)#obj[nf:nf+ncons]2020-02-02 11:58:41 the unnormalized value. for tweaking slack values on special nutrients like m+c
    st.sort_index(axis='index',inplace=True)
    st.loc[:,'+slacks']=s.primalVariableSolution['slacks2']#sol[nf+ncons:]
    st.sort_index(axis='index',inplace=True)
    st.loc[:,'hislack_n']=consdf['hislack2']#obj[nf+ncons:]

    AMst.sort_index(axis='index',inplace=True)
    AMst.loc[:,'loslack']=AMconsdf['loslack2'].values.astype(np.double)#obj[nf:nf+ncons]2020-02-02 11:58:41 the unnormalized value. for tweaking slack values on special nutrients like m+c
    AMst.sort_index(axis='index',inplace=True)
    AMst.loc[:,'+slacks']=s.primalVariableSolution['AMslacks2']#sol[nf+ncons:]
    AMst.sort_index(axis='index',inplace=True)
    AMst.loc[:,'hislack_n']=AMconsdf['hislack2']#obj[nf+ncons:]

    PMst.sort_index(axis='index',inplace=True)
    PMst.loc[:,'loslack']=PMconsdf['loslack2'].values.astype(np.double)#obj[nf:nf+ncons]2020-02-02 11:58:41 the unnormalized value. for tweaking slack values on special nutrients like m+c
    PMst.sort_index(axis='index',inplace=True)
    PMst.loc[:,'+slacks']=s.primalVariableSolution['PMslacks2']#sol[nf+ncons:]
    PMst.sort_index(axis='index',inplace=True)
    PMst.loc[:,'hislack_n']=PMconsdf['hislack2']#obj[nf+ncons:]

    #WHOAA 2020-02-12 14:54:57 what does values do here ? without it the data is corrupted. (although not in the jupyter notebook!!)
    #st.loc[:,'hislack']=consdf.loc[:,'hislack'].values.astype(np.double)#.copy()#obj[nf:nf+ncons]2020-02-02 11:58:41 the unnormalized value. for tweaking slack values on special nutrients like m+c
    #removed july 27 2020, 32 degrees hottest day of the year
    
    st.loc[:,'+slacks cost']=s.primalVariableSolution['slacks2']*consdf['hislack2']#sol[nf+ncons:]*obj[nf+ncons:]#feb 28 2021 putting this back. this indicates which nutrient is most responsible for distortion
    st.loc[:,'-slacks cost']=s.primalVariableSolution['slacks1']*consdf['loslack2']#sol[nf:nf+ncons]*obj[nf:nf+ncons]# april 24 2021 changed from st['-slacks cost']=sol[nf:nf+ncons]*obj[nf:nf+ncons] # i.e. setting on copy warning
    soll=Ac.transpose().dot(chosenfoods[['amounts']].values)#soll=A[:nf,:ncons].transpose().dot(chosenfoods[['amounts']].values)
    st.loc[:,'nuta']=soll

    AMst.loc[:,'+slacks cost']=s.primalVariableSolution['AMslacks2']*AMconsdf['hislack2']#sol[nf+ncons:]*obj[nf+ncons:]#feb 28 2021 putting this back. this indicates which nutrient is most responsible for distortion
    AMst.loc[:,'-slacks cost']=s.primalVariableSolution['AMslacks1']*AMconsdf['loslack2']#sol[nf:nf+ncons]*obj[nf:nf+ncons]# april 24 2021 changed from st['-slacks cost']=sol[nf:nf+ncons]*obj[nf:nf+ncons] # i.e. setting on copy warning
    AMsoll=AMAc.transpose().dot(chosenfoods[['AMamounts']].values)#soll=A[:nf,:ncons].transpose().dot(chosenfoods[['amounts']].values)
    AMst.loc[:,'nuta']=AMsoll

    PMst.loc[:,'+slacks cost']=s.primalVariableSolution['PMslacks2']*PMconsdf['hislack2']#sol[nf+ncons:]*obj[nf+ncons:]#feb 28 2021 putting this back. this indicates which nutrient is most responsible for distortion
    PMst.loc[:,'-slacks cost']=s.primalVariableSolution['PMslacks1']*PMconsdf['loslack2']#sol[nf:nf+ncons]*obj[nf:nf+ncons]# april 24 2021 changed from st['-slacks cost']=sol[nf:nf+ncons]*obj[nf:nf+ncons] # i.e. setting on copy warning
    PMsoll=PMAc.transpose().dot(chosenfoods[['PMamounts']].values)#soll=A[:nf,:ncons].transpose().dot(chosenfoods[['amounts']].values)
    PMst.loc[:,'nuta']=PMsoll


    # print('st[nuta]=',st['nuta'])
    # print("soll=",soll)
    #st['lomargin']=(st['nuta']-st['min']).abs()/st['min']# sort ascending; negative is deficient, larger is better. the marginal nutrients are the ones you want to ensure solid data.
    #st['himargin']=(st['max']-st['nuta']).abs()/st['max']#2020-02-04 10:57:04 slacks arent accurate within bounds (they are constrained positive)
    
    #add a parameter for the actual value of ratios, because the upper and lower are not individually as usefull
    if 'ratiosf' in globals():
        stratios=pd.DataFrame(index=ratiosf.index)
        for index, row in ratiosf.iterrows():
            stratios.loc[index,'nuta']=st.loc[row['numerator'],'nuta']/st.loc[row['denominator'],'nuta']
            stratios.loc[index,'min']=row['Loratio'];stratios.loc[index,'max']=row['Hiratio']
            stratios.loc[index,'NutrDesc1']=row['NutrDesc1']#todo npt only has the Hi and Lo as separate ratio targets...a simple fix would be just make Nutrdesc1 in the spreadsheet the name of either the Lo or the Hi....or maybe create yet another one which is the target between the midway point (presumably the ideal)
        st=st.append(stratios,ignore_index=False,verify_integrity=True)
    
    
    st['lomargin']=(st['nuta']-st['min'])/st['min']# sort ascending; negative is deficient, larger is better. the marginal nutrients are the ones you want to ensure solid data.
    st['himargin']=(st['max']-st['nuta'])/st['max']#2020-02-04 10:57:04 slacks arent accurate within bounds (they are constrained positive)
    st.sort_values('lomargin',ascending=True,inplace=True)
    st.fillna({'+slacks cost':'','-slacks cost':''},inplace=True)
 
    
    #print(stratios)
    #print("person=",person,"gotostuff=",consdf.loc['gotoratio'])
    #print(st['max'])print(st.to_html(table_id='st',escape=False))    
    #print(st.loc['gotoratio'])  #  print(st.loc['gotoratio','max'])
    
    #return (flask.render_template('viewst.html',tables=[st.style.set_table_attributes('table-layout="auto",id="st"').render()]))
    #st.to_html(vdwin+'lo slacks.html',index=True,classes='',table_id='slacks')
    # with open(get_vdwin()+'slacks.html', 'w') as fo:
    #     fo.write(flask.render_template('viewst.html',title='slacks',tables=[st.to_html(index=True,escape=False,table_id='st'),AMst.to_html(index=True,escape=False,table_id='AMst'),PMst.to_html(index=True,escape=False,table_id='PMst')]))
    # print("slacks() file wrote.")
    # return (flask.render_template('viewst.html',title='slacks',tables=[st.to_html(index=True,escape=False,table_id='st'),AMst.to_html(index=True,escape=False,table_id='AMst'),PMst.to_html(index=True,escape=False,table_id='PMst')]))

#this is also associated with a person.(todo) 
#can be associated with the usda 'diet patterns' for the sake of authoritative appearance?
#also can run in notebook, so for testing as well.
#This could be done in javascript/datatables? Probably,but it will run slow. pandas is optimized. how often will this have to run??
#todo:chosenfoods ' pro factor' column leading space in name is tripping up itertuples...
#b=chosenfoods.iloc[:,0].str.contains('',case=False,regex=True)#column matches are ANDed, and ORed across rows..BUT this happens implicitly when I zero the selection max_d
def exclude2(una1):#dataframe of regex strings. rebuilding chosenfoods.  
     for f in una1[collist].itertuples(index=False):
        #for idx,fc in enumerate(f):
        #    print(fc,f[idx+1],chosenfoods.iloc[0,idx])
        #    if isinstance(chosenfoods.iloc[0,idx],str):
        #        print(type(chosenfoods.iloc[0,idx]))
        #        a=a&(chosenfoods.iloc[:,idx].str.contains(fc,case=False))
        #    else:
        #        a=a&chosenfoods.iloc[:,idx]==float(f[idx+1])
        #the following initialization is necessary bc error in the apparetly(?) equivalent one commented out.optimization
        a=chosenfoods.iloc[:,0].str.contains('',case=False,regex=True)#np.empty(chosenfoods.shape[0])#pd.DataFrame(data=None, columns=una1.columns)#initialize empty accumulator of match results
        for idx,c in enumerate(una1[collist].columns):
            #print(chosenfoods.loc[:,c].astype('str').str.contains((str(getattr(f,c))),case=False).shape)
            #print(chosenfoods.iloc[:,0].str.contains('',case=False,regex=True).shape)
            #print(c," contains ",f[idx],'getattr=',getattr(f,c))
            a=a&(chosenfoods.loc[:,c].astype('str').str.contains((str(getattr(f,c))),case=False))
        #todo below: if certian nr columns are numberic, do =, if not, skip (doesnt work same as regex where '' matches all)
        #generalization todo:commented code above loops through columns and does comparison dependent on columnt type
        #& (chosenfoods.iloc[:,13]==f[14]) & (chosenfoods.iloc[:,14]==f[15])\
        # & (chosenfoods.iloc[:,16].str.contains(str(f[17]))) #& (chosenfoods.iloc[:,17]==f[18])\
          
        #print(a.value_counts()[True]," matches out of ",a.shape[0])
        hitn=a[a].shape[0]
        #print(f[0]," ",hitn," matches out of ",a.shape[0])
        if a.shape[0]-hitn<2:#indicia of regex problem, almost whole database selected
            print(hitn," matches out of ",a.shape[0]," ***for*** ",str(f));
        elif hitn>0:#todo: if there's overlap and a food gets zeroed twice, old value clobbered
            #todo, dont add columns to una, make another table...
            #OR just keep this, and split off the 2 new columns into another table and return the tuple.
            #una1.loc[f[0],'old_max_d']=chosenfoods.loc[a,'max_d'].values[0]#just grab the value of the first match,should be all the same
            chosenfoods.loc[a,'max_d']=0
            #una1.loc[f[0],'matches']=str(hitn)
            print(hitn," matches out of ",a.shape[0])#," for ",str(f.values));
         #b=b|a#do something with this?
     return(una1)#['matches']=str(a.value_counts()[True]))



# @app.route('/seeexclude')#
# def seeexclude():#regex strings
#     global una,chosenfoods,chosenfoods_cplex
#     #return (una.sort_index(ascending=False).to_html(table_id='una',escape=False))
#     #chosenfoods,chosenfoods_cplex,una=
#     get_chosen_foods()
#     return (flask.render_template('una.html',title='una',tables=[una.drop(columns="bitmap").to_html(index=True,escape=False,table_id='us')]))#drop bitmap july 3 2021

    # this file and constraints should be available to view without running a report like this ....
    #maybe these should be csv files - easy to preview, editable in excel
    #and also not encapsulated in a zip-like thing...but actual zip file are browsable ....
    #freecommander is back (treeviews) but does it do previews of html and csv ?
# from flask import request#2022-11-26

def loaddataset():#2022-03-14 called from every enndpoint (UScplex AND exclude())
    global una,chosenfoods,chosenfoods_cplex,npt,consdf
    trimflag=False
    if consdf is None:
    #try:
    #    consdf
    #except NameError:
        refreshconsdf()#2022-03-14
        trimflag=True
    if any(v is None for v in [chosenfoods,chosenfoods_cplex,una]):
    #try:
    #    chosenfoods,chosenfoods_cplex,una
    #except NameError:
        #chosenfoods,chosenfoods_cplex,una=
        get_chosen_foods()#
        trimflag=True
    if npt is None:#try:#todo test each variable 2022-05-20
    #    npt
        #print(npt.shape)#just looking for indication of cold start
    #except UnboundLocalError:#NameError:#really want to load up consdf each time, but not necessarily una
        npt=refreshnpt()#2022-02-19 this shoulbe be lazy-loaded#load all constraints (change the name please). made callable from UI.
        global nptfull
        nptfull=npt.copy()#2022-03-14 back #2022-03-06 moved to refreshnpt
        #cn=chosenfoods.rename(columns={'goto':'cost'},inplace=False)#.set_index('NDB_No')#june 15 2021 removed set_index
        #npt.update(chosenfoods[['cost']])#2022-10-05 moved to una calculate

        npt[['price']]=1.0 #2022-09-15 a default price level. could maybe just enter exceptionally high or low prices
        npt.update(chosenfoods[['price']])#should be displayed in foodlist to ease updating
        #print (npt.columns,consdf.index,consdf.index.difference(npt.columns))
        #consdf=pd.read_csv(vdwin+'consdf.csv',index_col=0)# july 23 - 
        #una=pd.read_csv(vdwin+'una.csv',index_col=0,parse_dates=True,dtype={'NDB_No':str});una.fillna(value='',inplace=True)#june 4 2021 removed
        st=pd.read_csv(get_vdwin()+'st.csv',index_col=0,keep_default_na=False)
        #2022-02-22 lines up to here were done in page load, but moved here to reload if they got booted prior to the ajax call

        #refreshnpt()#2022-02-22 removed
    if trimflag:
        trimdb()
    #end loaddataset
    if npt.isnull().values.any():
        is_NaN = npt.isnull()
        row_has_NaN = is_NaN.any(axis=1)
        rows_with_NaN = npt[row_has_NaN]
        #print("consdf columns after cleanup=",consdf.columns);
        print("npt rows ith nan=",rows_with_NaN)
        colsithnan=npt[npt.columns[npt.isna().any()]]#rows_with_NaN.isnull().any(axis=0)
        print('npt rwos, cols with nan=',colsithnan)

        assert ~npt.isnull().values.any()

# @app.route('/US2',methods=["POST"])
def US2():#Just ajaxify delta rows
    global nzf,unal,collist
    print("US2.")
    nzf=get_nzf()#cache.get("nzf")#2022-04-02
    nzfnew,unanew=UScplex()#US()
    try:
        #print(nzf['max_d'].head(), nzfnew['max_d'].head())
        nzf2=nzf['max_d'].head()
        nzfnew2=nzfnew['max_d'].head()
    except NameError:#for some reason US1 hasn't already been called, ie the this py file reloaded by flask, but browser jsstill loaded
        #2022-04-02 no. these have to be cached. this only ever gets called after exclude.
        #calling uscplex here wipes out wipes out the deltas in the output and input...
        # output and input must be cached (at least the deltas) 
        nzf,unal=UScplex()#US()
        print("us2 nameerror exception")
        #2022-02-22 todo-Dont call this again, just return all nonzero data.the browser has cached everything else
    v=nzfnew[(nzfnew['amounts'] != nzf['amounts'])\
    | (nzfnew['max_d'] != nzf['max_d'])\
    | (nzfnew['min_d'] != nzf['min_d'])\
    | (nzfnew['cost'] != nzf['cost'])\
    ]#cost was goto jun 15 2020

    #print("US2 v",v.columns,v[['amounts']])           
    nzf=nzfnew
    w=v.copy()
    #v['NDB_No']='#'+v['NDB_No']#todo(warning): should be 
    z=v.copy()#april 26 2021 avoid copy warning, replace v with z below
    #z.loc[:,'NDB_No']='#'+z['NDB_No']  #2020-01-21 21:48:46 dafuq dis for ??2020-01-22 08:34:20 datatables row selector
    z.index='#'+z.index#june 15 2021
  
    z['NDB_No']=z.index#june 15 2021
    w['NDB_No']=w.index#june 15 2021

    #collist=['FdGrp_Desc','Long_Desc','min_d','max_d','amounts','allmeas','cost']#june 15 2021 destroying the universality of collist right here...idgaf
    #return jsonify(ndbnos=json.loads(z[collist+['confid']].set_index('NDB_No').to_json(orient="split"))["index"],r=json.loads(w[collist+['confid']].to_json(orient="split"))["data"])
    return jsonify(ndbnos=json.loads(z[collist+['confid']].to_json(orient="split"))["index"],r=json.loads(w[collist+['confid']].to_json(orient="split"))["data"])

# @app.route('/exclude',methods=["POST"])#/<r0>/<r1>/<r2>/<r3>/<r4>/<r5>/<r6>/<hits>/<sinkarg>')#
def exclude():#r0,r1,r2,r3,r4,r5,r6,hits,sinkarg):#regex strings
    #april 28-variables are not secured within flask. therefore pickle immediately. memcaching or whatever will be
    # an optimization to be evaluated when i decide this goes online.
    global una,npt,chosenfoods,chosenfoods_cplex
    loaddataset()#todo this function was copied from uscplex, but uscplex need to call this, and this needs to be updated to check caches...
    r0=request.json['r0'];r1=request.json['r1'];r2=request.json['r2'];r3=request.json['r3']#args.get('r0');r1=request.args.get('r1');r2=request.args.get('r2');
    r4=request.json['r4'];r5=request.json['r5'];r6=request.json['r6'];r7=request.json['r7']#r3=request.args.get('r3');r4=request.args.get('r4');r5=request.args.get('r5');r6=request.args.get('r6');
    r8=request.json['r8']#2021-08-03 filter on confid
    hits=int(request.json['hits'])#int(request.args.get('hits'));
    collist1=['NDB_No','FdGrp_Desc','Long_Desc','min_d','max_d','amounts','allmeas','cost','confid']#2022-05-31 'cost' not 'goto
    #2022-01-06 make sure chosenfoods is the full database with all supplement placeholders here...todo
    a=\
    (chosenfoods.index.astype('str').str.contains((str(r0)),case=False))\
    & (chosenfoods.loc[:,collist1[1]].astype('str').str.contains((str(r1)),case=False))\
    & (chosenfoods.loc[:,collist1[2]].astype('str').str.contains((str(r2)),case=False))\
    & (chosenfoods.loc[:,collist1[3]].astype('str').str.contains((str(r3)),case=False))\
    & (chosenfoods.loc[:,collist1[4]].astype('str').str.contains((str(r4)),case=False))\
    & (chosenfoods.loc[:,collist1[5]].astype('str').str.contains((str(r5)),case=False))\
    & (chosenfoods.loc[:,collist1[6]].astype('str').str.contains((str(r6)),case=False))\
    & (chosenfoods.loc[:,collist1[7]].astype('str').str.contains((str(r7)),case=False))\
    & (chosenfoods.loc[:,collist1[8]].astype('str').str.contains((str(r8)),case=False))#2021-08-03 confid field
    #print(a.value_counts()[True]," matches out of ",a.shape[0])
    hitn=a[a].shape[0]
    if hitn!=hits:#2022-02-21  this will be differen
        rs="nothing is being changed.try regex again. python regex hits="+str(hitn)+" js hits is "+str(hits)
        print(rs)#print(chosenfoods_cplex[a])
        return(rs,400)#does the status code matter other than to the calling js ??
    #elif a.shape[0]-hitn<2:#indicia of regex problem, almost whole database selected#2020-02-25 09:40:45 because of mouse problems, this gets called with empty regex fields often enough
    #2022-03-17 temporary disable the regex failsafe ..
    if (False):#a.shape[0]-hitn<2:#indicia of regex problem, almost whole database selected#2020-02-25 09:40:45 because of mouse problems, this gets called with empty regex fields often enough
        rs=str(hitn)+" matches out of "+str(a.shape[0])+" ***for*** "+str(request.json)#str(f);#2020-02-26 11:26:58 todo f is not a printable thing, error messsage looks wierd
        print(rs)
        return(rs,400)
    elif hitn>0:#apply it
        #if r0 is empty, all rows matched, if r0 is a regex,will break. either input slice;
        #jan 12 2020 a blank dataframe with timestamp is created. addition columns are added dynamically
        #Also if called with all blank regex, then all matched and obvious user error, should filter here todo
        #because I dont have backtracking yet (i.e. rebuilding from una)?? but that is close, so leave this be for now.
        #nr=pd.DataFrame({'bitmap':chosenfoods[a].index.values.dumps()},index=[pd.Timestamp.now()])#2022-06-03 transition to index list.
        nr=pd.DataFrame({'bitmap':"placeholder"},index=[pd.Timestamp.now()])#2022-11-18
        nr.iloc[0,0]=chosenfoods[a].index.values.to_list()#2022-11-18
        #indexlist=pickle.loads(nr['bitmap'][0])#2022-06-04 test
        nr.loc[:,collist[0]]=str(r0)#todo for i in request.args   ??
        nr.loc[:,collist[1]]=str(r1);nr.loc[:,collist[2]]=str(r2)
        #nr.loc[:,collist[3]]=str(r3); nr.loc[:,collist[4]]=str(r4)#2022-06-09 min max and cost come from input fields, not table columns, and their json keys are as such
        nr.loc[:,collist[5]]=str(r5);nr.loc[:,collist[6]]=str(r6)
        #nr.loc[:,collist[7]]=str(r7)

        #nr=pd.DataFrame({'bitmap':a.values.dumps()},index=[pd.Timestamp.now()])#2022-06-04
        #nr.loc[pd.Timestamp.now(),'old_max_d']=chosenfoods_cplex.loc[a,'max_d'].values[0]#may 25 2021-important trick initializing blank nr    ;just grab the value of the first match,should be all the same
        if request.json['isint']!="":
            isint=bool(request.json['isint'])
            nr.loc[:,'isint']=isint#.astype(np.bool)
            print("isint.")
            #nr.loc[:,'bitmap']=a.values.dumps()#may 23 2021 see hacking jupyter notebook
        else:#Don't change anyhting about this existing state
            nr.loc[:,'isint']=np.NaN
            pass
        if request.json['maxfromgroup']!="":
            maxfromgroup=int(request.json['maxfromgroup']);
            minfromgroup=0#int(request.json['minfromgroup'])#june 4 2021 just zero for now
            print('maxfromgroup=',maxfromgroup)
            nr.loc[:,'maxfromgroup']=maxfromgroup;nr.loc[:,'minfromgroup']=minfromgroup
            #2022-02-15 todo for minfromgroup etc..
        else:
            nr.loc[:,'maxfromgroup']=np.NaN;nr.loc[:,'minfromgroup']=np.NaN
            #maxfromgroup=np.NaN#may 25 2021 this is unnecessary and useless. nr field is nan until it get assigned
            #its get nan if this column has not been created yet,(which at this stage, may not have been)
            pass
        #chosenfoods_cplex.loc[a,'max_d']=0.0 #removed june 16 2019..
        if request.json['sinkarg']!='':#try:#todo: '' is valid input that is ignored. invalid input (alpha) are genuine exceptions
            sink=float(request.json['sinkarg'])#args.get('sinkarg'));#todo:since no html input validation possible for scientific notation, do that here.
            if all(npt.loc[a,'cost']==sink):
                print("no npt changes, suspicious.",npt.loc[a,'cost'])
            else:
                print("npt changed.")
            if all(chosenfoods.loc[a,'cost']==sink):
                print("no chosenfoods changes, suspicious.")
            else:
                print("cf changed.")
            if all(chosenfoods_cplex.loc[a,'cost']==sink):
                print("no chosenfoods_cplex changes, suspicious.")
            else:
                print("cf_cplex changed.")
            #chosenfoods_cplex.loc[a,'cost']=sink#2022-06-02  #2022-03-07 this works even though a is bigger than _cplex, but a is series
            chosenfoods.loc[a,'cost']=sink#2022-02-23 for file save
            chosenfoods_cplex.loc[chosenfoods[a&cplexmask].index,'cost']=sink#2021 july 5
            npt.loc[chosenfoods[a&cplexmask].index,'cost']=sink#2021 july 5

            #npt.loc[chosenfoods_cplex[a]['NDB_No'],'gotoratio']=sink#added june 16 2019
            #npt.loc[chosenfoods_cplex[a]['NDB_No'],'cost']=sink#stupid name change june 16 2020
            
            #us-cplex.py:1759: UserWarning: Boolean Series key will be reindexed to match DataFrame index
            #2022-04-12 the following line should be removed, npt is not cached, this is done in UScplex...
            
            #the previous line is useless if only chosenfoods is cached ...
            # npt['cost']=chosenfoods_cplex['goto']
            # print('chosenfoods_cplex.loc=',chosenfoods_cplex.loc[a,'goto'])
            # print('chosenfoods.loc=',chosenfoods.loc[a,'goto'])
            # print('npt.loc a=',npt.loc[a,'cost'])
            #jan 25 2021 not saving npt anymore. but then npt must also have costs patched in like the ratiometric constraints..
            # ..and then any external costs management interface like spreadsheet will just write to the chosenfoods file.
            #
            #oct 23 2019 bug? this is only if any sink value was entered. this goes up into the condition above...
            nr.loc[:,'cost']=request.json['sinkarg']#sink#selecting 'all' rows because there is just one
            # print("request.json['sinkarg']=",request.json['sinkarg'])
            # print("nr.loc[:,'goto']",nr.loc[:,'goto_n'])
            #nr.loc[:,'bitmap']=a.values.dumps()#may 23 2021 see hacking jupyter notebook

        else:#except ValueError:
            sink=np.NaN
            nr.loc[:,'cost']=sink

            #print("sink is blank")#max is type",type(max)," of value=",max)
            pass
        if request.json['max']!='':
            max=float(request.json['max'])
            chosenfoods.loc[a,'max_d']=max
            chosenfoods_cplex.loc[chosenfoods[a&cplexmask].index,'max_d']=max#2021 july 5
            nr.loc[:,'max_d']=max
            print("max_d=",max)
            #nr.loc[:,'bitmap']=a.values.dumps()#may 23 2021 see hacking jupyter notebook

        else:#except ValueError:
            max=np.NaN
            nr.loc[:,'max_d']=max

            #print("max is blank")#max is type",type(max)," of value=",max)
            pass
        if request.json['min']!='':#try:
            min=float(request.json['min'])
            chosenfoods.loc[a,'min_d']=min
            chosenfoods_cplex.loc[chosenfoods[a&cplexmask].index,'min_d']=min#2021 july 5
            nr.loc[:,'min_d']=min
            print("min_d=",min)

            #nr.loc[:,'bitmap']=a.values.dumps()#may 23 2021 see hacking jupyter notebook

        else:#except ValueError:
            min=np.NaN
            nr.loc[:,'min_d']=min

            print("min is blank")#max is type",type(max)," of value=",max)
            pass


        #print(chosenfoods_cplex[a][['max_d']])
        nr.loc[:,'matches']=str(hits)#nr.loc[r0,'matches']=str(hits) edited july 4
        #nr.loc[:,'when']=pd.Timestamp.now()
        #nr.loc[:,'flip']='<button>flip</button>'#or 'see'+'delete' with global reload/re-run ??     
        
        #oh shit, I can regex by max_d, and set it...its a table interaction issue.
        #so you cant search by editable fields...the point of collist is the regexable subset ...
        #these are teh search criteria, the replace values are in new columns (not collist) of una
        #todo have to use the new columns when rebuilding from scratch using una

        #print("nr[['goto','min_d','max_d']]",nr[['goto','min_d','max_d']])
        #print("nr.dtypes=",nr.dtypes)
        #so to "edit", I would 'see' it, modify and save it, and delete the old, then reload food_des and re-run una
        #these are the basic operations over which convenience functions could layer (i.e. "edit")
        #for now, a column  is either searchable or writable, not both
        #the only maybe i can think of is to quickly locate pantry foods ...
        #una=una.append(nr,ignore_index=False,sort=False)
        
        una=nr.append(una,ignore_index=False,sort=False); 
        #print("una.dtypes=",una.dtypes)

        #print('una=',una[['goto','min_d','max_d']])
    # elif hitn>0:# == chosenfoods.shape[0]: removed 2020-02-25 10:27:28
    #     rs="must specify a subset (with a regex selector)-you have selected all."
    #     return(rs,400)#does the status code matter other than to the calling js ??
    #una.fillna(value='',inplace=True) #june 3 2021 removed. this is clobbering numerical columns
    # except ValueError:
    #     import sys;print("Invalid number format:", sys.exc_info())#[0])
    #     return ("exlude invalide number format:"+sys.exc_info(),500)#flask calls makeresponse()
   
    # except:#every other type
    #     import sys
    #     print("exclude Unexpected error:", sys.exc_info())#[0])
    #     return ("exlude Unexpected error:"+sys.exc_info(),500)#flask calls makeresponse()

    # return('exclusion added',204)#['matches']=str(a.value_counts()[True]))
    
    #return json.dumps({'success':True,'result':returnstatus}), 200, {'ContentType':'application/json'}#returnstatus is a message string I want to pass back to the user.
    get_chosen_foods(chosenfoods)#2022-04-07 also do get_una
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}


#sys.tracebacklimit = 1

# @app.route('/pickleuna/<fname>')#why wouldn't you pickle everything here?
# @app.route('/pickleuna')
def pickleexclude():#2020-04-22 13:36:39 saving to the vd+pname (version control)#fname='./una',pname='./person'):#todo use una unless get parameter specifies another filename
    global una,chosenfoods,chosenfoods_cplex
    import pickle
    #chosenfoods,chosenfoods_cplex,una=
    get_chosen_foods()

    #
    # 2020-01-24 10:23:17 No save the files separately. don't rely on language specific constructs too much
    # una will have serialize result both for compressed presentation, and faster rebuilding in memory
    #yes this does capture the concept of personalization, but not necessary yet.
    # consdf needs to import a spreadsheet and then do unit scaling etc...
    # data={'npt':npt,'chosenfoods':chosenfoods,'consdf':consdf,'una':una,'st':st} #june 16 2020 transition to csv format
    # with open(vdwin+pname,"wb") as f:
    #     pickle.dump(data,f)
    una.to_csv(get_vdwin()+'una.csv');chosenfoods.to_csv(get_vdwin()+'chosenfoods.csv')#june 4 2021 this is just a view file, doesn't get loaded
    #bc bitmap field type doesnt get reconstitued to "bytes" but to string, and no simple way to cast it.
    
    #npt.to_csv(get_vdwin()+'npt.csv') removed jan 19 2021 risk of corruption-ratiometric are spreadsheeted out

    una.to_pickle(get_vdwin()+'una')#usnutdata=pd.read_pickle('./nut_datausda')#2020-04-22 13:39:20 removded#june 4 2021 replaced
    #    chosenfoods.to_pickle('./chosenfoods')# 2020-04-22 13:39:31 removed

        #chosenfoods.to_pickle('./chosenfoods')#this is still debugging. just run exclude2 each time
    # except:
    #     import sys
    #     print("pickle exclude error:  ", sys.exc_info()[0])
    #     return('pickle exclude failture',400)
    # return ('excludes pickled.',204)
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}


    #constraints=consdf.reset_index().values#2022-02-19 deleting this wtf is it??
    # import json#an eye to doing this directly in javascript
    # with open('person.txt') as pfile:
    #     person=json.load(pfile)
    # except:
    #     import sys
    #     print("refresh error:  ", sys.exc_info()[0])
    #     return('refresh failur',400)
    # return ('pickles refreshed.',204)

#@app.route('/refreshnpt/<fname>')
#def refreshnpt(fname='./nptsinker'):#also pickles chosenfoods? 
PIECEWISE=True

def refreshconsdf():#2024-3-15
    global consdf,AMconsdf,PMconsdf,AMPM
    global consdf,AMconsdf,PMconsdf,AMPM
    with open(get_vdwin()+'consdf.xlsx', 'rb') as f:
        ox=pd.ExcelFile(f,engine='openpyxl')
        consdf=ox.parse(usecols='A:AA')

    consdf.set_index('id',inplace=True)
    consdf=consdf.drop(columns=['Min-IOM','notes','date last changed','body mass kg'])

    # from google.colab import auth
    # auth.authenticate_user()
    # import gspread
    # from google.auth import default
    # creds, _ = default()
    # gc = gspread.authorize(creds)
    
    # client = gc
    # sheet = client.open('consdf').sheet1
    # #values = sheet.get_all_values()#2D array

    # dtypes1 = [
    #     ('Min-IOM', 'O'),
    #     ('pref', 'float'),
    #     ('min', 'float'),
    #     ('max', 'float'),
    #     ('loslack-notnormed', 'float'),
    #     ('hislack-notnormed', 'float'),
    #     ('NutrDesc', 'str'),
    #     ('NutrDesc1', 'str'),
    #     ('loslack2', 'float'),
    #     ('hislack2', 'float'),
    #     ('notes', 'str'),
    #     ('date last changed', 'str'),
    #     ('body mass kg', 'float'),
    #     ('Ammin', 'str'),
    #     ('Ammax', 'str'),
    #     ('Amloslack-notnormed', 'float'),
    #     ('Amhislack-notnormed', 'float'),
    #     ('AMloslack2', 'str'),
    #     ('AMhislack2', 'str'),
    #     ('Pmmin', 'float'),
    #     ('Pmmax', 'float'),
    #     ('Pmloslack-notnormed', 'float'),
    #     ('Pmhislack-notnormed', 'float'),
    #     ('PMloslack2', 'float'),
    #     ('PMhislack2', 'float'),
    #     ('todelete', 'float')
    # ]


    # consdf=pd.DataFrame(sheet.get_all_records())
    # consdf.id=consdf.id.astype(str)
    # consdf.set_index('id', inplace=True)
 
    
    # # Drop unnecessary columns
    # consdf.drop(columns=['Min-IOM', 'notes', 'date last changed', 'body mass kg'], inplace=True)
    
    global PIECEWISE#2023-02-20 works ok with selected nutrient with tight boundaries
    if PIECEWISE:#2023-02-17 maybe just copy the table and overwrite min max and slacks ?
        # for index,row in consdf.iterrows():
        consdfpw=consdf.copy()
        pd.to_numeric(consdf['pref'])#2023-12-14 make sure all prefs are 0.0-1.0 or 2
        consdfpw=consdfpw[consdfpw['pref']<1.1]#pref column 0-1 range within iom, 2 disables inner slacks for that nutrient
        consdfpw['min']=consdfpw['min']+(consdfpw['max']-consdfpw['min'])*consdfpw['pref']*0.99
        consdfpw['max']=consdfpw['min']+(consdfpw['max']-consdfpw['min'])*consdfpw['pref']*1.01
        consdfpw.loslack2=consdfpw.loslack2*1e-1;consdfpw.hislack2=consdfpw.hislack2*1e-1#2024-3-28 was 1e-2, too small for price cost...
        consdfpw.index=consdfpw.index.astype(str)+'pw';        consdfpw.NutrDesc=consdfpw.NutrDesc.astype('str')+'pw'
    
        consdf = pd.concat([consdf, consdfpw], ignore_index=False, verify_integrity=True, sort=True)#2024-2-1
    
        #consdf=consdf.append(consdfpw,ignore_index=False,verify_integrity=True,sort=True)#april 25 2021 added sort=true to silence warning
    
    if RATIOMETRICS:
        #ratios_sheet = client.open('ratios').sheet1 #2024-6-23 just use this line instead if the google sheets way is better somehow
        #ratiosf=pd.DataFrame(ratios_sheet.get_all_records()).set_index('id')

        ratiosf=pd.read_excel(get_vdwin() +'ratios.xlsx',index_col=0,dtype={'numerator':str,'denominator':str})

       # Convert specific columns to string dtype
        #ratios_df['numerator'] = ratios_df['numerator'].astype(str)
        #ratios_df['denominator'] = ratios_df['denominator'].astype(str)
        for index, row in ratiosf.iterrows():#2022-03-13 preparing to split out
            #id	id	Min-IOM	min	max	loslack-notnormed	hislack-notnormed	min2	max2	loslack2-notnormed	hislack2-notnormed	loslack	hislack	id	NutrDesc	NutrDesc1	loslack2	hislack2	notes	date last changed	body mass kg
            newrow=pd.DataFrame(index=[index+'Lo',index+'Hi'],data={\
                'min':[0.001,0.001],'max':[0.01,0.01],\
                    #'min':[-0.01,0.001],'max':[-0.001,0.01],\#this was giving the dual infeasible error
                    'loslack-notnormed':[1.0e-0,0.0],'hislack-notnormed':[0.0,1.0e-0]})#april 26 , 2020 set these low to debug
            #I call it newrow, but its actually 2 rows
            #june 9 2021 trying directly creating new rows as above with npt
            # consdf[index+'Lo','loslack2']=newrow['loslack-notnormed']/newrow['min'];
            # consdf[index+'Lo','loslack2']=newrow['loslack-notnormed']/newrow['min'];#
            newrow['loslack2']=newrow['loslack-notnormed']/newrow['min'];assert newrow['min'].all()>0
            newrow['hislack2']=newrow['hislack-notnormed']/newrow['max'];assert newrow['max'].all()>0
            newrow['NutrDesc1']="<a href=http://localhost:5000/nutfocus?nutrno="+newrow.index+">"+newrow.index+"</a>"#I'm thinking there's no need for the textual description to be different than the id for it. There is a middle ground between brevity and comprehensiveness bigger than a sprinting track.
            #print("newrow.index=",newrow.index)
            consdf = pd.concat([consdf, newrow], ignore_index=False, verify_integrity=True, sort=True)#2024-2-1
    is_NaN = consdf.isnull()
    row_has_NaN = is_NaN.any(axis=1)
    rows_with_NaN = consdf[row_has_NaN]
    #print("consdf columns after cleanup=",consdf.columns);print("consdf rows ith nan=",rows_with_NaN)
    colsithnan=consdf[consdf.columns[consdf.isna().any()]]#rows_with_NaN.isnull().any(axis=0)
    #print('consdf rwos, cols with nan=',colsithnan)
    #2022-05-04 temporary delete follwing assertion...
    #assert ~consdf.isnull().values.any()#2021-12-19 spreadsheet dev by zero errors arent being detected!
    # print("consdf.shape",consdf.shape,"index=",consdf.index)
    #consdf.sort_index()#2024-3-15 whats this for
    # print("consdf.head=",consdf.head(),"consdf.tail=",consdf.tail())
    consdf.to_csv(get_vdwin()+"consdf.csv")
    #feb 28 2020 this seems to work once, then still need to reload the whole page.
    if AMPM:
        AMconsdf=consdf[consdf['todelete']==0].copy();#2021-12-17# print("AMconsdf.shape=",AMconsdf.shape);   
        AMconsdf.loc[:,'min']=consdf['Ammin'];AMconsdf.loc[:,'max']=consdf['Ammax']
        AMconsdf['loslack2']=consdf['AMloslack2'];AMconsdf['hislack2']=consdf['AMhislack2']
        PMconsdf=consdf[consdf['todelete']==0].copy()
        PMconsdf.loc[:,'min']=consdf['Pmmin'];PMconsdf.loc[:,'max']=consdf['Pmmax']
        PMconsdf['loslack2']=consdf['PMloslack2'];PMconsdf['hislack2']=consdf['PMhislack2']
        # print("AMconsdf min,max=",AMconsdf)#[['min','max']])
        is_NaN = AMconsdf.isnull()
        row_has_NaN = is_NaN.any(axis=1)
        rows_with_NaN = AMconsdf[row_has_NaN]
        # print("AMconsdf columns after cleanup=",AMconsdf.columns)
        # print("AMconsdf rows ith nan=",rows_with_NaN)
        colsithnan=AMconsdf[AMconsdf.columns[AMconsdf.isna().any()]]#rows_with_NaN.isnull().any(axis=0)
        #print('AMconsdf rwos, cols with nan=',colsithnan)
        assert ~AMconsdf.isnull().values.any()#2021-12-19 spreadsheet dev by zero errors arent being detected!


def US1():#initialize with a full html table
    global nzf2,unal, vdwin,npt,chosenfoods,consdf,una,st,ratiosf
    vdwin = get_vdwin()#request.args.get('vd'); print ('vdin='+vdwin)
    #cache.add('vdwin',vdwin)
    # US()#2022-01-12 output to file only, for comparison
    # nzf,unal=UScplex()#US()
    #USgpkit()#2022-04-20...2022-04-23 taking this over to google colab, needs more thinking
    nzf2,unal=UScplex()#2022-01-19 the previous 2 lines are more recent, I'm just having a quick look at serine etc.
    #print('nzf=',nzf)
    #watch(nzf)
    nzf2.style.set_table_attributes('table-layout="auto"')
    nzfs=nzf2.sort_values('amounts',inplace=False,ascending=False)
    nzfs.update(chosenfoods_cplex[['Long_Desc']])#2022-03-21 adds " CPLEX" to fooddesc

    #nzf[collist].to_html(vdwin+'foodlist.html',index=True,classes='',table_id='foodlist')
    #return (flask.render_template('view3.html',tables=[nzf[collist].to_html(index=False,escape=False,table_id='us'),unal.to_html(escape=False,table_id='una')]))
    
    # #jan 22 2021
    # #collist.append('confid')
    # confid=pd.read_pickle(vdwin+'confid.csv')#Dataframe hacking jupyter notebook is where I built this
    # nzfs=nzfs.merge(confid,left_on="NDB_No",right_index=True)
    #jan 22 2021 added fixed header class below
    collist=['FdGrp_Desc','Long_Desc','min_d','max_d','amounts','allmeas','cost']#G2020-06-06 keeping it more simple for now#june 15 2021 removing ndbno as a column
    AMcollist=['FdGrp_Desc','Long_Desc','min_d','max_d','AMamounts','allmeas','cost']
    PMcollist=['FdGrp_Desc','Long_Desc','min_d','max_d','PMamounts','allmeas','cost']
    #global AMnzfz,PMnzfz
    #n=solution2()#2022-02-24
    return nzfs #2022-10-14
    return (flask.render_template('view3.html',title='main',tables=[nzfs[collist+['confid']].to_html(index=True,escape=False,table_id='us')]))#2020-02-04 10:13:14 messing up scroll bar because this list becomes very large
    #june 15 2021 to html index True

#type(measf.loc['11969']['Gm_Wgt'])
#pd.set_eng_float_format(accuracy=1);
pd.options.display.float_format='{:.2f}'.format
#print('{:40,.3f}'.format(1233333444445676.0123456789))
#help('FORMATTING')