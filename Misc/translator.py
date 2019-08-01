"""
generates spreadsheet from properties files or vice versa
this is useful for translators to see translation strings next to each other
Example usage:

# generate a CSV file containing both Chinese and English string (side-by-side)
python translator.py messages_zh_CN.properties sidebyside.csv

# convert generated CSV file back to properties file
python translator sidebyside.csv messages_zh_CN.properties
"""

import csv
from collections import OrderedDict
import io
import argparse
import sys

def parseargs():
    parser = argparse.ArgumentParser()
    parser.add_argument('path1')
    parser.add_argument('path2')
    return parser.parse_args()

#read properties file into OrderedDict
def properties2dict(path):
    d = OrderedDict()
    with io.open(path, 'r', encoding='utf-8') as langfile:
        for line in langfile:
            if line.lstrip().startswith('#'):
                continue
            #sanitize bom
            line = line.replace(u'\ufeff', u'')

            vals = line.split('=', 1)
            if len(vals) == 2:
                d[vals[0].strip()] = vals[1].strip()
    return d

#write OrderedDict back to properties file
def dict2properties(d, path):
    with io.open(path, 'wb', encoding='utf-8', newline='\n') as dest:
        #write BOM
        #file_new.write('\ufeff')
        for (k, v) in d.iteritems():
            line = '{}={}\n'.format(k,v)
            dest.write(line)

#merge language strings from two properties files, with preference to the English file
def properties2csv(langpath, destcsv):
    engdict = properties2dict('messages.properties')
    otherlangdict = properties2dict(langpath)
    merged = OrderedDict()
    for (engk, engv) in engdict.iteritems():
        otherv = otherlangdict.get(engk, u'NEEDS TRANSLATION')
        merged[engk] = [engv, otherv]

    with open(destcsv, 'wb') as csvfile:
        csvout = csv.writer(csvfile)
        for (k,v) in merged.iteritems():
            row = map(lambda x:x.encode('utf-8'), [k, v[0], v[1]])
            csvout.writerow(row)

#convert CSV file previously created with this script back to messages file
def csv2properties(srccsv, langpath):
    #use 3 third column for foreign language strings
    with open(srccsv, 'rb') as csvfile:
        with io.open(langpath, 'w', encoding='utf-8', newline='\n') as destfile:
            reader = csv.reader(csvfile)
            for row in reader:
                line = u'{}={}\n'.format(row[0].decode('utf-8'),row[2].decode('utf-8'))
                destfile.write(line)

if __name__ == '__main__':
    args = parseargs()
    if(args.path1.endswith('.properties')):
        properties2csv(args.path1, args.path2)
    elif(args.path1.endswith('.csv')):
        csv2properties(args.path1, args.path2)
    else:
        print 'Unknown file input type'
        sys.exit(-1)
    
