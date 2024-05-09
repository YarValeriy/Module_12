import unittest
from unittest.mock import MagicMock, AsyncMock
from datetime import date, timedelta
from sqlalchemy import and_, or_, extract
from sqlalchemy.orm import Session
from src.repository import contacts
from src.database.models import Contact, User
from src.schemas import ContactCreate, ContactUpdate


class TestContactRepository(unittest.IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        self.db_session_mock = MagicMock(spec=Session)
        self.user = User(id=1, username="test_user", email="test@example.com")
        self.contact_mock = MagicMock(spec=Contact)

    async def test_create_contact(self):
        contact_data = ContactCreate(name="John", surname="Doe", email="john@example.com", phone="123456789",
                                     birthday=date(1990, 10, 20))
        result = await contacts.create_contact(contact_data, self.user, self.db_session_mock)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Contact)

    async def test_get_contact(self):
        contact_id = 1
        contact = Contact()
        self.db_session_mock.query().filter().first.return_value = contact
        result = await contacts.get_contact(contact_id, self.user, self.db_session_mock)
        self.assertEqual(result, contact)

    async def test_get_contact_not_found(self):
        contact_id = 1
        self.db_session_mock.query().filter().first.return_value = None
        result = await contacts.get_contact(contact_id, self.user, self.db_session_mock)
        self.assertIsNone(result)

    async def test_update_contact(self):
        contact_id = 1
        # Mocking the repository function
        contacts.get_contact = AsyncMock(return_value=Contact(id=contact_id))
        contact_update = ContactUpdate(name="John", surname="Doe", email="john@example.com", phone="123456789",
                                       birthday=date(1985, 10, 20))
        # Running the function to test
        result = await contacts.update_contact(contact_id, contact_update, self.user, self.db_session_mock)
        self.assertIsNotNone(result)
        self.assertEqual(result, contacts.get_contact.return_value)

    async def test_delete_contact(self):
        contact_id = 1
        # Running the function to test
        deleted_contact = await contacts.delete_contact(contact_id, self.user, self.db_session_mock)

        # Asserting that the session methods were called with correct arguments
        self.db_session_mock.commit.assert_called_once()

        # Asserting that the function returned the expected result
        self.assertEqual(deleted_contact, {"message": "Contact deleted successfully"})

    async def test_get_contacts(self):
        query_mock = MagicMock()
        query_mock.all.return_value = [
            Contact(id=1, name="John", surname="Doe", email="john@example.com", phone='987654321',
                    birthday=date(1990, 1, 1)),
            Contact(id=2, name="Jane", surname="Smith", email="jane@example.com", phone='987456123',
                    birthday=date(1991, 2, 2)),
            Contact(id=3, name="Alice", surname="Johnson", email="alice@example.com", phone='789456123',
                    birthday=date(1992, 3, 3)),
        ]

        # Mock the filter method of the query object
        query_mock.filter.return_value = query_mock

        # Mock the query method of the database session to return the query object
        self.db_session_mock.query.return_value = query_mock

        # Call the function under test
        contacts_list = await contacts.get_contacts(name="John", surname="Doe", email="john@example.com",
                                                    phone='987654321', birthday=date(1990, 1, 1),
                                                    user=self.user, db=self.db_session_mock)

        # Verify that the filter conditions are constructed correctly
        self.db_session_mock.query.assert_called_once_with(Contact)

        # Assert that the function returned the expected list of contacts
        self.assertEqual(len(contacts_list), 3)
        self.assertEqual(contacts_list[0].id, 1)
        self.assertEqual(contacts_list[1].id, 2)
        self.assertEqual(contacts_list[2].id, 3)

    async def test_get_birthdays(self):
        start_date = date.today()
        end_date = start_date + timedelta(days=7)

        # Create mock contacts with birthdays falling within the specified date range
        query_mock = MagicMock()
        query_mock.all.return_value = [
            Contact(id=1, name="John", surname="Doe", email="john@example.com", phone='987654321',
                    birthday=start_date),
            Contact(id=2, name="Jane", surname="Smith", email="jane@example.com", phone='987456123',
                    birthday=end_date),
            Contact(id=3, name="Alice", surname="Johnson", email="alice@example.com", phone='789456123',
                    birthday=start_date),
        ]

        # Mock the filter method of the query object
        query_mock.filter.return_value = query_mock

        # Mock the query method of the database session to return the query object
        self.db_session_mock.query.return_value = query_mock

        # Call the function under test

        birthdays = await contacts.get_birthdays(start_date, end_date, self.user, self.db_session_mock)

        # Verify that the filter conditions are constructed correctly
        self.db_session_mock.query.assert_called_once_with(Contact)

        # Assert that the function returned the expected list of contacts
        self.assertEqual(len(birthdays), 3)
        self.assertEqual(birthdays[0].id, 1)
        self.assertEqual(birthdays[1].id, 2)
        self.assertEqual(birthdays[2].id, 3)


if __name__ == '__main__':
    unittest.main()
