import data_prepare

while True:
    # ret = data_prepare.getAllBook(0, 10000)
    ret = data_prepare.getAllBook(10001, 20000)
    # ret = data_prepare.getAllBook(20001, 30000)
    # ret = data_prepare.getAllBook(30001, 40000)
    # ret = data_prepare.getAllBook(40001, 50000)
    # ret = data_prepare.getAllBook(50001, 54866)
    # ret = data_prepare.getAllBook(0, 54866)
    if len(ret)==0:
        break



# import data_statistics
# data_statistics.init(rebuild=True, banlist=[[],['Various', 'Anonymous'],[]])
# # data_statistics.init(banlist=[[],['Various', 'Anonymous'],[]])
# from data_statistics import rootp
# data_statistics.queryCnt(p=rootp)
# data_statistics.queryCnt(p=rootp+'/00')
# data_statistics.queryMax(p=rootp+'/00', depth=1, tp='folder', metric='files')
# data_statistics.queryMax(p=rootp+'/00', depth=1, tp='folder', metric='words')
# data_statistics.queryMax(p=rootp+'/00', depth=2, tp='file', metric='words')
