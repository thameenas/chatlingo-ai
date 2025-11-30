"""
Message Processor for Chatlingo AI

Core business logic that orchestrates the flow between WhatsApp, Database, and LLM.
"""

import logging
import uuid
from typing import Optional, Dict, Any
from app.schemas.whatsapp import WhatsAppWebhook, WhatsAppMessage
from app.services.whatsapp_service import whatsapp_service
from app.services.llm_service import llm_service
from app.services import db_service

logger = logging.getLogger(__name__)

# Menu Buttons
MENU_BUTTONS = [
    {"id": "practice_scenario_start", "title": "🎭 Practice Scenarios"},
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
        # Note: For roleplay, we should ideally pass session_id, but user object might not have it updated in memory if we just switched?
        # Actually, user object is fetched fresh at start of process_webhook.
        session_id = getattr(user, 'current_session_id', None)
        scenario_id = getattr(user, 'current_scenario_id', None)
        db_service.add_message(phone, "user", text, mode=mode, session_id=session_id, scenario_id=scenario_id)
        
        # Global commands
        if text.lower() in ["menu", "hi", "hello", "start", "restart"]:
            await self._send_main_menu(phone)
            return

        # Handle based on current mode
        if mode == "menu":
            await self._send_main_menu(phone)
            
        elif mode == "practice_scenario":
            await self._handle_practice_scenario_flow(user, text)
            
        elif mode == "random_chat":
            await self._handle_chat_flow(user, text)
            
        else:
            # Fallback to main menu
            await self._send_main_menu(phone)

    async def _handle_interactive_message(self, user: Any, interactive: Any):
        """Handle button clicks and list selections"""
        phone = user.phone_number
        
        # Handle Button Replies
        if interactive.type == "button_reply":
            button_id = interactive.button_reply.id
            
            if button_id == "practice_scenario_start":
                # Fetch all scenarios
                scenarios = db_service.get_all_scenarios()
                
                if not scenarios:
                    await whatsapp_service.send_text_message(phone, "No scenarios found. Please contact admin.")
                    return

                # Create list sections
                rows = []
                for scenario in scenarios:
                    rows.append({
                        "id": f"scenario_{scenario.id}",
                        "title": scenario.title[:24], # WhatsApp limit 24 chars
                    })
                
                sections = [{
                    "title": "Available Scenarios",
                    "rows": rows
                }]
                
                await whatsapp_service.send_interactive_list_message(
                    phone,
                    "Choose a scenario to practice:",
                    "Select Scenario",
                    sections
                )
                
            elif button_id == "random_chat":
                await self._handle_random_chat_start(phone)
                
            elif button_id == "sos_helper":
                await whatsapp_service.send_text_message(phone, "🚑 SOS Helper coming soon! (This feature is under construction)")
                await self._send_main_menu(phone)

        # Handle List Replies
        elif interactive.type == "list_reply":
            selection_id = interactive.list_reply.id
            
            if selection_id.startswith("scenario_"):
                try:
                    scenario_id = int(selection_id.split("_")[1])
                    await self._start_scenario(phone, scenario_id)
                except ValueError:
                    logger.error(f"Invalid scenario ID format: {selection_id}")
                    await self._send_main_menu(phone)

    async def _handle_random_chat_start(self, phone: str):
        """Start random chat mode"""
        db_service.update_user_mode(phone, "random_chat")
        await whatsapp_service.send_text_message(phone, "Banni! Let's have a cup of coffee and chat. What's on your mind?")

    async def _start_scenario(self, phone: str, scenario_id: int):
        """Start a specific practice scenario"""
        scenario = db_service.get_scenario_by_id(scenario_id)
        if scenario:
            # Generate new session ID
            session_id = str(uuid.uuid4())
            
            db_service.update_user_mode(phone, "practice_scenario", scenario_id=scenario_id, session_id=session_id)
            
            # Send opening line
            await whatsapp_service.send_text_message(phone, f"*{scenario.title}*\n\n{scenario.opening_line}")
            db_service.add_message(phone, "assistant", scenario.opening_line, mode="practice_scenario", session_id=session_id, scenario_id=scenario_id)
        else:
            await whatsapp_service.send_text_message(phone, "Scenario not found.")
            await self._send_main_menu(phone)

    async def _send_main_menu(self, phone: str):
        """Send the main menu with buttons"""
        # Reset mode to menu
        # Todo: Consider if we want this user state change
        db_service.update_user_mode(phone, "menu")
        
        await whatsapp_service.send_interactive_buttons(
            phone,
            "Namaskara! 🙏 Welcome to Chatlingo. How would you like to learn Kannada today?",
            MENU_BUTTONS
        )

    async def _handle_practice_scenario_flow(self, user: Any, text: str):
        """Handle conversation in practice scenario mode"""
        phone = user.phone_number
        
        # Check for exit commands
        if text.lower().strip() in ["exit", "quit", "stop", "menu", "end"]:
            await whatsapp_service.send_text_message(phone, "Ending practice session. Great job!")
            await self._send_main_menu(phone)
            return

        scenario_id = user.current_scenario_id
        
        scenario = db_service.get_scenario_by_id(scenario_id)
        if not scenario:
            await self._send_main_menu(phone)
            return

        # Get history filtered by current session
        session_id = getattr(user, 'current_session_id', None)
        history_objs = db_service.get_recent_messages(phone, limit=50, session_id=session_id)
        history = [{"role": msg.role, "content": msg.content} for msg in history_objs]
        
        # Generate response
        response_text = await llm_service.get_practice_scenario_response(history, scenario.model_dump())
        
        # Send and save
        await whatsapp_service.send_text_message(phone, response_text)
        db_service.add_message(phone, "assistant", response_text, mode="practice_scenario", session_id=session_id, scenario_id=scenario_id)

    async def _handle_chat_flow(self, user: Any, text: str):
        """Handle conversation in random chat mode"""
        phone = user.phone_number
        
        # Get history
        history_objs = db_service.get_recent_messages(phone, limit=50)
        history = [{"role": msg.role, "content": msg.content} for msg in history_objs]
        
        # Generate response
        response_text = await llm_service.get_chat_response(history)
        
        # Send and save
        await whatsapp_service.send_text_message(phone, response_text)
        db_service.add_message(phone, "assistant", response_text, mode="random_chat")

# Global instance
message_processor = MessageProcessor()