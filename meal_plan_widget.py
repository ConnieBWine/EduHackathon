from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QWidget, QScrollArea, QPushButton, QInputDialog, QMessageBox
from PyQt6.QtCore import Qt

class MealPlanWidget(QWidget):
    def __init__(self, meal_plan=None, meal_planner=None):
        super().__init__()
        self.meal_plan = meal_plan
        self.meal_planner = meal_planner
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("background-color: #1e1e1e; border: none;")
        
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(10, 10, 10, 10)
        self.content_layout.setSpacing(15)
        
        self.scroll_area.setWidget(self.content_widget)
        layout.addWidget(self.scroll_area)

        # Add update button
        self.update_button = QPushButton("Update Meal Plan")
        self.update_button.clicked.connect(self.update_meal_plan_button_clicked)
        layout.addWidget(self.update_button)

        self.update_plan()

    def update_plan(self):
        # Clear existing widgets
        for i in reversed(range(self.content_layout.count())): 
            self.content_layout.itemAt(i).widget().setParent(None)

        if self.meal_plan:
            for day in self.meal_plan:
                day_widget = self.create_day_widget(day)
                self.content_layout.addWidget(day_widget)
        else:
            self.display_no_plan_message()

    def create_day_widget(self, day):
        day_widget = QWidget()
        day_layout = QVBoxLayout(day_widget)
        
        day_label = QLabel(day['day'])
        day_label.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
        day_layout.addWidget(day_label)
        
        for meal, food in day['meals'].items():
            meal_label = QLabel(f"{meal.capitalize()}: {food}")
            meal_label.setStyleSheet("color: #cccccc; font-size: 16px;")
            meal_label.setWordWrap(True)
            day_layout.addWidget(meal_label)
        
        day_widget.setStyleSheet("background-color: #2d2d2d; border-radius: 10px; padding: 15px; margin-bottom: 15px;")
        return day_widget

    def display_no_plan_message(self):
        message_label = QLabel("No meal plan generated yet.")
        message_label.setStyleSheet("""
            color: #cccccc;
            font-size: 18px;
            background-color: #1e1e1e;
            padding: 30px;
            border-radius: 10px;
            qproperty-alignment: AlignCenter;
        """)
        self.content_layout.addWidget(message_label)

    def set_meal_plan(self, meal_plan):
        self.meal_plan = meal_plan
        self.update_plan()

    def update_meal_plan_button_clicked(self):
        user_request, ok = QInputDialog.getText(self, "Update Meal Plan", "Enter your meal plan update request:")
        if ok and user_request:
            try:
                updated_plan = self.meal_planner.update_meal_plan(user_request)
                if isinstance(updated_plan, list):
                    self.set_meal_plan(updated_plan)
                    QMessageBox.information(self, "Success", "Meal plan updated successfully!")
                else:
                    QMessageBox.warning(self, "Error", str(updated_plan))
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to update meal plan: {str(e)}")