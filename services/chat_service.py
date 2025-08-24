from repositories.user_repository import UserRepository
from repositories.chat_repository import ChatRepository
from services.llm_service import LLMService
from services.whatsapp_service import WhatsAppService
import os
from datetime import datetime
import re

class ChatService:
    def __init__(self):
        """Initialize chat service with dependencies"""
        self.user_repository = UserRepository()
        self.chat_repository = ChatRepository()
        self.llm_service = LLMService()
        self.whatsapp_service = WhatsAppService()
    
    def process_user_message(self, user_msg, phone):
        """Process user message and return AI response"""
        # Check if this is a new user (user doesn't exist in database)
        user = self.user_repository.get_user(phone)
        is_new_user = user is None
        
        # Flag to track if user is returning (sending a greeting to continue)
        is_returning_user = False
        
        if is_new_user:
            # New user - start with day 1
            day_number = 1
            self.user_repository.create_user(phone, day_number)
            prompt = self.llm_service.build_prompt(day_number, is_new_user=True)
        else:
            # Existing user
            # check if this is a regular message or if we should continue from last day
            last_day = user.day_number
                
            # If it's a regular conversation, use the message as is
            # If it looks like a restart or new session, remind them of their current day
            if user_msg.lower() in ["hi", "hello", "start", "restart", "continue"]:
                # User wants to continue their learning journey
                prompt = self.llm_service.build_prompt(last_day+1, is_returning_user=True)
                self.user_repository.set_last_day_number(phone, last_day+1)
            else:
                # Regular conversation within the current day
                prompt = user_msg
                
        # Get chat history
        chat_history = self.chat_repository.get_chat_history(phone)
        
        # Process with LLM
        response = self.llm_service.process_message(prompt, chat_history,
                                                   is_new_user=is_new_user,
                                                   is_returning_user=is_returning_user)
        
        # Save messages to database
        self.chat_repository.add_chat_message(phone, 'user', user_msg)
        self.chat_repository.add_chat_message(phone, 'model', response)
        
        return response
    
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
                    prompt = self.llm_service.build_prompt(day_number, is_returning_user=True)
                    if not prompt:
                        print(f"Invalid day number {day_number} for user {user_record.phone}")
                        continue
                    
                    # Send the prompt via WhatsApp
                    print(f"Sending nudge to user {original_phone} for day {day_number}")
                    print(f"Message: {prompt[:100]}...")  # Show first 100 chars
                    
                    # Send WhatsApp message via WhatsApp Cloud API
                    success, result = self.whatsapp_service.send_message(original_phone, prompt)
                    
                    if success:
                        print(f"Message sent successfully. Result: {result}")
                    else:
                        print(f"Failed to send message: {result}")
                    
                except Exception as e:
                    print(f"Error sending nudge to user {user_record.phone}: {str(e)}")
                    continue
                    
            print(f"Daily nudge job completed at {datetime.now()}")
            
        except Exception as e:
            print(f"Error in daily nudge job: {str(e)}") 
    
    def parse_day_command(self, user_msg):
        """Parse day command from user message"""
        user_msg = user_msg.strip().lower()
        if match := re.match(r"(?i)^day\s*(\d+)$", user_msg):
            day_number = int(match.group(1))
            if 1 <= day_number <= 30:
                return day_number
            else:
                return None
        else:
            return None