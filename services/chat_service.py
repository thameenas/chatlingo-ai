from repositories.user_repository import UserRepository
from repositories.chat_repository import ChatRepository
from services.llm_service import LLMService
from twilio.rest import Client
import os
from datetime import datetime

class ChatService:
    def __init__(self):
        """Initialize chat service with dependencies"""
        self.user_repository = UserRepository()
        self.chat_repository = ChatRepository()
        self.llm_service = LLMService()
        self.twilio_client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
        self.twilio_phone_number = os.getenv("TWILIO_PHONE_NUMBER")
    
    def process_user_message(self, user_msg, phone):
        """Process user message and return AI response"""
        # Parse day command if present
        day_number = self.llm_service.parse_day_command(user_msg)
        
        if day_number:
            # User wants to start a specific day
            self.user_repository.set_last_day_number(phone, day_number)
            prompt = self.llm_service.build_prompt(day_number)
        else:
            # Regular message, use as is
            prompt = user_msg
        
        # Get chat history
        chat_history = self.chat_repository.get_chat_history(phone)
        
        # Process with LLM
        response = self.llm_service.process_message(prompt, chat_history)
        
        # Save messages to database
        self.chat_repository.add_chat_message(phone, 'user', prompt)
        self.chat_repository.add_chat_message(phone, 'model', response)
        
        return response
    
    def reset_chat_history(self, phone):
        """Reset chat history for a user"""
        self.chat_repository.clear_chat_history(phone)
    
    def get_user_progress(self, phone):
        """Get user's current day number"""
        return self.user_repository.get_last_day_number(phone)
    
    def send_daily_nudges(self):
        """Send daily nudges to all users"""
        try:
            print(f"Starting daily nudge job at {datetime.now()}")
            
            # Get all users
            users = self.user_repository.get_all_users()
            print(f"Found {len(users)} users to send nudges to")
            
            for user_record in users:
                try:
                    # Get user's current day number and original phone
                    day_number = user_record.day_number
                    original_phone = user_record.original_phone
                    
                    # Generate the first prompt for this day
                    prompt = self.llm_service.build_prompt(day_number)
                    if not prompt:
                        print(f"Invalid day number {day_number} for user {user_record.phone}")
                        continue
                    
                    # Send the prompt via WhatsApp
                    print(f"Sending nudge to user {original_phone} for day {day_number}")
                    print(f"Message: {prompt[:100]}...")  # Show first 100 chars
                    
                    # Send WhatsApp message via Twilio
                    message = self.twilio_client.messages.create(
                        body=prompt,
                        from_=f"whatsapp:{self.twilio_phone_number}",
                        to=f"whatsapp:{original_phone}"
                    )
                    
                    print(f"Message sent successfully. SID: {message.sid}")
                    
                except Exception as e:
                    print(f"Error sending nudge to user {user_record.phone}: {str(e)}")
                    continue
                    
            print(f"Daily nudge job completed at {datetime.now()}")
            
        except Exception as e:
            print(f"Error in daily nudge job: {str(e)}") 