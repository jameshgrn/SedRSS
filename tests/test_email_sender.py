import pytest
from components.email_sender import EmailSender
from datetime import datetime
import smtplib
from unittest.mock import MagicMock, patch

@pytest.fixture
def smtp_config():
    """Create test SMTP configuration"""
    return {
        'host': 'test.smtp.com',
        'port': '587',
        'username': 'test@example.com',
        'password': 'test_password'
    }

@pytest.fixture
def email_sender(smtp_config):
    """Create test email sender instance"""
    return EmailSender(smtp_config)

@pytest.fixture
def sample_content():
    """Create sample newsletter content"""
    return {
        'featured_articles': [
            {
                'title': 'Featured Article 1',
                'url': 'http://example.com/1',
                'journal': 'Nature',
                'summary': 'Test summary 1'
            }
        ],
        'other_articles': [
            {
                'title': 'Other Article 1',
                'url': 'http://example.com/2',
                'journal': 'Science'
            }
        ]
    }

@pytest.mark.asyncio
async def test_email_sending(email_sender, sample_content):
    """Test email sending with mocked SMTP"""
    mock_smtp = MagicMock()
    
    with patch('smtplib.SMTP') as mock_smtp_class:
        mock_smtp_class.return_value.__enter__.return_value = mock_smtp
        
        await email_sender.send(
            subject='Test Newsletter',
            content=sample_content,
            recipients=['test@example.com']
        )
        
        # Verify SMTP interactions
        mock_smtp_class.assert_called_once_with('test.smtp.com', 587)
        mock_smtp.starttls.assert_called_once()
        mock_smtp.login.assert_called_once_with('test@example.com', 'test_password')
        mock_smtp.send_message.assert_called_once()

@pytest.mark.asyncio
async def test_email_content_rendering(email_sender, sample_content):
    """Test email content rendering"""
    with patch('smtplib.SMTP') as mock_smtp_class:
        await email_sender.send(
            subject='Test Newsletter',
            content=sample_content,
            recipients=['test@example.com']
        )
        
        # Get the message that would have been sent
        mock_smtp_instance = mock_smtp_class.return_value.__enter__.return_value
        sent_message = mock_smtp_instance.send_message.call_args[0][0]
        
        # Check email structure
        assert sent_message['Subject'] == 'Test Newsletter'
        assert sent_message['From'] == 'test@example.com'
        assert sent_message['To'] == 'test@example.com'
        
        # Check content
        html_content = sent_message.get_payload()[0].get_payload()
        assert 'Featured Article 1' in html_content
        assert 'Other Article 1' in html_content
        assert 'Nature' in html_content
        assert 'Science' in html_content
        assert datetime.now().strftime('%B') in html_content

@pytest.mark.asyncio
async def test_email_sending_error(email_sender, sample_content):
    """Test email sending error handling"""
    with patch('smtplib.SMTP') as mock_smtp_class:
        mock_smtp_class.side_effect = smtplib.SMTPException('Test error')
        
        with pytest.raises(smtplib.SMTPException):
            await email_sender.send(
                subject='Test Newsletter',
                content=sample_content,
                recipients=['test@example.com']
            ) 