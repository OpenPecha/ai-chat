import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from unittest.mock import Mock, patch, MagicMock
from uuid import uuid4, UUID
from datetime import datetime

from chat_api.threads.thread_views import thread_router, get_db
from chat_api.threads.thread_response_model import ThreadResponse, Message, SearchResult
from chat_api.threads.models import Thread
from chat_api.chats.models import Chat


@pytest.fixture
def app():
    """Create a FastAPI app with the thread router."""
    app = FastAPI()
    app.include_router(thread_router)
    return app


@pytest.fixture
def client(app):
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def mock_db():
    """Create a mock database session."""
    return Mock()


@pytest.fixture
def sample_thread_id():
    """Generate a sample thread ID."""
    return uuid4()


@pytest.fixture
def sample_chat_id():
    """Generate a sample chat ID."""
    return uuid4()


@pytest.fixture
def sample_thread(sample_thread_id, sample_chat_id):
    """Create a sample thread with chats."""
    thread = Mock(spec=Thread)
    thread.id = sample_thread_id
    thread.email = "test@example.com"
    thread.created_at = datetime.utcnow()
    thread.updated_at = datetime.utcnow()
    thread.is_deleted = False
    
    # Create sample chats
    chat1 = Mock(spec=Chat)
    chat1.id = sample_chat_id
    chat1.question = "What is Python?"
    chat1.response = {
        "answer": "Python is a programming language.",
        "search_results": [
            {
                "id": "1",
                "title": "Python Documentation",
                "text": "Python is a high-level programming language."
            }
        ]
    }
    chat1.created_at = datetime.utcnow()
    
    thread.chats = [chat1]
    return thread


@pytest.fixture
def sample_thread_response(sample_thread_id, sample_chat_id):
    """Create a sample thread response."""
    return ThreadResponse(
        id=sample_thread_id,
        title="What is Python?",
        messages=[
            Message(
                role="user",
                content="What is Python?",
                id=sample_chat_id,
                searchResults=None
            ),
            Message(
                role="assistant",
                content="Python is a programming language.",
                id=sample_chat_id,
                searchResults=[
                    SearchResult(
                        id="1",
                        title="Python Documentation",
                        text="Python is a high-level programming language."
                    )
                ]
            )
        ]
    )


class TestGetThread:
    """Tests for the get_thread endpoint."""
    
    def test_get_thread_success(self, client, mock_db, sample_thread, sample_thread_response):
        """Test successfully retrieving a thread."""
        thread_id = sample_thread.id
        
        def override_get_db():
            yield mock_db
        
        client.app.dependency_overrides[get_db] = override_get_db
        
        with patch('chat_api.threads.thread_views.ThreadRepository') as mock_repo_class, \
             patch('chat_api.threads.thread_views.ThreadService') as mock_service_class:
            
            mock_repo = Mock()
            mock_service = Mock()
            mock_repo_class.return_value = mock_repo
            mock_service_class.return_value = mock_service
            mock_service.get_thread_by_id.return_value = sample_thread_response
            
            response = client.get(f"/threads/{thread_id}")
            
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == str(sample_thread_response.id)
            assert data["title"] == sample_thread_response.title
            assert len(data["messages"]) == 2
            assert data["messages"][0]["role"] == "user"
            assert data["messages"][1]["role"] == "assistant"
            
            mock_repo_class.assert_called_once_with(mock_db)
            mock_service_class.assert_called_once_with(mock_repo)
            mock_service.get_thread_by_id.assert_called_once_with(thread_id)
        
        client.app.dependency_overrides.clear()
    
    def test_get_thread_not_found(self, client, mock_db):
        """Test retrieving a non-existent thread."""
        thread_id = uuid4()
        
        def override_get_db():
            yield mock_db
        
        client.app.dependency_overrides[get_db] = override_get_db
        
        with patch('chat_api.threads.thread_views.ThreadRepository') as mock_repo_class, \
             patch('chat_api.threads.thread_views.ThreadService') as mock_service_class:
            
            from fastapi import HTTPException
            
            mock_repo = Mock()
            mock_service = Mock()
            mock_repo_class.return_value = mock_repo
            mock_service_class.return_value = mock_service
            mock_service.get_thread_by_id.side_effect = HTTPException(
                status_code=404, 
                detail="Thread not found"
            )
            
            response = client.get(f"/threads/{thread_id}")
            
            assert response.status_code == 404
            assert response.json()["detail"] == "Thread not found"
        
        client.app.dependency_overrides.clear()
    
    def test_get_thread_invalid_uuid(self, client, mock_db):
        """Test retrieving a thread with an invalid UUID."""
        invalid_id = "not-a-uuid"
        
        def override_get_db():
            yield mock_db
        
        client.app.dependency_overrides[get_db] = override_get_db
        
        response = client.get(f"/threads/{invalid_id}")
        
        assert response.status_code == 422
        
        client.app.dependency_overrides.clear()
    
    def test_get_thread_with_multiple_chats(self, client, mock_db, sample_thread_id):
        """Test retrieving a thread with multiple chats."""
        chat_id_1 = uuid4()
        chat_id_2 = uuid4()
        
        thread_response = ThreadResponse(
            id=sample_thread_id,
            title="First question",
            messages=[
                Message(role="user", content="First question", id=chat_id_1, searchResults=None),
                Message(role="assistant", content="First answer", id=chat_id_1, searchResults=None),
                Message(role="user", content="Second question", id=chat_id_2, searchResults=None),
                Message(role="assistant", content="Second answer", id=chat_id_2, searchResults=None),
            ]
        )
        
        def override_get_db():
            yield mock_db
        
        client.app.dependency_overrides[get_db] = override_get_db
        
        with patch('chat_api.threads.thread_views.ThreadRepository') as mock_repo_class, \
             patch('chat_api.threads.thread_views.ThreadService') as mock_service_class:
            
            mock_repo = Mock()
            mock_service = Mock()
            mock_repo_class.return_value = mock_repo
            mock_service_class.return_value = mock_service
            mock_service.get_thread_by_id.return_value = thread_response
            
            response = client.get(f"/threads/{sample_thread_id}")
            
            assert response.status_code == 200
            data = response.json()
            assert len(data["messages"]) == 4
            assert data["messages"][0]["content"] == "First question"
            assert data["messages"][1]["content"] == "First answer"
            assert data["messages"][2]["content"] == "Second question"
            assert data["messages"][3]["content"] == "Second answer"
        
        client.app.dependency_overrides.clear()
    
    def test_get_thread_with_search_results(self, client, mock_db, sample_thread_id, sample_chat_id):
        """Test retrieving a thread with search results."""
        thread_response = ThreadResponse(
            id=sample_thread_id,
            title="Question with search",
            messages=[
                Message(role="user", content="Question with search", id=sample_chat_id, searchResults=None),
                Message(
                    role="assistant", 
                    content="Answer with search results", 
                    id=sample_chat_id,
                    searchResults=[
                        SearchResult(id="1", title="Result 1", text="Text 1"),
                        SearchResult(id="2", title="Result 2", text="Text 2"),
                    ]
                ),
            ]
        )
        
        def override_get_db():
            yield mock_db
        
        client.app.dependency_overrides[get_db] = override_get_db
        
        with patch('chat_api.threads.thread_views.ThreadRepository') as mock_repo_class, \
             patch('chat_api.threads.thread_views.ThreadService') as mock_service_class:
            
            mock_repo = Mock()
            mock_service = Mock()
            mock_repo_class.return_value = mock_repo
            mock_service_class.return_value = mock_service
            mock_service.get_thread_by_id.return_value = thread_response
            
            response = client.get(f"/threads/{sample_thread_id}")
            
            assert response.status_code == 200
            data = response.json()
            assert len(data["messages"]) == 2
            assert data["messages"][1]["searchResults"] is not None
            assert len(data["messages"][1]["searchResults"]) == 2
            assert data["messages"][1]["searchResults"][0]["title"] == "Result 1"
            assert data["messages"][1]["searchResults"][1]["title"] == "Result 2"
        
        client.app.dependency_overrides.clear()


class TestGetDbDependency:
    
    def test_get_db_yields_session(self):
        with patch('chat_api.threads.thread_views.SessionLocal') as mock_session_local:
            mock_db = Mock()
            mock_session_local.return_value = mock_db
            
            db_generator = get_db()
            
            db = next(db_generator)
            
            assert db == mock_db
            mock_session_local.assert_called_once()
            
            try:
                next(db_generator)
            except StopIteration:
                pass
            
            mock_db.close.assert_called_once()
    
    def test_get_db_closes_session_on_exception(self):
        with patch('chat_api.threads.thread_views.SessionLocal') as mock_session_local:
            mock_db = Mock()
            mock_session_local.return_value = mock_db
            
            db_generator = get_db()
            
            db = next(db_generator)
            
            try:
                db_generator.throw(Exception("Test exception"))
            except Exception:
                pass
            
            mock_db.close.assert_called_once()


class TestGetAllThreads:
    
    def test_get_all_threads_no_filters(self, client, mock_db):
        def override_get_db():
            yield mock_db
        
        client.app.dependency_overrides[get_db] = override_get_db
        
        with patch('chat_api.threads.thread_views.ThreadRepository') as mock_repo_class, \
             patch('chat_api.threads.thread_views.ThreadService') as mock_service_class:
            
            mock_repo = Mock()
            mock_service = Mock()
            mock_repo_class.return_value = mock_repo
            mock_service_class.return_value = mock_service
            mock_service.get_all_threads.return_value = {
                "data": [
                    {"id": str(uuid4()), "title": "Thread 1"},
                    {"id": str(uuid4()), "title": "Thread 2"}
                ],
                "total": 2
            }
            
            response = client.get("/threads")
            
            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 2
            assert len(data["data"]) == 2
            assert data["data"][0]["title"] == "Thread 1"
            assert data["data"][1]["title"] == "Thread 2"
            
            mock_service.get_all_threads.assert_called_once_with(
                email=None,
                application=None,
                skip=0,
                limit=10
            )
        
        client.app.dependency_overrides.clear()
    
    def test_get_all_threads_with_email_filter(self, client, mock_db):
        def override_get_db():
            yield mock_db
        
        client.app.dependency_overrides[get_db] = override_get_db
        
        with patch('chat_api.threads.thread_views.ThreadRepository') as mock_repo_class, \
             patch('chat_api.threads.thread_views.ThreadService') as mock_service_class:
            
            mock_repo = Mock()
            mock_service = Mock()
            mock_repo_class.return_value = mock_repo
            mock_service_class.return_value = mock_service
            mock_service.get_all_threads.return_value = {
                "data": [{"id": str(uuid4()), "title": "User Thread"}],
                "total": 1
            }
            
            response = client.get("/threads?email=test@example.com")
            
            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 1
            
            mock_service.get_all_threads.assert_called_once_with(
                email="test@example.com",
                application=None,
                skip=0,
                limit=10
            )
        
        client.app.dependency_overrides.clear()
    
    def test_get_all_threads_with_application_filter(self, client, mock_db):
        def override_get_db():
            yield mock_db
        
        client.app.dependency_overrides[get_db] = override_get_db
        
        with patch('chat_api.threads.thread_views.ThreadRepository') as mock_repo_class, \
             patch('chat_api.threads.thread_views.ThreadService') as mock_service_class:
            
            mock_repo = Mock()
            mock_service = Mock()
            mock_repo_class.return_value = mock_repo
            mock_service_class.return_value = mock_service
            mock_service.get_all_threads.return_value = {
                "data": [{"id": str(uuid4()), "title": "App Thread"}],
                "total": 1
            }
            
            response = client.get("/threads?application=my-app")
            
            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 1
            
            mock_service.get_all_threads.assert_called_once_with(
                email=None,
                application="my-app",
                skip=0,
                limit=10
            )
        
        client.app.dependency_overrides.clear()
    
    def test_get_all_threads_with_pagination(self, client, mock_db):
        def override_get_db():
            yield mock_db
        
        client.app.dependency_overrides[get_db] = override_get_db
        
        with patch('chat_api.threads.thread_views.ThreadRepository') as mock_repo_class, \
             patch('chat_api.threads.thread_views.ThreadService') as mock_service_class:
            
            mock_repo = Mock()
            mock_service = Mock()
            mock_repo_class.return_value = mock_repo
            mock_service_class.return_value = mock_service
            mock_service.get_all_threads.return_value = {
                "data": [],
                "total": 50
            }
            
            response = client.get("/threads?skip=10&limit=20")
            
            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 50
            
            mock_service.get_all_threads.assert_called_once_with(
                email=None,
                application=None,
                skip=10,
                limit=20
            )
        
        client.app.dependency_overrides.clear()
    
    def test_get_all_threads_with_all_filters(self, client, mock_db):
        def override_get_db():
            yield mock_db
        
        client.app.dependency_overrides[get_db] = override_get_db
        
        with patch('chat_api.threads.thread_views.ThreadRepository') as mock_repo_class, \
             patch('chat_api.threads.thread_views.ThreadService') as mock_service_class:
            
            mock_repo = Mock()
            mock_service = Mock()
            mock_repo_class.return_value = mock_repo
            mock_service_class.return_value = mock_service
            mock_service.get_all_threads.return_value = {
                "data": [{"id": str(uuid4()), "title": "Filtered Thread"}],
                "total": 1
            }
            
            response = client.get("/threads?email=user@test.com&application=test-app&skip=5&limit=15")
            
            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 1
            
            mock_service.get_all_threads.assert_called_once_with(
                email="user@test.com",
                application="test-app",
                skip=5,
                limit=15
            )
        
        client.app.dependency_overrides.clear()
    
    def test_get_all_threads_empty_result(self, client, mock_db):
        def override_get_db():
            yield mock_db
        
        client.app.dependency_overrides[get_db] = override_get_db
        
        with patch('chat_api.threads.thread_views.ThreadRepository') as mock_repo_class, \
             patch('chat_api.threads.thread_views.ThreadService') as mock_service_class:
            
            mock_repo = Mock()
            mock_service = Mock()
            mock_repo_class.return_value = mock_repo
            mock_service_class.return_value = mock_service
            mock_service.get_all_threads.return_value = {
                "data": [],
                "total": 0
            }
            
            response = client.get("/threads")
            
            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 0
            assert len(data["data"]) == 0
        
        client.app.dependency_overrides.clear()
    
    def test_get_all_threads_response_structure(self, client, mock_db):
        def override_get_db():
            yield mock_db
        
        client.app.dependency_overrides[get_db] = override_get_db
        
        with patch('chat_api.threads.thread_views.ThreadRepository') as mock_repo_class, \
             patch('chat_api.threads.thread_views.ThreadService') as mock_service_class:
            
            mock_repo = Mock()
            mock_service = Mock()
            mock_repo_class.return_value = mock_repo
            mock_service_class.return_value = mock_service
            mock_service.get_all_threads.return_value = {
                "data": [
                    {"id": str(uuid4()), "title": "Thread 1"}
                ],
                "total": 1
            }
            
            response = client.get("/threads")
            
            assert response.status_code == 200
            data = response.json()
            assert "data" in data
            assert "total" in data
            assert isinstance(data["data"], list)
            assert isinstance(data["total"], int)
            assert "id" in data["data"][0]
            assert "title" in data["data"][0]
        
        client.app.dependency_overrides.clear()
    
    def test_get_all_threads_default_pagination_values(self, client, mock_db):
        def override_get_db():
            yield mock_db
        
        client.app.dependency_overrides[get_db] = override_get_db
        
        with patch('chat_api.threads.thread_views.ThreadRepository') as mock_repo_class, \
             patch('chat_api.threads.thread_views.ThreadService') as mock_service_class:
            
            mock_repo = Mock()
            mock_service = Mock()
            mock_repo_class.return_value = mock_repo
            mock_service_class.return_value = mock_service
            mock_service.get_all_threads.return_value = {
                "data": [],
                "total": 0
            }
            
            response = client.get("/threads")
            
            assert response.status_code == 200
            
            mock_service.get_all_threads.assert_called_once_with(
                email=None,
                application=None,
                skip=0,
                limit=10
            )
        
        client.app.dependency_overrides.clear()


class TestThreadRouter:
    
    def test_router_exists(self):
        from chat_api.threads.thread_views import thread_router
        assert thread_router is not None
        assert hasattr(thread_router, 'routes')
    
    def test_get_thread_route_registered(self):
        from chat_api.threads.thread_views import thread_router
        
        routes = [route for route in thread_router.routes]
        assert len(routes) > 0
        
        get_thread_route = None
        for route in routes:
            if hasattr(route, 'path') and '/threads/{thread_id}' in route.path:
                get_thread_route = route
                break
        
        assert get_thread_route is not None
        assert 'GET' in get_thread_route.methods
    
    def test_get_all_threads_route_registered(self):
        from chat_api.threads.thread_views import thread_router
        
        routes = [route for route in thread_router.routes]
        
        get_all_threads_route = None
        for route in routes:
            if hasattr(route, 'path') and route.path == '/threads':
                get_all_threads_route = route
                break
        
        assert get_all_threads_route is not None
        assert 'GET' in get_all_threads_route.methods
