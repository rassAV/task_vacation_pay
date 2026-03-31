import sys
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QLabel, QListWidget
)
from PySide6.QtGui import QFont

# бд
engine = create_engine("sqlite:///vacation.db", echo=False)
Base = declarative_base()

class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    salary = Column(Float)
    days = Column(Integer)
    vacation_pay = Column(Float)

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

# расчет отпускных
def calc_vacation(salary, days):
    return (salary / 29.3) * days

# главное окно
class App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Расчет отпускных")
        self.resize(800, 500)

        layout = QVBoxLayout()

        # поля ввода
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Имя сотрудника")
        self.salary_input = QLineEdit()
        self.salary_input.setPlaceholderText("Зарплата")
        self.days_input = QLineEdit()
        self.days_input.setPlaceholderText("Дни отпуска")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Фильтрация по имени (необязательно)")

        layout.addWidget(self.name_input)
        layout.addWidget(self.salary_input)
        layout.addWidget(self.days_input)
        layout.addWidget(self.search_input)

        # кнопки добавить и показать
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Добавить запись")
        self.show_btn = QPushButton("Показать записи")
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.show_btn)
        layout.addLayout(btn_layout)

        # кнопки для сортировки
        sort_layout = QHBoxLayout()
        self.s_salary_asc = QPushButton("ЗП ↑")
        self.s_salary_desc = QPushButton("ЗП ↓")
        self.s_days_asc = QPushButton("Дни ↑")
        self.s_days_desc = QPushButton("Дни ↓")
        self.s_vac_asc = QPushButton("Отпуск ↑")
        self.s_vac_desc = QPushButton("Отпуск ↓")
        for b in [self.s_salary_asc, self.s_salary_desc, self.s_days_asc,
                  self.s_days_desc, self.s_vac_asc, self.s_vac_desc]:
            sort_layout.addWidget(b)
        layout.addLayout(sort_layout)

        # список и строка информирующая пользователя
        self.list_widget = QListWidget()
        mono_font = QFont("Courier New")
        mono_font.setPointSize(10)
        self.list_widget.setFont(mono_font)
        self.status_label = QLabel("")
        layout.addWidget(self.list_widget)
        layout.addWidget(self.status_label)

        self.setLayout(layout)

        # события
        self.add_btn.clicked.connect(self.add_employee)
        self.show_btn.clicked.connect(lambda: self.show_employees())
        self.s_salary_asc.clicked.connect(lambda: self.show_employees(sort_field="salary", ascending=True))
        self.s_salary_desc.clicked.connect(lambda: self.show_employees(sort_field="salary", ascending=False))
        self.s_days_asc.clicked.connect(lambda: self.show_employees(sort_field="days", ascending=True))
        self.s_days_desc.clicked.connect(lambda: self.show_employees(sort_field="days", ascending=False))
        self.s_vac_asc.clicked.connect(lambda: self.show_employees(sort_field="vacation_pay", ascending=True))
        self.s_vac_desc.clicked.connect(lambda: self.show_employees(sort_field="vacation_pay", ascending=False))

    # добавление записи
    def add_employee(self):
        try:
            name = self.name_input.text().strip()
            salary = float(self.salary_input.text())
            days = int(self.days_input.text())
            vacation = calc_vacation(salary, days)

            session = Session()
            emp = Employee(name=name, salary=salary, days=days, vacation_pay=vacation)
            session.add(emp)
            session.commit()
            self.status_label.setText(f"Запись ID {emp.id} успешно добавлена")
            self.name_input.clear()
            self.salary_input.clear()
            self.days_input.clear()
        except Exception as e:
            self.status_label.setText("Ошибка при добавлении данных")

    # показать записи
    def show_employees(self, sort_field=None, ascending=True):
        try:
            session = Session()
            self.list_widget.clear()
            query = session.query(Employee)

            # фильтр по имени
            search_text = self.search_input.text().strip()
            if search_text:
                query = query.filter(Employee.name.contains(search_text))

            # сортировка
            if sort_field:
                col = getattr(Employee, sort_field)
                query = query.order_by(col.asc() if ascending else col.desc())

            header = f"{'ID':<4} {'Имя':<30} {'ЗП':<18} {'Дни':<6} {'Отпускные':<18}"
            self.list_widget.addItem(header)
            self.list_widget.addItem("-"*80)

            for e in query:
                line = f"{e.id:<4} {e.name:<30} {e.salary:>18.2f} {e.days:>6} {e.vacation_pay:>18.2f}"
                self.list_widget.addItem(line)
            
            if search_text:
                self.status_label.setText(f"Показано {query.count()} записей по фильтру - {search_text}")
            else:
                self.status_label.setText(f"Показано {query.count()} записей")
        except Exception:
            self.status_label.setText("Ошибка отображения данных")


# запуск приложения
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec())
