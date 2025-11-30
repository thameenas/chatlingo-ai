"""
Message Processor for Chatlingo AI

Core business logic that orchestrates the flow between WhatsApp, Database, and LLM.
"""

import logging
from typing import Optional, Dict, Any
from app.schemas.whatsapp import WhatsAppWebhook, WhatsAppMessage
from app.services.whatsapp_service import whatsapp_service
from app.services.llm_service import llm_service
from app.services import db_service

logger = logging.getLogger(__name__)

# Menu Buttons
MENU_BUTTONS = [
    {"id": "roleplay_start", "title": "🎭 Roleplay"},
    {"id": "sos_helper", "title": "🚑 SOS Helper"},
    {"id": "random_chat", "title": "☕ Random Chat"}
]

class MessageProcessor:
    """Core logic for processing incoming WhatsApp messages"""
    
    async def process_webhook(self, payload: WhatsAppWebhook):
        """
        Entry point for processing a webhook payload.
        """
        try:
            # Extract the first entry and change
            if not payload.entry or not payload.entry[0].changes:
                return
                
            change = payload.entry[0].changes[0]
            value = change.value
            
            # Check if it's a message
            if not value.messages or not value.messages[0]:
                return
                
            message = value.messages[0]
            phone_number = message.from_
            
            # 1. Mark message as read immediately (UX)
            await whatsapp_service.mark_message_as_read(message.id)
            
            # 2. Get or create user in DB
            user = db_service.get_or_create_user(phone_number)
            
            # 3. Handle different message types
            if message.type == "text":
                await self._handle_text_message(user, message.text.body)
            elif message.type == "interactive":
                await self._handle_interactive_message(user, message.interactive)
                
        except Exception as e:
            logger.error(f"Error processing webhook: {str(e)}")

    async def _handle_text_message(self, user: Any, text: str):
        """Handle incoming text messages based on user state"""
        phone = user.phone_number
        mode = user.current_mode
        
        # Save user message to history
        db_service.add_message(phone, "user", text)
        
        # Global commands
        if text.lower() in ["menu", "hi", "hello", "start", "restart"]:
            await self._send_main_menu(phone)
            return

        # Handle based on mode
        if mode == "menu":
            # If in menu mode but types text, treat as general chat or re-show menu
            # For now, let's just show the menu again to guide them
            await self._send_main_menu(phone)
            
        elif mode == "roleplay":
            await self._handle_roleplay_flow(user, text)
            
        elif mode == "random_chat":
            await self._handle_chat_flow(user, text)
            
        else:
            # Fallback to main menu
            await self._send_main_menu(phone)

    async def _handle_interactive_message(self, user: Any, interactive: Any):
        """Handle button clicks"""
        phone = user.phone_number
        button_id = interactive.button_reply.id
        
        if button_id == "roleplay_start":
            # Switch to roleplay mode
            # For MVP, let's pick the first scenario automatically or list them
            # Let's list scenarios (simplified for now: just start Scenario 1)
            scenario = db_service.get_scenario_by_id(1)
            if scenario:
                db_service.update_user_mode(phone, "roleplay", scenario_id=1)
                
                # Send opening line
                await whatsapp_service.send_text_message(phone, f"*{scenario.title}*\n\n{scenario.opening_line}")
                db_service.add_message(phone, "bot", scenario.opening_line)
            else:
                await whatsapp_service.send_text_message(phone, "No scenarios found. Please contact admin.")
                
        elif button_id == "random_chat":
            db_service.update_user_mode(phone, "random_chat")
            await whatsapp_service.send_text_message(phone, "Banni! Let's have a cup of coffee and chat. What's on your mind?")
            
        elif button_id == "sos_helper":
            await whatsapp_service.send_text_message(phone, "🚑 SOS Helper coming soon! (This feature is under construction)")
            await self._send_main_menu(phone)

    async def _send_main_menu(self, phone: str):
        """Send the main menu with buttons"""
        # Reset mode to menu
        db_service.update_user_mode(phone, "menu")
        
        await whatsapp_service.send_interactive_buttons(
            phone,
            "Namaskara! 🙏 Welcome to Chatlingo. How would you like to learn Kannada today?",
            MENU_BUTTONS
        )

    async def _handle_roleplay_flow(self, user: Any, text: str):
        """Handle conversation in roleplay mode"""
        phone = user.phone_number
        scenario_id = user.current_scenario_id
        
        scenario = db_service.get_scenario_by_id(scenario_id)
        if not scenario:
            await self._send_main_menu(phone)
            return

        # Get history
        history_objs = db_service.get_recent_messages(phone, limit=10)
        history = [{"role": msg.role, "content": msg.content} for msg in history_objs]
        
        # Generate response
        response_text = await llm_service.get_roleplay_response(history, scenario.model_dump())
        
        # Send and save
        await whatsapp_service.send_text_message(phone, response_text)
        db_service.add_message(phone, "bot", response_text)

    async def _handle_chat_flow(self, user: Any, text: str):
        """Handle conversation in random chat mode"""
        phone = user.phone_number
        
        # Get history
        history_objs = db_service.get_recent_messages(phone, limit=10)
        history = [{"role": msg.role, "content": msg.content} for msg in history_objs]
        
        # Generate response
        response_text = await llm_service.get_chat_response(history)
        
        # Send and save
        await whatsapp_service.send_text_message(phone, response_text)
        db_service.add_message(phone, "bot", response_text)

# Global instance
message_processor = MessageProcessor()