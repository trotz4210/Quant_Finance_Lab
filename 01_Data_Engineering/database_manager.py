import sqlite3
import pandas as pd
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DatabaseManager:
    """
    SQLite 데이터베이스와의 모든 상호작용을 관리하는 클래스.
    """
    def __init__(self, db_path):
        """
        데이터베이스 경로로 초기화합니다.
        :param db_path: SQLite 데이터베이스 파일의 경로
        """
        self.db_path = db_path
        self.conn = None

    def __enter__(self):
        """
        'with' 구문 사용 시 데이터베이스 연결을 엽니다.
        """
        try:
            self.conn = sqlite3.connect(self.db_path)
            logging.info(f"Database connection opened to {self.db_path}")
            return self
        except sqlite3.Error as e:
            logging.error(f"Error connecting to database: {e}")
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        'with' 구문 종료 시 데이터베이스 연결을 닫습니다.
        """
        if self.conn:
            self.conn.close()
            logging.info("Database connection closed.")

    def save_dataframe(self, df: pd.DataFrame, table_name: str):
        """
        DataFrame을 지정된 테이블 이름으로 데이터베이스에 저장합니다.
        테이블이 이미 존재하면 내용을 교체합니다.

        :param df: 저장할 pandas DataFrame
        :param table_name: 데이터베이스에 생성될 테이블의 이름
        """
        if self.conn is None:
            logging.error("Database connection is not open. Use 'with' statement.")
            return

        try:
            df.to_sql(table_name, self.conn, if_exists='replace', index=False)
            logging.info(f"Successfully saved {len(df)} rows to table '{table_name}'.")
        except Exception as e:
            logging.error(f"Error saving dataframe to table '{table_name}': {e}")