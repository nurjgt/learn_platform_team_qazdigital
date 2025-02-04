import unittest

# Assume these are your functions
def process_quiz(quiz_id, answers):
    correct_answers = {
        'python_basic': ['a', 'b', 'c'],
        'sql_intro': ['b', 'a', 'c']
    }
    return correct_answers.get(quiz_id, []) == answers

def generate_certificate(user_name, quiz_id, score):
    if score == 3:
        return f"Certificate for {user_name} - {quiz_id} - Passed"
    else:
        return f"Certificate for {user_name} - {quiz_id} - Failed"

# Test class
class TestQuizSystem(unittest.TestCase):

    def test_correct_answers(self):
        """Testing correct answers for the quiz."""
        quiz_id = 'python_basic'
        answers = ['a', 'b', 'c']
        result = process_quiz(quiz_id, answers)
        self.assertTrue(result, "Answers should be correct.")

    def test_incorrect_answers(self):
        """Testing incorrect answers for the quiz."""
        quiz_id = 'python_basic'
        answers = ['a', 'b', 'd']
        result = process_quiz(quiz_id, answers)
        self.assertFalse(result, "Answers should not be correct.")

    def test_certificate_generation_pass(self):
        """Testing certificate generation for correct answers."""
        user_name = 'John Doe'
        quiz_id = 'python_basic'
        score = 3
        certificate = generate_certificate(user_name, quiz_id, score)
        self.assertEqual(certificate, f"Certificate for {user_name} - {quiz_id} - Passed")

    def test_certificate_generation_fail(self):
        """Testing certificate generation for incorrect answers."""
        user_name = 'John Doe'
        quiz_id = 'python_basic'
        score = 1
        certificate = generate_certificate(user_name, quiz_id, score)
        self.assertEqual(certificate, f"Certificate for {user_name} - {quiz_id} - Failed")


# Running the tests
if __name__ == '__main__':
    unittest.main()
