import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import getdate

from expense_manager.api import add_dependent
from expense_manager.expense_manager.doctype.dependent.dependent import (
    get_pocket_money_balance,
    roll_over_to_savings,
)
from expense_manager.expense_manager.doctype.expense.expense import create_expense
from expense_manager.expense_manager.factories import PASSWORD, make_category, make_dependent, make_user


class TestDependent(FrappeTestCase):
    def setUp(self):
        self.guardian = make_user("test.guardian@example.com", "Individual")
        self.child = "test.child@example.com"
        self.dependent = make_dependent(self.child, self.guardian)
        self.food = make_category("Test Food")
        today = getdate()
        frappe.get_doc(
            {
                "doctype": "Pocket Money Allocation",
                "dependent": self.dependent,
                "month": str(today.month),
                "year": today.year,
                "amount": 1000,
            }
        ).insert()

    def tearDown(self):
        frappe.set_user("Administrator")
        frappe.db.rollback()

    def test_balance_is_allocation_minus_spend(self):
        create_expense(self.child, self.food, 250, "snacks", "Manual")
        balance = get_pocket_money_balance(self.dependent)
        self.assertEqual(balance["allocated"], 1000)
        self.assertEqual(balance["spent"], 250)
        self.assertEqual(balance["balance"], 750)

    def test_rollover_moves_the_balance_once(self):
        create_expense(self.child, self.food, 250, "snacks", "Manual")
        self.assertEqual(roll_over_to_savings(self.dependent), 750)
        self.assertEqual(roll_over_to_savings(self.dependent), 0)
        balance = get_pocket_money_balance(self.dependent)
        self.assertEqual(balance["balance"], 0)
        self.assertEqual(balance["total_savings"], 750)

    def test_overspent_dependent_rolls_over_nothing(self):
        create_expense(self.child, self.food, 1200, "big", "Manual")
        self.assertEqual(roll_over_to_savings(self.dependent), 0)
        self.assertEqual(frappe.get_all("Savings Entry", filters={"dependent": self.dependent}), [])

    def test_dependent_cannot_read_another_dependents_data(self):
        sibling = "test.sibling@example.com"
        other = make_dependent(sibling, self.guardian)
        create_expense(self.child, self.food, 100, "mine", "Manual")
        create_expense(sibling, self.food, 200, "theirs", "Manual")
        frappe.set_user(self.child)
        self.assertEqual(set(frappe.get_list("Expense", pluck="spent_by")), {self.child})
        with self.assertRaises(frappe.PermissionError):
            get_pocket_money_balance(other)

    def test_individual_sees_their_dependents_expenses(self):
        create_expense(self.child, self.food, 100, "kid", "Manual")
        frappe.set_user(self.guardian)
        self.assertIn(self.child, frappe.get_list("Expense", pluck="spent_by"))

    def test_individual_can_add_a_dependent(self):
        frappe.set_user(self.guardian)
        add_dependent("Test Kid Two", "test.kidtwo@example.com", PASSWORD)
        self.assertTrue(
            frappe.db.exists("Dependent", {"user": "test.kidtwo@example.com", "parent_user": self.guardian})
        )
        self.assertIn("Dependent", frappe.get_roles("test.kidtwo@example.com"))
