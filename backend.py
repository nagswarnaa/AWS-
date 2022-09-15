import pymysql
import pandas as pds
import numpy as nup


class backend:

    def __init__(myobject, config):

        myobject.db_nm = config['db_nm']
        myobject.user = config['unm']
        myobject.password = config['pwd']
        myobject.server = config['hst']

    def make_conn(myobject):
        try:
            db_conn = None
            db_conn = pymysql.connect(
                host=myobject.server, user=myobject.user, password=myobject.password, db=myobject.db_nm)
        except:
            print(f"Issue in database connection please check")
        return db_conn

    def made_bat(myobject, data, n=100):
        return [data[x:x+n] for x in range(0, len(data), n)]

    def det_get(myobject, cmmd):
        cnn = myobject.make_conn()
        dataframe = pds.read_sql(cmmd, con=cnn)
        cnn.close()
        return dataframe

    def made_qty(myobject, df):
        clms = df.columns
        vls = '%s,'*(len(clms)-1)+'%s'
        inst_qry = f"""INSERT INTO {myobject.table_name} ("""
        for cnt, cl in enumerate(clms):
            inst_qry += str(cl)
            if cnt != len(clms)-1:
                inst_qry += ','
        inst_qry += f""") VALUES ({vls})"""
        return inst_qry

    def put_dt(myobject, table_name, json_data):
        cnn = myobject.make_conn()
        myobject.table_name = table_name
        with cnn.cursor() as cursor:
            temp_df = pds.DataFrame(json_data)
            qry = myobject.made_qty(df=temp_df)
            bts = myobject.made_bat(temp_df)
            for cnt, btc in enumerate(bts):
                btc = btc.replace({nup.NaN: None})
                dta = tuple(tuple(i) for i in btc.values)
                cursor.executemany(qry, dta)
                cnn.commit()
        cnn.close()
