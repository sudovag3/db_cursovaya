# # db_manager.py
# import pyodbc
#
# class DBManager:
#     def __init__(self):
#         self.conn = None
#
#     def connect(self, server, database):
#         self.conn = pyodbc.connect('DRIVER={SQL Server};SERVER=WIN-A7QEQEU69OA;DATABASE=work5;Trust_Connection=yes;')
#
#     def execute_query(self, query, params=None):
#         cursor = self.conn.cursor()
#         if params:
#             cursor.execute(query, params)
#         else:
#             cursor.execute(query)
#         result = cursor.fetchall()
#         cursor.close()
#         return result
#
#     def commit(self):
#         self.conn.commit()
#
#     def close(self):
#         if self.conn:
#             self.conn.close()
