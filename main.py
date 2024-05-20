import sys

import mysql.connector
from PyQt5.QtCore import QDate, Qt, QDateTime
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QTabWidget, QLineEdit, \
    QTextEdit, QMessageBox, QListWidget, QListWidgetItem, QFileDialog, QComboBox, QDialog, QDateTimeEdit, QSpinBox
from PyQt5.QtGui import QPixmap
import pyodbc
class OrderDetailsWindow(QDialog):
    def __init__(self, order_id, arrangement_name, order_date, delivery_date, delivery_address):
        super().__init__()
        self.setWindowTitle(f'Информация о заказе {order_id}')
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()

        label_order_id = QLabel(f'<b>Номер заказа:</b> {order_id}')
        layout.addWidget(label_order_id)

        label_arrangement_name = QLabel(f'<b>Композиция:</b> {arrangement_name}')
        layout.addWidget(label_arrangement_name)

        label_order_date = QLabel(f'<b>Дата заказа:</b> {order_date}')
        layout.addWidget(label_order_date)

        label_delivery_date = QLabel(f'<b>Дата доставки:</b> {delivery_date}')
        layout.addWidget(label_delivery_date)

        label_delivery_address = QLabel(f'<b>Адрес доставки:</b> {delivery_address}')
        layout.addWidget(label_delivery_address)

        self.setLayout(layout)

class DeliveryWindow(QDialog):
    def __init__(self, order_id, florist_id):
        super().__init__()

        self.order_id = order_id
        self.florist_id = florist_id

        self.setWindowTitle('Доставка')
        self.setGeometry(100, 100, 400, 200)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.date_edit = QDateTimeEdit()
        self.date_edit.setDateTime(QDateTime.currentDateTime())
        layout.addWidget(QLabel('Дата доставки:'))
        layout.addWidget(self.date_edit)

        self.address_input = QLineEdit()
        self.address_input.setPlaceholderText('Адрес доставки')
        layout.addWidget(self.address_input)

        self.courier_combo = QComboBox()  # Добавляем комбобокс для выбора курьера
        self.populate_couriers()  # Заполняем комбобокс курьерами
        layout.addWidget(self.courier_combo)

        add_button = QPushButton('Добавить доставку')
        add_button.clicked.connect(self.add_delivery)
        layout.addWidget(add_button)

        self.setLayout(layout)

    def populate_couriers(self):
        try:
            conn = mysql.connector.connect(
                host='127.0.0.1',
                user="root",
                password="root",
                database="rgr_db_default",
                port=33060
            )
            cursor = conn.cursor()

            cursor.execute("SELECT CourierID, Name FROM Courier")
            couriers = cursor.fetchall()

            for courier in couriers:
                courier_id, name = courier
                self.courier_combo.addItem(f'{courier_id}: {name}')

            conn.close()

        except pyodbc.Error as e:
            print(f'Ошибка при загрузке курьеров из базы данных: {str(e)}')

    def add_delivery(self):
        delivery_date = self.date_edit.dateTime().toString(Qt.ISODate)
        address = self.address_input.text()
        selected_courier = self.courier_combo.currentText().split(':')[0]  # Получаем идентификатор выбранного курьера

        if not address:
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, введите адрес доставки')
            return

        try:
            conn = mysql.connector.connect(
                host='127.0.0.1',
                user="root",
                password="root",
                database="rgr_db_default",
                port=33060
            )
            cursor = conn.cursor()

            cursor.execute("INSERT INTO Delivery (order_id, delivery_date, delivery_address, Courier) VALUES (%s, %s, %s, %s)",
                           (self.order_id,  delivery_date, address, selected_courier))
            conn.commit()

            QMessageBox.information(self, 'Успешно', 'Информация о доставке добавлена!')

            conn.close()
            self.close()

        except pyodbc.Error as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка при добавлении информации о доставке: {str(e)}')


class ProductDetailsWindow(QDialog):
    def __init__(self, composition_name, description, price, photo_data):
        super().__init__()

        self.setWindowTitle(composition_name)
        self.setGeometry(100, 100, 400, 400)

        self.init_ui(composition_name, description, price, photo_data)

    def init_ui(self, composition_name, description, price, photo_data):
        layout = QVBoxLayout()

        label_name = QLabel(f"<b>{composition_name}</b>")
        layout.addWidget(label_name)

        label_description = QLabel(description)
        layout.addWidget(label_description)

        label_price = QLabel(f"<b>Цена:</b> {price} руб.")
        layout.addWidget(label_price)

        pixmap = QPixmap()
        pixmap.loadFromData(photo_data)
        label_photo = QLabel()
        label_photo.setPixmap(pixmap.scaledToWidth(300))
        layout.addWidget(label_photo)

        self.setLayout(layout)

class AuthorizationWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.client_id = None  # Добавляем переменную для client_id
        self.florist_id = None
        self.setWindowTitle('Авторизация')
        self.setGeometry(100, 100, 400, 200)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        label = QLabel('Выберите тип пользователя:')
        layout.addWidget(label)

        self.user_type_combo = QComboBox()
        self.user_type_combo.addItems(['Клиент', 'Сотрудник'])
        layout.addWidget(self.user_type_combo)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText('Имя')
        layout.addWidget(self.name_input)

        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText('Телефон')
        layout.addWidget(self.phone_input)

        login_button = QPushButton('Войти')
        login_button.clicked.connect(self.login)
        layout.addWidget(login_button)

        self.setLayout(layout)

    def login(self):
        user_type = self.user_type_combo.currentText()
        name = self.name_input.text()
        phone = self.phone_input.text()

        try:
            conn = mysql.connector.connect(
                host='127.0.0.1',
                user="root",
                password="root",
                database="rgr_db_default",
                port=33060
            )
            cursor = conn.cursor()

            if user_type == 'Клиент':
                print(name, phone, "!@#@!#")
                cursor.execute("SELECT client_id FROM Clients WHERE client_name = %s AND client_phone = %s", (name, phone))
                client = cursor.fetchone()

                if client:
                    self.client_id = client[0]  # Сохраняем client_id
                    QMessageBox.information(self, 'Успешный вход', 'Добро пожаловать, клиент!')
                    self.open_client_page()
                else:
                    QMessageBox.warning(self, 'Ошибка входа', 'Неверные имя или телефон клиента!')

            elif user_type == 'Сотрудник':
                cursor.execute("SELECT florist_id FROM Florists WHERE florist_name = %s", (name,))
                florist = cursor.fetchone()

                if florist:
                    self.florist_id = florist[0]  # Сохраняем florist_id
                    QMessageBox.information(self, 'Успешный вход', 'Добро пожаловать, флорист!')
                    self.open_florist_page()
                else:
                    QMessageBox.warning(self, 'Ошибка входа', 'Неверное имя сотрудника (флориста)!')

        except pyodbc.Error as e:
            QMessageBox.critical(self, 'Ошибка подключения', f'Ошибка при подключении к базе данных:\n{str(e)}')

    def open_client_page(self):
        self.client_page = ClientPage(self.client_id)  # Передаем client_id в ClientPage
        self.client_page.show()
        self.close()

    def open_florist_page(self):
        self.florist_page = FloristPage(self.florist_id)
        self.florist_page.show()
        self.close()

class ClientPage(QWidget):
    def __init__(self, client_id):
        super().__init__()
        self.client_id = client_id

        self.setWindowTitle('Страница клиента')
        self.setGeometry(100, 100, 600, 400)

        self.init_ui()

    def show_product_details(self, item):
        try:
            composition_data = item.data(1)
            composition_name, description, price, photo_data = composition_data

            product_details_window = ProductDetailsWindow(composition_name, description, price, photo_data)
            product_details_window.exec_()

        except Exception as e:
            print(f'Ошибка при отображении подробностей продукта: {str(e)}')

    def show_order_details(self, item):
        try:
            order_id = item.data(Qt.UserRole)
            conn = mysql.connector.connect(
                host='127.0.0.1',
                user="root",
                password="root",
                database="rgr_db_default",
                port=33060
            )
            cursor = conn.cursor()

            cursor.execute("SELECT a.arrangement_name, o.order_date, d.delivery_date, d.delivery_address "
                           "FROM Orders o "
                           "INNER JOIN Arrangements a ON o.arrangement_id = a.arrangement_id "
                           "LEFT JOIN Delivery d ON o.order_id = d.order_id "
                           "WHERE o.order_id = %s", (order_id,))
            order_details = cursor.fetchone()

            if order_details:
                arrangement_name, order_date, delivery_date, delivery_address = order_details
                order_details_window = OrderDetailsWindow(order_id, arrangement_name, order_date,
                                                          delivery_date or 'Не доставлен',
                                                          delivery_address or 'Не указан')
                order_details_window.exec_()
            else:
                QMessageBox.warning(self, 'Ошибка', 'Информация о заказе не найдена')

            conn.close()

        except pyodbc.Error as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка при загрузке информации о заказе: {str(e)}')

    def init_ui(self):
        layout = QVBoxLayout()

        label = QLabel('Доступные композиции:')
        layout.addWidget(label)

        self.compositions_list = QListWidget()
        self.compositions_list.itemDoubleClicked.connect(self.show_product_details)
        self.populate_compositions()
        layout.addWidget(self.compositions_list)

        label_my_orders = QLabel('Мои заказы:')
        layout.addWidget(label_my_orders)

        self.my_orders_list = QListWidget()
        self.my_orders_list.itemDoubleClicked.connect(self.show_order_details)  # Обработчик двойного клика
        self.populate_my_orders()
        layout.addWidget(self.my_orders_list)

        logout_button = QPushButton('Выход')
        logout_button.clicked.connect(self.logout)
        layout.addWidget(logout_button)

        self.setLayout(layout)

    def populate_my_orders(self):
        try:
            conn = mysql.connector.connect(
                host='127.0.0.1',
                user="root",
                password="root",
                database="rgr_db_default",
                port=33060
            )
            cursor = conn.cursor()

            # Получаем заказы текущего клиента
            cursor.execute("SELECT order_id, order_date FROM Orders WHERE client_id = %s", (self.client_id,))
            orders = cursor.fetchall()

            # Очищаем список перед добавлением новых элементов
            self.my_orders_list.clear()

            # Добавляем заказы в список
            for order in orders:
                order_id, order_date = order
                item = QListWidgetItem(f'Заказ {order_id}: {order_date}')
                item.setData(Qt.UserRole, order_id)  # Сохраняем ID заказа в элементе списка
                self.my_orders_list.addItem(item)

            # Закрываем соединение с базой данных
            conn.close()

        except pyodbc.Error as e:
            print(f'Ошибка при загрузке заказов клиента из базы данных: {str(e)}')
    def populate_compositions(self):
        try:
            conn = mysql.connector.connect(
                host='127.0.0.1',
                user="root",
                password="root",
                database="rgr_db_default",
                port=33060
            )
            cursor = conn.cursor()

            cursor.execute("SELECT arrangement_name, description, price, photo FROM Arrangements")
            compositions = cursor.fetchall()

            for composition in compositions:
                composition_name = composition[0]
                item = QListWidgetItem(composition_name)
                item.setData(1, composition)  # Сохраняем данные о композиции в элементе списка
                self.compositions_list.addItem(item)

            conn.close()

        except pyodbc.Error as e:
            print(f'Ошибка при загрузке композиций из базы данных: {str(e)}')

    def show_product_details(self, item):
        try:
            composition_data = item.data(1)  # Получаем данные о композиции
            composition_name, description, price, photo_data = composition_data

            product_details_window = ProductDetailsWindow(composition_name, description, price, photo_data)
            product_details_window.exec_()  # Открываем окно с подробностями о продукте

        except Exception as e:
            print(f'Ошибка при отображении подробностей продукта: {str(e)}')

    def logout(self):
        self.close()
class SupplierOrderWindow(QDialog):
    def __init__(self, supplier_id):
        super().__init__()

        self.supplier_id = supplier_id

        self.setWindowTitle('Заказ у поставщика')
        self.setGeometry(100, 100, 400, 200)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.product_input = QLineEdit()
        self.product_input.setPlaceholderText('Название продукта')
        layout.addWidget(self.product_input)

        self.quantity_input = QSpinBox()
        self.quantity_input.setMinimum(1)
        self.quantity_input.setMaximum(999)
        layout.addWidget(self.quantity_input)

        submit_button = QPushButton('Оформить заказ')
        submit_button.clicked.connect(self.submit_order)
        layout.addWidget(submit_button)

        self.setLayout(layout)

    def submit_order(self):
        product_name = self.product_input.text()
        quantity = self.quantity_input.value()

        if not product_name:
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, введите название продукта')
            return

        try:
            conn = mysql.connector.connect(
                host='127.0.0.1',
                user="root",
                password="root",
                database="rgr_db_default",
                port=33060
            )
            cursor = conn.cursor()

            cursor.execute("INSERT INTO Postavki ( Arrangemetns, PostID, Quantity) VALUES (%s, %s, %s)",
                           (product_name,self.supplier_id, quantity))
            conn.commit()

            QMessageBox.information(self, 'Успешно', 'Заказ у поставщика оформлен!')

            conn.close()
            self.close()

        except pyodbc.Error as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка при оформлении заказа у поставщика: {str(e)}')

class FloristPage(QWidget):
    def __init__(self, florist_id):
        super().__init__()
        self.setWindowTitle('Страница флориста')
        self.setGeometry(100, 100, 800, 600)
        self.florist_id = florist_id  # Сохраняем идентификатор флориста
        self.init_ui()  # Инициализация интерфейса

    def init_ui(self):
        layout = QVBoxLayout()

        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)

        # Вкладка "Оформление заказа"
        order_tab = QWidget()
        self.init_order_tab(order_tab)
        tab_widget.addTab(order_tab, 'Оформление заказа')

        # Вкладка "Добавление композиции"
        add_composition_tab = QWidget()
        self.init_add_composition_tab(add_composition_tab)
        tab_widget.addTab(add_composition_tab, 'Добавление композиции')

        # Вкладка "Мои заказы"
        my_orders_tab = QWidget()
        self.init_my_orders_tab(my_orders_tab)
        tab_widget.addTab(my_orders_tab, 'Мои заказы')

        # Вкладка "Доставка"
        delivery_tab = QWidget()
        self.init_delivery_tab(delivery_tab)
        tab_widget.addTab(delivery_tab, 'Доставка')

        # Вкладка "Поставщики"
        supplier_tab = QWidget()
        self.init_supplier_tab(supplier_tab)
        tab_widget.addTab(supplier_tab, 'Поставщики')

        # Новая вкладка "Все доставки"
        all_deliveries_tab = QWidget()
        self.init_all_deliveries_tab(all_deliveries_tab)
        tab_widget.addTab(all_deliveries_tab, 'Все доставки')

        # Новая вкладка "Все поставки"
        all_supplier_orders_tab = QWidget()
        self.init_all_supplier_orders_tab(all_supplier_orders_tab)
        tab_widget.addTab(all_supplier_orders_tab, 'Все поставки')

        logout_button = QPushButton('Выход')
        logout_button.clicked.connect(self.logout)
        layout.addWidget(logout_button)

        self.setLayout(layout)

    def init_all_deliveries_tab(self, all_deliveries_tab):
        layout = QVBoxLayout()

        label = QLabel('Все доставки:')
        layout.addWidget(label)

        self.all_deliveries_list = QListWidget()
        self.populate_all_deliveries()
        layout.addWidget(self.all_deliveries_list)

        all_deliveries_tab.setLayout(layout)

    def populate_all_deliveries(self):
        try:
            conn = mysql.connector.connect(
                host='127.0.0.1',
                user="root",
                password="root",
                database="rgr_db_default",
                port=33060
            )
            cursor = conn.cursor()

            cursor.execute("SELECT d.order_id, d.delivery_date, d.delivery_address, c.Name "
                           "FROM Delivery d "
                           "INNER JOIN Courier c ON d.Courier = c.CourierID")
            deliveries = cursor.fetchall()

            for delivery in deliveries:
                order_id, delivery_date, delivery_address, courier_name = delivery
                item = QListWidgetItem(
                    f'Заказ {order_id}: Доставка {delivery_date} по адресу {delivery_address}. Курьер: {courier_name}')
                self.all_deliveries_list.addItem(item)

            conn.close()

        except pyodbc.Error as e:
            print(f'Ошибка при загрузке всех доставок из базы данных: {str(e)}')

    def init_all_supplier_orders_tab(self, all_supplier_orders_tab):
        layout = QVBoxLayout()

        label = QLabel('Все поставки:')
        layout.addWidget(label)

        self.all_supplier_orders_list = QListWidget()
        self.populate_all_supplier_orders()
        layout.addWidget(self.all_supplier_orders_list)

        all_supplier_orders_tab.setLayout(layout)

    def populate_all_supplier_orders(self):
        try:
            conn = mysql.connector.connect(
                host='127.0.0.1',
                user="root",
                password="root",
                database="rgr_db_default",
                port=33060
            )
            cursor = conn.cursor()

            cursor.execute("SELECT so.PostavkaID, s.Name, so.Arrangemetns, so.Quantity "
                           "FROM Postavki so "
                           "INNER JOIN Post s ON so.PostID = s.PostID")
            supplier_orders = cursor.fetchall()

            for supplier_order in supplier_orders:
                supplier_id, supplier_name, product_name, quantity = supplier_order
                item = QListWidgetItem(f'Поставщик {supplier_name}: Продукт {product_name}, Количество {quantity}')
                self.all_supplier_orders_list.addItem(item)

            conn.close()

        except pyodbc.Error as e:
            print(f'Ошибка при загрузке всех поставок из базы данных: {str(e)}')

    def init_supplier_tab(self, supplier_tab):
        layout = QVBoxLayout()

        label = QLabel('Поставщики:')
        layout.addWidget(label)

        self.supplier_list = QListWidget()
        self.populate_suppliers()
        layout.addWidget(self.supplier_list)

        order_button = QPushButton('Оформить заказ')
        order_button.clicked.connect(self.order_from_supplier)
        layout.addWidget(order_button)

        supplier_tab.setLayout(layout)

    def order_from_supplier(self):
        selected_supplier = self.supplier_list.currentItem().text().split(':')[
            0]  # Получаем идентификатор выбранного поставщика

        supplier_order_window = SupplierOrderWindow(selected_supplier)
        supplier_order_window.exec_()
    def populate_suppliers(self):
        try:
            conn = mysql.connector.connect(
                host='127.0.0.1',
                user="root",
                password="root",
                database="rgr_db_default",
                port=33060
            )
            cursor = conn.cursor()

            cursor.execute("SELECT PostID, Name FROM Post")
            suppliers = cursor.fetchall()

            for supplier in suppliers:
                supplier_id, name = supplier
                self.supplier_list.addItem(f'{supplier_id}: {name}')

            conn.close()

        except pyodbc.Error as e:
            print(f'Ошибка при загрузке поставщиков из базы данных: {str(e)}')
    def init_order_tab(self, order_tab):
        layout = QVBoxLayout()

        label_client = QLabel('Выберите клиента:')
        layout.addWidget(label_client)

        self.client_combo = QComboBox()
        self.populate_clients()
        layout.addWidget(self.client_combo)

        label_composition = QLabel('Выберите композицию:')
        layout.addWidget(label_composition)

        self.composition_combo = QComboBox()
        self.populate_compositions()
        layout.addWidget(self.composition_combo)

        submit_button = QPushButton('Оформить заказ')
        submit_button.clicked.connect(self.submit_order)
        layout.addWidget(submit_button)

        order_tab.setLayout(layout)

    def init_add_composition_tab(self, add_composition_tab):
        layout = QVBoxLayout()

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText('Название композиции')
        layout.addWidget(self.name_input)

        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText('Описание композиции')
        layout.addWidget(self.description_input)

        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText('Цена (руб.)')
        layout.addWidget(self.price_input)

        add_button = QPushButton('Добавить композицию')
        add_button.clicked.connect(self.add_composition)
        layout.addWidget(add_button)

        add_composition_tab.setLayout(layout)

    def init_my_orders_tab(self, my_orders_tab):
        layout = QVBoxLayout()

        label = QLabel('Мои заказы:')
        layout.addWidget(label)

        self.my_orders_list = QListWidget()
        self.my_orders_list.itemDoubleClicked.connect(self.show_delivery_window)
        self.populate_my_orders()
        layout.addWidget(self.my_orders_list)

        my_orders_tab.setLayout(layout)

    def populate_my_orders(self):
        try:
            conn = mysql.connector.connect(
                host='127.0.0.1',
                user="root",
                password="root",
                database="rgr_db_default",
                port=33060
            )
            cursor = conn.cursor()

            # Запрос для получения заказов текущего флориста
            cursor.execute("SELECT o.order_id, a.arrangement_name, o.order_date FROM Orders o INNER JOIN Florist_Assignment fa ON o.order_id = fa.order_id INNER JOIN Arrangements a ON o.arrangement_id = a.arrangement_id WHERE fa.florist_id = %s", (self.florist_id,))
            orders = cursor.fetchall()

            for order in orders:
                order_id, arrangement_name, order_date = order
                item = QListWidgetItem(f'Заказ {order_id}: {arrangement_name} ({order_date})')
                item.setData(Qt.UserRole, order_id)  # Сохраняем ID заказа в элементе списка
                self.my_orders_list.addItem(item)

            conn.close()

        except pyodbc.Error as e:
            print(f'Ошибка при загрузке заказов флориста из базы данных: {str(e)}')

    def init_delivery_tab(self, delivery_tab):
        layout = QVBoxLayout()

        label_order = QLabel('Выберите заказ:')
        layout.addWidget(label_order)

        self.order_combo = QComboBox()
        self.populate_orders()
        layout.addWidget(self.order_combo)

        submit_button = QPushButton('Отправить на доставку')
        submit_button.clicked.connect(self.send_to_delivery)
        layout.addWidget(submit_button)

        delivery_tab.setLayout(layout)

    def populate_orders(self):
        try:
            conn = mysql.connector.connect(
                host='127.0.0.1',
                user="root",
                password="root",
                database="rgr_db_default",
                port=33060
            )
            cursor = conn.cursor()

            # Запрос для получения заказов текущего флориста
            cursor.execute(
                "SELECT o.order_id, a.arrangement_name FROM Orders o INNER JOIN Florist_Assignment fa ON o.order_id = fa.order_id INNER JOIN Arrangements a ON o.arrangement_id = a.arrangement_id WHERE fa.florist_id = %s",
                (self.florist_id,))
            orders = cursor.fetchall()

            for order in orders:
                order_id, arrangement_name = order
                self.order_combo.addItem(f'{order_id}: {arrangement_name}')

            conn.close()

        except pyodbc.Error as e:
            print(f'Ошибка при загрузке заказов флориста из базы данных: {str(e)}')

    def send_to_delivery(self):
        selected_order = self.order_combo.currentText().split(':')[0]  # Получаем идентификатор выбранного заказа

        delivery_window = DeliveryWindow(selected_order, self.florist_id)
        delivery_window.exec_()

    def logout(self):
        self.close()
    def populate_clients(self):
        try:
            conn = mysql.connector.connect(
                host='127.0.0.1',
                user="root",
                password="root",
                database="rgr_db_default",
                port=33060
            )
            cursor = conn.cursor()

            cursor.execute("SELECT client_name FROM Clients")
            clients = cursor.fetchall()

            for client in clients:
                self.client_combo.addItem(client[0])

            conn.close()

        except pyodbc.Error as e:
            print(f'Ошибка при загрузке клиентов из базы данных: {str(e)}')

    def populate_compositions(self):
        try:
            conn = mysql.connector.connect(
                host='127.0.0.1',
                user="root",
                password="root",
                database="rgr_db_default",
                port=33060
            )
            cursor = conn.cursor()

            cursor.execute("SELECT arrangement_name FROM Arrangements")
            compositions = cursor.fetchall()

            for composition in compositions:
                self.composition_combo.addItem(composition[0])

            conn.close()

        except pyodbc.Error as e:
            print(f'Ошибка при загрузке композиций из базы данных: {str(e)}')

    def add_composition(self):
        name = self.name_input.text()
        description = self.description_input.toPlainText()
        price = self.price_input.text()

        if not name or not description or not price:
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, заполните все поля')
            return

        try:
            conn = mysql.connector.connect(
                host='127.0.0.1',
                user="root",
                password="root",
                database="rgr_db_default",
                port=33060
            )
            cursor = conn.cursor()

            cursor.execute("INSERT INTO Arrangements (arrangement_name, description, price) VALUES (%s, %s, %s)",
                           (name, description, price))
            conn.commit()

            QMessageBox.information(self, 'Успешно', 'Композиция добавлена в базу данных!')

            # Очистка полей после добавления композиции
            self.name_input.clear()
            self.description_input.clear()
            self.price_input.clear()

            conn.close()

        except pyodbc.Error as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка при добавлении композиции в базу данных: {str(e)}')

    def submit_order(self):
        client_name = self.client_combo.currentText()
        composition_name = self.composition_combo.currentText()
        order_date = QDate.currentDate().toString(Qt.ISODate)

        try:
            conn = mysql.connector.connect(
                host='127.0.0.1',
                user="root",
                password="root",
                database="rgr_db_default",
                port=33060
            )
            cursor = conn.cursor()

            cursor.execute("SELECT client_id FROM Clients WHERE client_name = %s", (client_name,))
            client_id = cursor.fetchone()[0]

            cursor.execute("SELECT arrangement_id FROM Arrangements WHERE arrangement_name = %s", (composition_name,))
            arrangement_id = cursor.fetchone()[0]

            cursor.execute("INSERT INTO Orders (client_id, arrangement_id, order_date) VALUES (%s, %s, %s)",
                           (client_id, arrangement_id, order_date))
            conn.commit()

            QMessageBox.information(self, 'Успешно', 'Заказ оформлен!')

            conn.close()

        except pyodbc.Error as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка при оформлении заказа: {str(e)}')

    def show_delivery_window(self, item):
        order_id = item.data(Qt.UserRole)  # Получаем ID заказа
        delivery_window = DeliveryWindow(order_id, self.florist_id)
        delivery_window.exec_()

    def logout(self):
        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    current_client_id = 1
    auth_window = AuthorizationWindow()
    auth_window.show()
    sys.exit(app.exec_())
