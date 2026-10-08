import unittest

from server import normalize_student_data, validate_student_id


class StudentValidationTests(unittest.TestCase):
    def test_normalize_student_data_trims_and_rejects_invalid_email(self):
        with self.assertRaises(ValueError) as error:
            normalize_student_data({
                "name": "  Arun  ",
                "email": "not-an-email",
                "course": " Python ",
            })
        self.assertEqual(str(error.exception), "A valid email address is required")

    def test_normalize_student_data_returns_trimmed_values(self):
        self.assertEqual(
            normalize_student_data({
                "name": "  Arun  ",
                "email": "arun@example.com",
                "course": " Python ",
            }),
            {
                "name": "Arun",
                "email": "arun@example.com",
                "course": "Python",
            },
        )

    def test_validate_student_id_rejects_invalid_ids(self):
        with self.assertRaises(ValueError):
            validate_student_id("not-a-number")


if __name__ == "__main__":
    unittest.main()
