import pytest
from unittest.mock import Mock
from uuid import uuid4
from datetime import datetime
from fastapi import HTTPException

from chat_api.threads.thread_service import ThreadService
from chat_api.threads.thread_repository import ThreadRepository
from chat_api.threads.thread_response_model import ThreadResponse, Message, SearchResult
from chat_api.threads.models import Thread
from chat_api.chats.models import Chat


@pytest.fixture
def mock_repository():
    """Create a mock repository."""
    return Mock(spec=ThreadRepository)


@pytest.fixture
def thread_service(mock_repository):
    """Create a ThreadService instance with mock repository."""
    return ThreadService(mock_repository)


@pytest.fixture
def sample_thread_id():
    """Generate a sample thread ID."""
    return uuid4()


@pytest.fixture
def sample_chat_id():
    """Generate a sample chat ID."""
    return uuid4()


@pytest.fixture
def sample_thread(sample_thread_id):
    """Create a sample thread without chats."""
    thread = Mock(spec=Thread)
    thread.id = sample_thread_id
    thread.email = "test@example.com"
    thread.created_at = datetime.utcnow()
    thread.updated_at = datetime.utcnow()
    thread.is_deleted = False
    thread.chats = []
    return thread


@pytest.fixture
def sample_chat(sample_chat_id):
    """Create a sample chat."""
    chat = Mock(spec=Chat)
    chat.id = sample_chat_id
    chat.question = "What is Python?"
    chat.response = {
        "answer": "Python is a programming language.",
        "search_results": [
            {
                "id": "1",
                "title": "Python Documentation",
                "text": "Python is a high-level programming language."
            }
        ]
    }
    chat.created_at = datetime.utcnow()
    return chat


class TestThreadServiceInit:
    """Tests for ThreadService initialization."""
    
    def test_init_with_repository(self, mock_repository):
        """Test that ThreadService initializes with a repository."""
        service = ThreadService(mock_repository)
        assert service.repository == mock_repository


class TestGetThreadById:
    """Tests for the get_thread_by_id method."""
    
    def test_get_thread_by_id_success(self, thread_service, mock_repository, sample_thread_id, sample_chat_id):
        """Test successfully retrieving a thread by ID."""
        thread = Mock(spec=Thread)
        thread.id = sample_thread_id
        
        chat = Mock(spec=Chat)
        chat.id = sample_chat_id
        chat.question = "Test question"
        chat.response = {"answer": "Test answer", "search_results": []}
        chat.created_at = datetime.utcnow()
        
        thread.chats = [chat]
        mock_repository.get_thread_by_id.return_value = thread
        
        result = thread_service.get_thread_by_id(sample_thread_id)
        
        assert isinstance(result, ThreadResponse)
        assert result.id == sample_thread_id
        assert result.title == "Test question"
        assert len(result.messages) == 2
        mock_repository.get_thread_by_id.assert_called_once_with(sample_thread_id)
    
    def test_get_thread_by_id_not_found(self, thread_service, mock_repository, sample_thread_id):
        """Test retrieving a non-existent thread raises HTTPException."""
        mock_repository.get_thread_by_id.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            thread_service.get_thread_by_id(sample_thread_id)
        
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Thread not found"
        mock_repository.get_thread_by_id.assert_called_once_with(sample_thread_id)
    
    def test_get_thread_by_id_empty_chats(self, thread_service, mock_repository, sample_thread_id):
        """Test retrieving a thread with no chats."""
        thread = Mock(spec=Thread)
        thread.id = sample_thread_id
        thread.chats = []
        
        mock_repository.get_thread_by_id.return_value = thread
        
        result = thread_service.get_thread_by_id(sample_thread_id)
        
        assert isinstance(result, ThreadResponse)
        assert result.id == sample_thread_id
        assert result.title == "Untitled Thread"
        assert len(result.messages) == 0
    
    def test_get_thread_by_id_multiple_chats(self, thread_service, mock_repository, sample_thread_id):
        """Test retrieving a thread with multiple chats."""
        thread = Mock(spec=Thread)
        thread.id = sample_thread_id
        
        chat1 = Mock(spec=Chat)
        chat1.id = uuid4()
        chat1.question = "First question"
        chat1.response = {"answer": "First answer", "search_results": []}
        chat1.created_at = datetime(2024, 1, 1, 10, 0, 0)
        
        chat2 = Mock(spec=Chat)
        chat2.id = uuid4()
        chat2.question = "Second question"
        chat2.response = {"answer": "Second answer", "search_results": []}
        chat2.created_at = datetime(2024, 1, 1, 11, 0, 0)
        
        thread.chats = [chat1, chat2]
        mock_repository.get_thread_by_id.return_value = thread
        
        result = thread_service.get_thread_by_id(sample_thread_id)
        
        assert result.title == "First question"
        assert len(result.messages) == 4
        assert result.messages[0].content == "First question"
        assert result.messages[1].content == "First answer"
        assert result.messages[2].content == "Second question"
        assert result.messages[3].content == "Second answer"


class TestTransformChatsToMessages:
    """Tests for the transform_chats_to_messages method."""
    
    def test_transform_empty_chats(self, thread_service):
        """Test transforming an empty list of chats."""
        result = thread_service.transform_chats_to_messages([])
        assert result == []
    
    def test_transform_single_chat_with_dict_response(self, thread_service, sample_chat_id):
        """Test transforming a single chat with dict response."""
        chat = Mock(spec=Chat)
        chat.id = sample_chat_id
        chat.question = "What is Python?"
        chat.response = {
            "answer": "Python is a programming language.",
            "search_results": []
        }
        chat.created_at = datetime.utcnow()
        
        result = thread_service.transform_chats_to_messages([chat])
        
        assert len(result) == 2
        assert result[0].role == "user"
        assert result[0].content == "What is Python?"
        assert result[0].id == sample_chat_id
        assert result[0].searchResults is None
        
        assert result[1].role == "assistant"
        assert result[1].content == "Python is a programming language."
        assert result[1].id == sample_chat_id
        assert result[1].searchResults is None
    
    def test_transform_chat_with_search_results(self, thread_service, sample_chat_id):
        """Test transforming a chat with search results."""
        chat = Mock(spec=Chat)
        chat.id = sample_chat_id
        chat.question = "What is Python?"
        chat.response = {
            "answer": "Python is a programming language.",
            "search_results": [
                {
                    "id": "1",
                    "title": "Python Docs",
                    "text": "Python is a high-level language."
                },
                {
                    "id": "2",
                    "title": "Python Tutorial",
                    "text": "Learn Python programming."
                }
            ]
        }
        chat.created_at = datetime.utcnow()
        
        result = thread_service.transform_chats_to_messages([chat])
        
        assert len(result) == 2
        assert result[1].searchResults is not None
        assert len(result[1].searchResults) == 2
        assert result[1].searchResults[0].id == "1"
        assert result[1].searchResults[0].title == "Python Docs"
        assert result[1].searchResults[0].text == "Python is a high-level language."
        assert result[1].searchResults[1].id == "2"
    
    def test_transform_chat_with_non_dict_response(self, thread_service, sample_chat_id):
        """Test transforming a chat with non-dict response."""
        chat = Mock(spec=Chat)
        chat.id = sample_chat_id
        chat.question = "What is Python?"
        chat.response = "Simple string response"
        chat.created_at = datetime.utcnow()
        
        result = thread_service.transform_chats_to_messages([chat])
        
        assert len(result) == 1
        assert result[0].role == "user"
        assert result[0].content == "What is Python?"
    
    def test_transform_multiple_chats_sorted_by_created_at(self, thread_service):
        """Test that chats are sorted by created_at timestamp."""
        chat1 = Mock(spec=Chat)
        chat1.id = uuid4()
        chat1.question = "First question"
        chat1.response = {"answer": "First answer", "search_results": []}
        chat1.created_at = datetime(2024, 1, 1, 12, 0, 0)
        
        chat2 = Mock(spec=Chat)
        chat2.id = uuid4()
        chat2.question = "Second question"
        chat2.response = {"answer": "Second answer", "search_results": []}
        chat2.created_at = datetime(2024, 1, 1, 10, 0, 0)
        
        chat3 = Mock(spec=Chat)
        chat3.id = uuid4()
        chat3.question = "Third question"
        chat3.response = {"answer": "Third answer", "search_results": []}
        chat3.created_at = datetime(2024, 1, 1, 11, 0, 0)
        
        result = thread_service.transform_chats_to_messages([chat1, chat2, chat3])
        
        assert len(result) == 6
        assert result[0].content == "Second question"
        assert result[2].content == "Third question"
        assert result[4].content == "First question"
    
    def test_transform_chat_with_missing_answer_key(self, thread_service, sample_chat_id):
        """Test transforming a chat with missing answer key in response."""
        chat = Mock(spec=Chat)
        chat.id = sample_chat_id
        chat.question = "What is Python?"
        chat.response = {"search_results": []}
        chat.created_at = datetime.utcnow()
        
        result = thread_service.transform_chats_to_messages([chat])
        
        assert len(result) == 2
        assert result[1].content == ""
    
    def test_transform_chat_with_missing_search_results_key(self, thread_service, sample_chat_id):
        """Test transforming a chat with missing search_results key."""
        chat = Mock(spec=Chat)
        chat.id = sample_chat_id
        chat.question = "What is Python?"
        chat.response = {"answer": "Python is a programming language."}
        chat.created_at = datetime.utcnow()
        
        result = thread_service.transform_chats_to_messages([chat])
        
        assert len(result) == 2
        assert result[1].searchResults is None
    
    def test_transform_chat_with_empty_search_results(self, thread_service, sample_chat_id):
        """Test transforming a chat with empty search results list."""
        chat = Mock(spec=Chat)
        chat.id = sample_chat_id
        chat.question = "What is Python?"
        chat.response = {
            "answer": "Python is a programming language.",
            "search_results": []
        }
        chat.created_at = datetime.utcnow()
        
        result = thread_service.transform_chats_to_messages([chat])
        
        assert len(result) == 2
        assert result[1].searchResults is None
    
    def test_transform_chat_with_incomplete_search_result_data(self, thread_service, sample_chat_id):
        """Test transforming a chat with incomplete search result data."""
        chat = Mock(spec=Chat)
        chat.id = sample_chat_id
        chat.question = "What is Python?"
        chat.response = {
            "answer": "Python is a programming language.",
            "search_results": [
                {
                    "title": "Python Docs"
                },
                {
                    "id": "2",
                    "text": "Some text"
                }
            ]
        }
        chat.created_at = datetime.utcnow()
        
        result = thread_service.transform_chats_to_messages([chat])
        
        assert len(result) == 2
        assert result[1].searchResults is not None
        assert len(result[1].searchResults) == 2
        assert result[1].searchResults[0].id == ""
        assert result[1].searchResults[0].title == "Python Docs"
        assert result[1].searchResults[0].text == ""
        assert result[1].searchResults[1].id == "2"
        assert result[1].searchResults[1].title == ""
        assert result[1].searchResults[1].text == "Some text"
    
    def test_transform_preserves_chat_id_in_messages(self, thread_service):
        """Test that chat ID is preserved in both user and assistant messages."""
        chat_id = uuid4()
        chat = Mock(spec=Chat)
        chat.id = chat_id
        chat.question = "Test question"
        chat.response = {"answer": "Test answer", "search_results": []}
        chat.created_at = datetime.utcnow()
        
        result = thread_service.transform_chats_to_messages([chat])
        
        assert result[0].id == chat_id
        assert result[1].id == chat_id
    
    def test_transform_multiple_chats_with_mixed_responses(self, thread_service):
        """Test transforming multiple chats with mixed response types."""
        chat1 = Mock(spec=Chat)
        chat1.id = uuid4()
        chat1.question = "Question 1"
        chat1.response = {"answer": "Answer 1", "search_results": []}
        chat1.created_at = datetime(2024, 1, 1, 10, 0, 0)
        
        chat2 = Mock(spec=Chat)
        chat2.id = uuid4()
        chat2.question = "Question 2"
        chat2.response = "String response"
        chat2.created_at = datetime(2024, 1, 1, 11, 0, 0)
        
        chat3 = Mock(spec=Chat)
        chat3.id = uuid4()
        chat3.question = "Question 3"
        chat3.response = {
            "answer": "Answer 3",
            "search_results": [{"id": "1", "title": "Result", "text": "Text"}]
        }
        chat3.created_at = datetime(2024, 1, 1, 12, 0, 0)
        
        result = thread_service.transform_chats_to_messages([chat1, chat2, chat3])
        
        assert len(result) == 5
        assert result[0].content == "Question 1"
        assert result[1].content == "Answer 1"
        assert result[2].content == "Question 2"
        assert result[3].content == "Question 3"
        assert result[4].content == "Answer 3"
        assert result[4].searchResults is not None


class TestDeleteThreadById:
    """Tests for the delete_thread_by_id method."""
    
    def test_delete_thread_success(self, thread_service, mock_repository, sample_thread_id):
        """Test successfully soft deleting a thread."""
        mock_repository.soft_delete_thread.return_value = True
        
        result = thread_service.delete_thread_by_id(sample_thread_id)
        
        assert result["message"] == "Thread deleted successfully"
        assert result["thread_id"] == str(sample_thread_id)
        mock_repository.soft_delete_thread.assert_called_once_with(sample_thread_id)
    
    def test_delete_thread_not_found(self, thread_service, mock_repository, sample_thread_id):
        """Test deleting a non-existent thread raises HTTPException."""
        mock_repository.soft_delete_thread.return_value = False
        
        with pytest.raises(HTTPException) as exc_info:
            thread_service.delete_thread_by_id(sample_thread_id)
        
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Thread not found or already deleted"
        mock_repository.soft_delete_thread.assert_called_once_with(sample_thread_id)
    
    def test_delete_already_deleted_thread(self, thread_service, mock_repository, sample_thread_id):
        """Test deleting an already deleted thread raises HTTPException."""
        mock_repository.soft_delete_thread.return_value = False
        
        with pytest.raises(HTTPException) as exc_info:
            thread_service.delete_thread_by_id(sample_thread_id)
        
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Thread not found or already deleted"
