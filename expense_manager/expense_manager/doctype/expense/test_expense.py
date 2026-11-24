import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import getdate

from expense_manager.expense_manager.doctype.expense.expense import (
    allowed_categories_for,
    create_expense,
    get_month_spend,
)
from expense_manager.expense_manager.factories import make_category, make_dependent, make_user


class TestExpense(FrappeTestCase):
    def setUp(self):
        self.guardian = make_user("test.guardian@example.com", "Individual")
        self.child = "test.child@example.com"
        self.dependent = make_dependent(self.child, self.guardian)
        self.food = make_category("Test Food")
        self.travel = make_category("Test Travel")

    def tearDown(self):
        frappe.set_user("Administrator")
        frappe.db.rollback()

    def test_overspending_a_budget_notifies_the_user(self):
        today = getdate()
        frappe.get_doc(
            {
                "doctype": "Budget",
                "user": self.guardian,
                "category": self.food,
                "month": str(today.month),
                "year": today.year,
                "amount": 100,
            }
        ).insert()
        create_expense(self.guardian, self.food, 150, "over", "Manual")
        subjects = frappe.get_all("Notification Log", filters={"for_user": self.guardian}, pluck="subject")
        self.assertTrue(any("Over budget" in subject for subject in subjects))

    def test_blocked_category_is_rejected(self):
        dependent = frappe.get_doc("Dependent", self.dependent)
        dependent.append("blocked_categories", {"category": self.travel})
        dependent.save()
        self.assertNotIn(self.travel, allowed_categories_for(self.child))
        with self.assertRaises(frappe.ValidationError):
            create_expense(self.child, self.travel, 10, "blocked", "Manual")

    def test_month_spend_adds_up_per_category(self):
        create_expense(self.guardian, self.food, 40, "a", "Manual")
        create_expense(self.guardian, self.travel, 60, "b", "Manual")
        today = getdate()
        self.assertEqual(get_month_spend(self.guardian, today, self.food), 40)
        self.assertEqual(get_month_spend(self.guardian, today), 100)
