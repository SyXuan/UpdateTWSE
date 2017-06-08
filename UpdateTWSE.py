import os
import csv
import requests
import pickle
import pandas as pd
from datetime import date, timedelta, datetime
from time import time, gmtime, strftime, strptime, localtime

cleanData = False
getRange = False

if cleanData:
    print '\nCleanData: True, will clean stock data and download.'
else:
    print '\nCleanData: False, will update existed data.'
if getRange == True:
    startDate = date.today() - timedelta(180)
    print 'GetRange: True, get from startDate.\n\n'
else:
    startDate = date(1992, 1, 1)
    print 'GetRange: False, get from 1992/01/01.\n\n'

errorList = []


def main():
    # Setup directory
    if not os.path.isdir('save'):
        print 'save directory not exists, create directory.'
        os.mkdir('save')

    print 'Start downloading TWSE data.'
    stock_no = []
    with open('stock_no.csv', 'r') as f:
        reader = csv.reader(f)
        stock_no = list(reader)
    # stockList = []

    print 'Stock numbers:', len(stock_no)
    startDateTW = str(startDate.year - 1911) + '/' + \
        startDate.strftime('%m/%d')
    print 'Start to get from', startDateTW

    #UpdateOneStock('1598', startDate.strftime('%Y%m%d'))

    for i in range(0, len(stock_no)):
        # print stock_no[i][0]
        print '\n%d/%d' % (i + 1, len(stock_no))
        UpdateOneStock(stock_no[i][0], startDate.strftime('%Y%m%d'))

    myfile = open('error_list.csv', 'wb')
    wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
    wr.writerow(errorList)
    myfile.close()
    print 'Save error list to error_list.csv'
    print '\nFinish update stock data'

    '''
    print '\n\nFinish getting data\n\n'
    print 'Data error', dataError
    print 'CSV error', csvError
    errorList = dataError + csvError
    myfile = open('error_list.csv', 'wb')
    wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
    wr.writerow(errorList)
    myfile.close()
    print 'Save error list to error_list.csv'
    '''


def UpdateOneStock(stockNum, start):
    '''
    csvFile = os.path.join('data', '%s.csv' % stockNum)
    if os.path.exists(csvFile):
        print csvFile, 'exists, start update'
    '''
    pickleFile = os.path.join('save', '%s.pickle' % stockNum)
    if os.path.exists(pickleFile) and cleanData == False:
        try:
            pickle_in = open(pickleFile, 'rb')
            df = pickle.load(pickle_in)
            pickle_in.close()
        except Exception:
            global errorList
            errorList.append(stockNum)
            print 'Read pickle error'
            print 'Error list:', errorList
            return None
        # Get last day
        lastDay = df['date'][len(df) - 1]
        print '%s.pickle existed. Updating from %s' % (stockNum, lastDay)
        yyyy, mm, dd = lastDay.split('/')
        startTmp = datetime.strptime('%04d%02d%02d' % (
            (int(yyyy) + 1911), int(mm), int(dd)), '%Y%m%d')
        monthCount = diff_month(date.today(), startTmp)
        getYear = startTmp.year
        getMonth = startTmp.month

    else:
        startTmp = strptime(start, '%Y%m%d')
        monthCount = diff_month(
            date.today(), datetime.strptime(start, '%Y%m%d'))
        getYear = datetime.strptime(start, '%Y%m%d').year
        getMonth = datetime.strptime(start, '%Y%m%d').month
        df = pd.DataFrame(columns=list(
            ["date", "amount", "value", "open", "high", "low", "close", "spreads", "deal_sheets"]))

    print 'Downloading stock: %s from %d/%02d' % (stockNum, getYear, getMonth)
    i = 0
    retry = 0
    dataEmpty = False
    while i <= monthCount:
        # print 'Downloading stock: %s from %d/%02d' % (stockNum, getYear,
        # getMonth)
        jsonTmp = getJson(getYear, getMonth, stockNum)
        if jsonTmp != None:
            retry = 0
            dataEmpty = False
            df2 = pd.DataFrame(jsonTmp, columns=list(
                ["date", "amount", "value", "open", "high", "low", "close", "spreads", "deal_sheets"]))
            df = df.append(df2, ignore_index=True)
            df = df.drop_duplicates(['date'])
            df = df.reset_index(drop=True)
            if getMonth == 12:
                getMonth = 1
                getYear += 1
            else:
                getMonth += 1
        else:
            retry += 1
            dataEmpty = True
            print 'Retry', retry
            if retry == 3:
                retry = 0
                if getMonth == 12:
                    getMonth = 1
                    getYear += 1
                else:
                    getMonth += 1
            else:
                i -= 1

        i += 1

    # Save csv file
    # df.to_csv(csvFile, sep='\t', encoding='utf-8')
    # Save pickle file
    try:
        pickleFile = os.path.join('save', '%s.pickle' % stockNum)
        with open(pickleFile, 'wb') as f:
            pickle.dump(df, f)
        print 'Save file: %s successed' % pickleFile
    except Exception:
        #global errorList
        errorList.append(stockNum)
        print 'Save pickle error'
    if dataEmpty:
        errorList.append(stockNum)
        print 'Data empty at last month'
    if errorList != []:
        print 'Error list:', errorList


def getJson(y, m, n):
    try:
        req = requests.session()
        # req.get('http://www.twse.com.tw/zh/page/trading/exchange/STOCK_DAY.html',
        #        headers={'Accept-Language': 'zh-TW'})
        url = 'http://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date=%4d%02d01&stockNo=%s' % (
            y, m, n)
        response = req.get(url, headers={'Accept-Language': 'zh-TW'})
    except Exception:
        print 'Requests error in %d%02d' % (y, m)
        print 'url:', url
        return None
    try:
        if 'data' in response.json():
            # remove '--' data
            newJson = []
            print 'Get data in %d%02d' % (y, m)
            for i in response.json()['data']:
                if '--' in i:
                    pass
                else:
                    newJson.append(i)
            return newJson
        else:
            print 'No data in %d%02d' % (y, m)
            return None
    except Exception:
        print 'JSON decoded error in %d%02d' % (y, m)
        return None


def diff_month(d1, d2):
    return (d1.year - d2.year) * 12 + d1.month - d2.month


if __name__ == '__main__':
    main()
