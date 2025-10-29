import pymysql

def test_db_connection():
    # 資料庫設定
    db_settings = {
        "host": "192.168.82.3",
        "port": 3306,
        #"port": 33060,
        #"user": "root",
		"user": "funthing_teach_web_root",
        #"password": "wmmkscsie",
		"password": "Funthing_teach_web_01",
        "db": "funthing_teach",
        "charset": "utf8"
    }

    try:
        # 嘗試連接資料庫
        conn = pymysql.connect(**db_settings)
        print("資料庫連接成功")
        
        # 連接成功後，可以選擇檢查資料庫中的表
        with conn.cursor() as cursor:
            cursor.execute("SHOW TABLES;")
            tables = cursor.fetchall()
            print("資料庫中的表:")
            for table in tables:
                print(table)
        
        # 關閉連接
        conn.close()

    except pymysql.MySQLError as e:
        print(f"連接資料庫失敗: {e}")

if __name__ == "__main__":
    test_db_connection()
