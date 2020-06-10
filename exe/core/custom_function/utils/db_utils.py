import cx_Oracle
class DBOperation:
    def __init__(self,db_config):
        ip = db_config['ip']
        port = db_config['port']
        sid = db_config['sid']
        self.user = db_config['user']
        self.pwd = db_config['pwd']
        self.dsnStr = cx_Oracle.makedsn(ip,port,sid)
        #test connect 
        self._disconnect(self._connect())
        
    def create(self,table_name,column_names,insert_data):
        column_tuple,value_tuple = self._col_tuple(column_names)
        db_connection = self._connect()

        if db_connection!=None:
            try:
                print('connect ok start insert')
                cursor = db_connection.cursor()
                sql = f"INSERT INTO {table_name}{column_tuple} VALUES {value_tuple}"
                cursor.prepare(sql)
                cursor.executemany(None,insert_data)
                print('finish insert')
                db_connection.commit()
                # self._commit(db_connection)
                print('finish commit')
                self._disconnect(db_connection)
                print('finish disconnect')
            except Exception as e:
                print(str(e))
                self.error = str(e)
                self._disconnect(db_connection)
        
    def update(self,update_table_name,update_dict,hashkey):
        try:
            update_str=''
            for k,v in update_dict.items():
                update_str+= f"{k}='{v}',"
            update_str = update_str[:-1]
            db_connection = self._connect()
            cursor = db_connection.cursor()
            sql = f"UPDATE {update_table_name} SET {update_str} WHERE HASH_KEY='{hashkey}' "
            print('start update',str(sql))
            cursor.prepare(sql)
            cursor.execute(sql)
            db_connection.commit()
            print('finish update',str(sql))
        except Exception as e:
            print(sql)
            print('update failed')
            print(e)
        
    def read(self,table_name,selected_columns,select_filter):
        cols= ','.join(selected_columns)
        condiction=''
        for k,v in select_filter.items():
            condiction+=f" {k}='{v}' and"
        condiction = condiction[:-3]
        db_connection = self._connect()
        if db_connection!=None:
            cursor = db_connection.cursor()
            sql = f"SELECT {cols} FROM {table_name} where{condiction}"
            print(sql)
            cursor.prepare(sql)
            cursor.execute(sql)
            return list(cursor)
    def delete(self):
        pass
    def _connect(self):
        try:
            db_connection =  cx_Oracle.connect(self.user,self.pwd,dsn=self.dsnStr)
            print('connect ok')
            self.status=True
        except Exception as e:
            self.error = str(e)
            self.status=False
            db_connection = None
        return db_connection
    def _disconnect(self,db_connection):
        if db_connection!=None:
            db_connection.close()
    def _commit(self,db_connection):
        db_connection.commit()
        # if db_connection!=None:
        #     db_connection.commit()
    
    def _col_tuple(self,column_names):
        cols = []
        for i in [column_names]:
            col = "("
            for j in i:
                tmp = j+','
                col+=tmp
            col = col[:-1]+')'
            cols.append(col)
        for i in [column_names]:
            col = "("
            for j in i:
                tmp =':'+ j+','
                col+=tmp
            col = col[:-1]+')'
            cols.append(col)
        return cols