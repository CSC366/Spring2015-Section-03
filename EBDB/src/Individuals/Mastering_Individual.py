import MySQLdb as mdb
from difflib import SequenceMatcher as SM
import re
import operator
import json
import time
import datetime

def get_config():

    f = open('./client.conf','r')
    conf = f.read()
    f.close()

    conf = json.loads(conf)
    return conf

def fuzzy_match(orig, comp):
    seq = SM(None, orig, comp)
    score = seq.ratio() * 100
    return score

def compare_1point(row, comp):
    score = 0
    r_type = row[1]
    r_name = row[2]
    r_dob = row[3]
    r_isop = row[4]
    r_gender = row[5]
    r_spec = row[6]
    r_spec2 = row[7]
    
    c_type = comp[1]
    c_name = comp[2]
    c_dob = comp[3]
    c_isop = comp[4]
    c_gender = comp[5]
    c_spec = comp[6]
    c_spec2 = comp[7]

    threshold = 70
    if (r_gender != None and c_gender != None) and fuzzy_match(r_gender, c_gender) >= threshold:
    		score += CONFIG['gender']
    if (r_spec != None and c_spec != None) and fuzzy_match(r_spec, c_spec) >= threshold:
    		score += CONFIG['spec1']
    if (r_spec2 != None and c_spec2 != None) and fuzzy_match(r_spec2, c_spec2) >= threshold:
    		score += CONFIG['spec2']
   
    return score
    
    
def checkAddress(r_street,r_city, r_country, r_county, r_postcode, r_unit, r_region, c_street, c_city, c_county, c_country, c_postcode, c_unit, c_region, streetscore, cityscore, countryscore, countyscore, postcodescore, unitscore, regionscore):
    score = 0
    
    if r_street != None and c_street != None and r_street == c_street:
      	#score += CONFIG['street']
        score += streetscore
    
    if r_city != None and c_city != None and r_city == c_city:
    	#score += CONFIG['city']
        score += cityscore
        
    if r_country != None and c_country != None and r_country == c_country:
    	#score += CONFIG['country']
        score += countryscore
        
    if r_county != None and c_county != None and r_county == c_county:
    	#score += CONFIG['county']
        score += countyscore
        
    if r_postcode != None and c_postcode != None and r_postcode == c_postcode:
    	#score += CONFIG['postcode']
        score += postcodescore
        
    if r_unit != None and c_unit != None and r_unit == c_unit:
    	#score += CONFIG['unit']
        score += unitscore
        
    if r_region != None and c_region != None and r_region == c_region:
    	#score += CONFIG['region']
        score += regionscore
    
    return score
    
def parseName(n):
    prefixes = ['Mr', 'Ms', 'Mrs', "Dr", 'Mr.', 'Ms.', 'Mrs.', 'Dr.', 'DR', 'DR.']
    titles = ['LMT', 'MD', 'M.D.', 'FNP', 'OD', 'MRCP', 'DO', 'MED', 'LPC', 'DDS', 'LCSW-C', 'PHD', 'PA-C', 'NP', 'MA', 'APNP', 'FNP-C', 'DRPH']
    suffixes = ['JR', 'SR', 'JR.', 'SR.', 'Jr', 'Sr', 'I', 'II', 'III', 'IV', 'V']
    nameList = n.split(' ')
    
    prefixes = ''
    credential = ''
    first = ''
    middle = ''
    last = ''
    suffix = ''
    extra = ''
    
    for name in nameList:
        for p in prefixes:
            if name == p:
                prefixes = name
                nameList.remove(prefixes)
                
        for t in titles:
            if name == t:
                nameList.remove(name)
                credential = name if len(credential) == 0 else ' ' + name
                
        for s in suffixes:
                
            if name == s:
                nameList.remove(s)
                suffix = name
                
        if name == '-' and nameList.index(name) != 0 and len(nameList) > nameList.index(name):
            index = nameList.index(name)
            nameList[index - 1] = nameList[index - 1] + '-' + nameList[index + 1]
            nameList.pop(index) # pops -
            nameList.pop(index) # pops second half of last name
    
    first = nameList[0] if len(nameList) > 0 else ''
    last = nameList[1] if len(nameList) > 1 else ''
    if len(nameList) > 2:
        middle = last
        last = nameList[2] if len(nameList) > 2 else ''
    extra = nameList[3] if len(nameList) > 3 else ''
    
    #if len(nameList) > 4:
    #    print 'long name found: ' + ' '.join(nameList)
    
    return prefixes, credential, first, middle, last, suffix, extra
    
    
def pickBest(matchList):
    points = {}
    master = []
    if len(matchList) > 0:
        for person in matchList:
        #    print person
            pts = 0
            for attributes in person:
                if attributes != None:
                    pts +=1
            points[person] = pts
        
        sortedPoints = sorted(points, key=points.get, reverse=True)
        
        #for p in sortedPoints:
        #    print points[p], person
        
        #master = sortedPoints[0]
        
        #i = 0
        
        master.append(sortedPoints[0][1])
        
        #Supposed to audit chossing the best baseline for the master, but servers are down
        #aMasterFile.write(master[?] + 'Set as baseline')
        
        prefix = ''
        credential = ''
        first = ''
        middle = ''
        last = ''
        suffix = ''
        extra = ''
        
        
        for sp in sortedPoints:
            name_tup = parseName(sp[2])
            prefix = name_tup[0] if prefix == '' else prefix
            credential = name_tup[1] if credential == '' else credential
            first = name_tup[2] if first == '' else first
            middle = name_tup[3] if (middle == '' or (len(middle) == 1 and len(name_tup[3]) > 1)) else middle
            last = name_tup[4] if last == '' else last
            suffix = name_tup[5] if suffix == '' else suffix
            extra = name_tup[6] if extra == '' else extra
            
        master.append(prefix)
        master.append(first)
        master.append(middle)
        master.append(last)
        master.append(suffix)
        master.append(credential)
        

        for i in range(3,22):
            flag = 0
            index = 0
            
            for sp in sortedPoints:
                if sp[i] != None:
                    master.append(sp[i])
                    #print "ADDED ATTRIBUTE TO MASTER", index, "sp[", i, "]=",sp[i]
                    flag = 1
                    break 
                index += 1
            
            if flag == 0:
                master.append('')
            
        soleProprietor = 'X'
        #loop through matchlist to check if there is at least one person with isSoleProprietor = Y
        #if there is set master isSoleProprietor to true 
        #if there isSoleProprietor = N, set to N
        #if neither for all persons in matchList set to X
        for person in matchList:
            curProprietor = person[5]
            if curProprietor == 'Y':
                soleProprietor = 'Y'
                break;
            elif curProprietor == 'N':
                soleProprietor = 'N'
            
        master[5] = soleProprietor

        #print "***PRINTING ***"
        #print "Master: ", master
        #for sp in sortedPoints:
        #    print "Candidate[",points[sp],"]: ", sp  
            
    return master 



def compare(row, comp, name, name8, isop, gender, spec1, spec2, phone, streetscore, cityscore, countryscore, countyscore, postcodescore, unitscore, regionscore, matchthresh):
    score = 0

    #Match Auditig
    a_name = 0
    a_isop = 0
    a_gender = 0
    a_spec = 0
    a_spec2 = 0
    a_phone = 0
    a_addr1 = 0
    a_addr2 = 0
    
    
    r_type = row[1]
    r_name = row[2]
    r_dob = row[3]
    r_isop = row[4]
    r_gender = row[5]
    r_spec = row[6]
    r_spec2 = row[7]
    r_phone = row[8]
    
    c_type = comp[1]
    c_name = comp[2]
    c_dob = comp[3]
    c_isop = comp[4]
    c_gender = comp[5]
    c_spec = comp[6]
    c_spec2 = comp[7]
    c_phone = comp[8]

    if r_type != None and c_type != None and r_type != c_type:
        return False, -1
    
    edit_distance = SM(None, c_name.lower(), r_name.lower()).ratio()
    if c_name != None and r_name != None:
        if edit_distance == 1:
            a_name = name
            #a_name = CONFIG['name']
            #score += CONFIG['name']
            score += name
        elif edit_distance >= .8:
            #score += CONFIG['name8']
            score += name8
        elif edit_distance <= .5:
            #score += -CONFIG['name']
            score += -name
            return False, -1
    
    if r_isop != None and c_isop != None:
        if  r_isop == c_isop:
            #a_isop = CONFIG['isop']
            #score += CONFIG['isop']
            a_isop = isop
            score += isop
        else:
            #score += -CONFIG['isop']
            score += -isop
      
    if r_gender != None and c_gender != None:
        if r_gender == c_gender:
            #a_gender = CONFIG['gender']
            #score += CONFIG['gender']
            a_gender = gender
            score += gender
        else:
            #score += -CONFIG['gender']
            score += -gender
      
    if r_spec != None and c_spec != None:
        if r_spec == c_spec:
            #a_spec = CONFIG['spec1']
            #score += CONFIG['spec1']
            a_spec = spec1
            score += spec1
        else:
            #score += -CONFIG['spec1']
            score += -spec1
            
    if r_spec2 != None and c_spec2 != None:
        if r_spec2 == c_spec2:
            #a_spec2 = CONFIG['spec2']
            #score += CONFIG['spec2']
            a_spec2 = spec2
            score += spec2
        else:
            #score += -CONFIG['spec2']
            score += -spec2
            
    if r_phone != None and c_phone != None:
        c_phoneClean = re.sub("[^0-9]", "", c_phone)
        r_phoneClean = re.sub("[^0-9]", "", r_phone)
        
        
        if r_phoneClean == c_phoneClean:
            #a_phone = CONFIG['phone']
            #score += CONFIG['phone']
            a_phone = phone
            score += phone
        else:
            """
            score += -1
            """
      
    a_addr1 = checkAddress(row[9], row[10], row[11], row[12], row[13], row[14], row[15], comp[9], comp[10], comp[11], comp[12], comp[13], comp[14], comp[15], streetscore, cityscore, countryscore, countyscore, postcodescore, unitscore, regionscore)
    a_addr2 = checkAddress(row[16], row[17], row[18], row[19], row[20], row[21], row[22], comp[16], comp[17], comp[18], comp[19], comp[20], comp[21], comp[22], streetscore, cityscore, countryscore, countyscore, postcodescore, unitscore, regionscore)
    score += a_addr1
    score += a_addr2
    
    
    if score > matchthresh:
        audit_insert = []
        if a_name != 0:
            aMatchFile.write(str(row[0]) + '\t' + str(comp[0]) + '\t Name match: ' + str(a_name) + '\n')
            audit_insert.append('INSERT INTO Audit (SourceID, ComparisonID, Comment) Values (%s, %s, \'%s\')' % (str(row[0]), str(comp[0]),  'Name match: '  + str(a_name)))
        if a_isop != 0:
            aMatchFile.write(str(row[0]) + '\t' + str(comp[0]) + '\t ISOP match: ' + str(a_isop) + '\n')
            audit_insert.append('INSERT INTO Audit (SourceID, ComparisonID, Comment) Values (%s, %s, \'%s\')' % (str(row[0]), str(comp[0]),  'ISOP match: '  + str(a_isop)))
        if a_gender != 0:
            aMatchFile.write(str(row[0]) + '\t' + str(comp[0]) + '\t Gender match: ' + str(a_gender) + '\n')
            audit_insert.append('INSERT INTO Audit (SourceID, ComparisonID, Comment) Values (%s, %s, \'%s\')' % (str(row[0]), str(comp[0]),  'Gender match: '  + str(a_gender)))
        if a_spec != 0:
            aMatchFile.write(str(row[0]) + '\t' + str(comp[0]) + '\t Prime Spec match: ' + str(a_spec) + '\n')
            audit_insert.append('INSERT INTO Audit (SourceID, ComparisonID, Comment) Values (%s, %s, \'%s\')' % (str(row[0]), str(comp[0]),  'Prime Spec match: '  + str(a_spec)))
        if a_spec2 != 0:
            aMatchFile.write(str(row[0]) + '\t' + str(comp[0]) + '\t Second Spec match: ' + str(a_spec2) + '\n')
            audit_insert.append('INSERT INTO Audit (SourceID, ComparisonID, Comment) Values (%s, %s, \'%s\')' % (str(row[0]), str(comp[0]),  'Second Spec match: '  + str(a_spec2)))
        if a_phone != 0:
            aMatchFile.write(str(row[0]) + '\t' + str(comp[0]) + '\t Phone match: ' + str(a_phone) + '\n')
            audit_insert.append('INSERT INTO Audit (SourceID, ComparisonID, Comment) Values (%s, %s, \'%s\')' % (str(row[0]), str(comp[0]),  'Phone match: '  + str(a_phone)))
        if a_addr1 != 0:
            aMatchFile.write(str(row[0]) + '\t' + str(comp[0]) + '\t M Addr match: ' + str(a_addr1) + '\n')
            audit_insert.append('INSERT INTO Audit (SourceID, ComparisonID, Comment) Values (%s, %s, \'%s\')' % (str(row[0]), str(comp[0]),  'M Addr match: '  + str(a_addr1)))
        if a_addr2 != 0:
            aMatchFile.write(str(row[0]) + '\t' + str(comp[0]) + '\t P Addr match: ' + str(a_addr2) + '\n')
            audit_insert.append('INSERT INTO Audit (SourceID, ComparisonID, Comment) Values (%s, %s, \'%s\')' % (str(row[0]), str(comp[0]),  'P Addr match: '  + str(a_addr2)))
            
        con = mdb.connect(host='localhost',user='Alec',passwd='cAkp3f7fg/',db='cpe366')

        with con:
            cur = con.cursor()
            for i in range(0, len(audit_insert)):
               cur.execute(audit_insert[i]) 
            
            
        return True, score
    else:
        return False, score
        
def nameTest():
    con = mdb.connect(host='localhost',user='Alec',passwd='cAkp3f7fg/',db='cpe366')

    with con:

        cur = con.cursor()
      
        cur.execute('''SELECT Name
                       FROM SourceProviders as SP 
                    ''')
        rows = cur.fetchall()
        
        LIMIT = 20
        for i in range(0, LIMIT):
            print 'name: ' + rows[i][0]
            prefixes, credential, first, middle, last, suffix, extra = parseName(rows[i][0])
            print 'credential: ' + credential + '  prefixes: ' + prefixes + '  first: ' + first + '  middle: ' + middle + '  last: ' + last + '  suffix: ' + suffix + '  extra: ' + extra + '\n'
          
          

          
def create_insert(master_record):
    firstName = '\'' + master_record[2] + '\''
    lastName = '\'' + master_record[4] + '\''
    middleName = '\'' + master_record[3] + '\''
    credential = '\'' + master_record[6] + '\''
    prefix = '\'' + master_record[1] + '\''
    suffix = '\'' + master_record[5] + '\''
    type = '\'' + master_record[0] + '\''
    dob = '\'' + master_record[8] + '\''
    soleProp = '\'' + master_record[9] + '\''
    gender = '\'' + master_record[7] + '\''
    
    
    if firstName == "\'\'":
        firstName = "NULL"
    if middleName == "\'\'":
        middleName = "NULL"
    if lastName == "\'\'":
        lastName = "NULL"
    if credential == "\'\'":
        credential = "NULL"
    if prefix == "\'\'":
        suffix = "NULL"
    if type == "\'\'":
        type = "NULL"
    if dob == "\'\'":
        dob = "NULL"
    if soleProp == "\'\'":
        soleProp = "NULL"
    if gender == "\'\'":
        gender = "NULL"
    
    insert_statement = 'INSERT INTO MasterProviders (FirstName, LastName, MiddleName, Credential, Prefix, Suffix, Type, DoB, IsSoleProprietor, Gender) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);' % (firstName, lastName, middleName, credential, suffix, prefix, type, dob, soleProp, gender)
    return insert_statement
    
def match():
    con = mdb.connect(host='localhost',user='Alec',passwd='cAkp3f7fg/',db='cpe366')

    name = CONFIG['name']
    name8 = CONFIG['name8']
    isop = CONFIG['isop']
    gender = CONFIG['gender']
    spec1 = CONFIG['spec1']
    spec2 = CONFIG['spec2']
    phone = CONFIG['phone']
    streetscore = CONFIG['street']
    cityscore = CONFIG['city']
    countryscore = CONFIG['country']
    countyscore = CONFIG['county']
    postcodescore = CONFIG['postcode']
    unitscore = CONFIG['unit']
    regionscore = CONFIG['region']
    matchthresh = CONFIG['match']
    
    with con:
        
        cur = con.cursor()
 
        #old select statement where Addresses and Phonenumber has null values
        #cur.execute('''SELECT SP.*, PN.PhoneNumber,
        #               A1.Street, A1.City, A1.Country, A1.County, A1.PostCode, A1.Unit, A1.Region, 
        #               A2.Street, A2.City, A2.Country, A2.County, A2.PostCode, A2.Unit, A2.Region
        #               FROM SourceProviders as SP, PhoneNumbers as PN, Addresses as A1, Addresses as A2 
        #               WHERE SP.ID = PN.SourceID AND A1.SourceID = SP.ID AND A2.SourceID = SP.ID AND A1.Type = 'm' AND A2.type = 'p'
        #            ''')
        cur.execute('''
                    SELECT SP.*, PN.PhoneNumber,
                           A1.Street, A1.City, A1.Country, A1.County, A1.PostCode, A1.Unit, A1.Region,
                           A2.Street, A2.City, A2.Country, A2.County, A2.PostCode, A2.Unit, A2.Region
                           FROM SourceProviders as SP
                           LEFT JOIN PhoneNumbers PN ON SP.ID = PN.SourceID
                           LEFT JOIN (SELECT * FROM Addresses WHERE Type = "m") A1 ON A1.SourceID = SP.ID
                           LEFT JOIN (SELECT * FROM Addresses WHERE Type = "p") A2 ON A2.SourceID = SP.ID
                           WHERE SP.Type = 'Individual';
                    ''')

        
		
        rows = cur.fetchall()
        tmp = []
        master = []
        match = {}
        match_id = 0
        phonePattern = re.compile(r'(\d{3})\D*(\d{3})\D*(\d{4})\D*(\d*)$')
        
        TOTAL = len(rows)

        for i in range(0, TOTAL):
            tmp.append(rows[i])

        print "Entries evaluated: " + str(len(tmp))

        count = 0
        match_count = 0
        i = 0
        while i < len(tmp):
            row = tmp[i]
            row_id = row[0]

            if row_id not in match:
               master.append([row])
               match[row_id] = match_id
               match_id += 1

            j = i + 1
            if i % 100 == 0:
                print i

            while j < len(tmp):
                count += 1
                comp = tmp[j]
                comp_id = comp[0]

                result, score = compare(row, comp, name, name8, isop, gender, spec1, spec2, phone, streetscore, cityscore, countryscore, countyscore, postcodescore, unitscore, regionscore, matchthresh)
                if result:
                    match_count += 1

                    if comp_id in match:
                        index = match[comp_id]
                        copy = master[index]
                        master[index] = []
                        index = match[row_id]
                        master[index] += copy
                    else:
                        index = match[row_id]
                        match[comp_id] = index
                        print index
                        master[index].append(comp)
                    tmp.remove(comp)
                    print '----- MATCH ' + str(score) + ' -----'
                    print row
                    print comp


                j += 1
            print "length of temp: " + str(len(tmp))
            i += 1


        print 'comparisons: ' + str(count)
        print 'matches: ' + str(match_count)
        
        
        mfile = open('Masters_' + time + '.txt', 'w')
        mfile.write('ID\tType\tName Prefix\tFirst Name\tMiddle Name\tLast Name\tName Suffix\tCredentials\tGender\tDoB\tSole Prop.\tPhone\tPrimary Specialty\tSecondarySpecialty\n') 
        
        cfile = open('Crosswalk_' + time + '.txt', 'w')
        cfile.write('MasterId\tSourceId\n')
        for i in range(0,len(master)):
            r = master[i]
            r_len = len(r)
           
            master_record = pickBest(r)
            if len(master_record) > 0:
                phone = master_record[12]
                
                if phone != None and phone != '':
                    c_phone = re.sub("\D", "", phone)
                    match = phonePattern.search(c_phone)
                    if match:
                        phone = '(' + match.group(1) + ')-' + match.group(2) + '-' + match.group(3)
                
                insert_statement = create_insert(master_record) 
                cur.execute(insert_statement)
                #cur.execute('INSERT INTO MasterProviders (Name, Type, Dob, IsSoleProprietor, Gender) VALUES(%s,%s,%s,%s,%s)', (master_record[1] + ' ' + master_record[2] + ' ' + master_record[3] + ' ' + master_record[4] + ' ' + master_record[5] + ' ' + master_record[6] , master_record[0], master_record[7], master_record[8], master_record[9]))
                mfile.write(str(i) + '\t' + master_record[0] + '\t' + master_record[1] + '\t' + master_record[2] + '\t' + master_record[3] + '\t' + master_record[4] + '\t' + master_record[5] + '\t' + master_record[6] + '\t' + master_record[7] + '\t' + master_record[8] + '\t' + master_record[9] + '\t' + phone + '\t' + str(master_record[10]) + '\t' + str(master_record[11]) + '\n')
                #mfile.write(str(i) + '\t0' + master_record[0] + '\t1' + master_record[1] + '\t2' + master_record[2] + '\t3' + master_record[3] + '\t4' + master_record[4] + '\t5' + master_record[5] + '\t6' + master_record[6] + '\t7' + master_record[7] + '\t8' + master_record[8] + '\t9' + master_record[9] + '\t12' + str(master_record[12]) + '\t10' + str(master_record[10]) + '\t11' + str(master_record[11]) + '\n')
                for j in range(0, r_len):
                    cfile.write(str(i) + '\t' + str(r[j][0]) + '\n')
                    cur.execute('INSERT INTO Crosswalk(MasterId, SourceId) VALUES(%s, %s)', ((i + 1), str(r[j][0])))


       
       #     type = master_record[0]
       #     name = master_record[1] + master_record[2] + master_record[3] + master_record[4] + master_record[5] + master_record[6] 
       #     dob = master_record[7]
       #     isop = master_record[8]
       #     gender = master_record[9]             
       #     spec1 = master_record[10]
       #     spec2 = master_record[11]
       #     phone = master_record[12]

        
        mfile.close()
        cfile.close()
            
       
                
      

    con.close()

if __name__ == '__main__':
	
    # Reset Mastered tables
    #con = mdb.connect(host='csc-db0.csc.calpoly.edu',user='ecobb',passwd='ebdb',db='ecobb')
    #cursor = con.cursor()
    #sql = open("DB-cleanup-master.sql").read()
    #cursor.execute(sql)
    #con.close()

    # Create groupstamp
    time = datetime.datetime.fromtimestamp(time.time()).strftime('%H_%M_%S')

    #Create Audit file for matches
    aMatchFile = open('Audits_' + time + '.txt', 'w')
    aMatchFile.write('Provider\tComparison\tInfo\n') 

    #Create README_EXTRACT
    rFile = open('REAME_EXTRACT_' + time + '.txt','w')
    rFile.write('The audits are found in Audits_<groupstamp>.txt\n')
    rFile.write('The Format is: <SourceId of current provider> <tab> <Id of provider being compared if this is a comparison> <tab> <Info>\n')
    rFile.write('For comparisons, Info states why each match was awarded points for pairs of providers that were combined') 
    rFile.close()
    
    CONFIG = get_config()
    match()

    aMatchFile.close()
