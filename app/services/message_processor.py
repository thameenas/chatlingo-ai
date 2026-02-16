"""
Message Processor for Chatlingo AI

Handles webhook processing and message routing for both WhatsApp and Telegram.
Includes conversation logic (scenarios, chat flows).
"""

import logging
import traceback
import uuid
from typing import Any
from app.schemas.whatsapp import WhatsAppWebhook
from app.schemas.telegram import TelegramUpdate
from app.services.whatsapp_service import whatsapp_service
from app.services.telegram_service import telegram_service
from app.services.platform_adapter import get_platform_adapter
from app.services.llm_service import llm_service
from app.services import supabase_service

logger = logging.getLogger(__name__)

# Menu Buttons
MENU_BUTTONS = [
    {"id": "practice_scenario_start", "title": "🎭 Practice Scenarios"},
    {"id": "sos_helper", "title": "🚑 SOS Helper"},
    {"id": "random_chat", "title": "☕ Random Chat"}
]

class MessageProcessor:
    """Core logic for processing incoming messages from WhatsApp and Telegram"""
    
    @staticmethod
    async def process_telegram_update(update: TelegramUpdate):
        """Process incoming Telegram update"""
        try:
            # Handle regular message
            if update.message:
                message = update.message
                user_id = str(message.chat.id)
                logger.info(f"Telegram message from {user_id}: {message.text}")
                
                user = supabase_service.get_or_create_user(user_id)
                platform = get_platform_adapter("telegram", telegram_service)
                
                if message.text:
                    await MessageProcessor._handle_text_message(user, message.text, platform)
                    
            # Handle callback query (button press)
            elif update.callback_query:
                callback = update.callback_query
                user_id = str(callback.message.chat.id) if callback.message else str(callback.from_.id)
                
                await telegram_service.answer_callback_query(callback.id)
                user = supabase_service.get_or_create_user(user_id)
                platform = get_platform_adapter("telegram", telegram_service)
                
                await MessageProcessor._handle_button_callback(user, callback.data, platform)
        
        except Exception as e:
            logger.error(f"Error processing Telegram update: {e}\n{traceback.format_exc()}")
    
    async def process_webhook(self, payload: WhatsAppWebhook):
        """Entry point for processing a WhatsApp webhook payload"""
        try:
            if not payload.entry or not payload.entry[0].changes:
                return
                
            change = payload.entry[0].changes[0]
            value = change.value
            
            if not value.messages or not value.messages[0]:
                return
                
            message = value.messages[0]
            phone_number = message.from_
            logger.info(f"WhatsApp message from {phone_number}: type={message.type}")
            
            # Mark message as read
            await whatsapp_service.mark_message_as_read(message.id)
            
            # Get/create user
            user = supabase_service.get_or_create_user(phone_number)
            platform = get_platform_adapter("whatsapp", whatsapp_service)
            
            # Handle different message types
            if message.type == "text":
                await self._handle_text_message(user, message.text.body, platform)
            elif message.type == "interactive":
                await self._handle_interactive_message(user, message.interactive, platform)
                
        except Exception as e:
            logger.error(f"Error processing webhook: {e}\n{traceback.format_exc()}")

    @staticmethod
    async def _handle_text_message(user: Any, text: str, platform: Any):
        """Handle incoming text messages based on user state"""
        user_id = user.phone_number
        mode = user.current_mode
        
        # Save user message
        session_id = getattr(user, 'current_session_id', None)
        scenario_id = getattr(user, 'current_scenario_id', None)
        supabase_service.add_message(user_id, "user", text, mode=mode, session_id=session_id, scenario_id=scenario_id)
        
        # Global commands (including /start for Telegram)
        if text.lower() in ["menu", "hi", "hello", "start", "restart", "/start"]:
            await MessageProcessor._send_main_menu(user_id, platform)
            return

        # Handle based on current mode
        if mode == "menu":
            await MessageProcessor._send_main_menu(user_id, platform)
            
        elif mode == "practice_scenario":
            await MessageProcessor._handle_practice_scenario_flow(user, text, platform)
            
        elif mode == "random_chat":
            await MessageProcessor._handle_chat_flow(user, text, platform)
            
        else:
            await MessageProcessor._send_main_menu(user_id, platform)

    async def _handle_interactive_message(self, user: Any, interactive: Any, platform: Any):
        """Handle WhatsApp button clicks and list selections"""
        # Handle Button Replies
        if interactive.type == "button_reply":
            await self._handle_button_callback(user, interactive.button_reply.id, platform)

        # Handle List Replies
        elif interactive.type == "list_reply":
            await self._handle_button_callback(user, interactive.list_reply.id, platform)

    @staticmethod
    async def _handle_button_callback(user: Any, button_id: str, platform: Any):
        """Handle button/callback actions"""
        user_id = user.phone_number
        
        if button_id == "practice_scenario_start":
            scenarios = supabase_service.get_all_scenarios()
            
            if not scenarios:
                await platform.send_text(user_id, "No scenarios found. Please contact admin.")
                return

            # Create list items
            items = [
                {
                    "id": f"scenario_{s.id}",
                    "title": s.title[:24],
                    "description": s.bot_persona[:72] if len(s.bot_persona) <= 72 else s.bot_persona[:69] + "..."
                }
                for s in scenarios
            ]
            
            await platform.send_menu_list(user_id, "Choose a scenario to practice:", "Select Scenario", items)
            
        elif button_id == "random_chat":
            await MessageProcessor._start_random_chat(user_id, platform)
            
        elif button_id == "sos_helper":
            await platform.send_text(user_id, "🚑 SOS Helper coming soon! (This feature is under construction)")
            await MessageProcessor._send_main_menu(user_id, platform)
            
        elif button_id.startswith("scenario_"):
            try:
                scenario_id = int(button_id.split("_")[1])
                await MessageProcessor._start_scenario(user_id, scenario_id, platform)
            except ValueError:
                logger.error(f"Invalid scenario ID: {button_id}")
                await MessageProcessor._send_main_menu(user_id, platform)

    @staticmethod
    async def _start_random_chat(user_id: str, platform: Any):
        """Start random chat mode"""
        supabase_service.update_user_mode(user_id, "random_chat")
        
        # Generate opening using LLM
        response_text = await llm_service.get_chat_response([])
        
        await platform.send_text(user_id, response_text)
        supabase_service.add_message(user_id, "assistant", response_text, mode="random_chat")

    @staticmethod
    async def _start_scenario(user_id: str, scenario_id: int, platform: Any):
        """Start a specific practice scenario"""
        scenario = supabase_service.get_scenario_by_id(scenario_id)
        if not scenario:
            await platform.send_text(user_id, "Scenario not found.")
            await MessageProcessor._send_main_menu(user_id, platform)
            return
            
        # Create session and update user state
        session_id = str(uuid.uuid4())
        supabase_service.update_user_mode(user_id, "practice_scenario", scenario_id=scenario_id, session_id=session_id)
        
        # Generate opening via LLM
        response_text = await llm_service.get_practice_scenario_response([], scenario.model_dump())
        supabase_service.add_message(user_id, "assistant", response_text, mode="practice_scenario", 
                                    session_id=session_id, scenario_id=scenario_id)
        
        # Send opening line with scenario title
        await platform.send_text(user_id, f"*{scenario.title}*\n\n{response_text}")

    @staticmethod
    async def _send_main_menu(user_id: str, platform: Any):
        """Send the main menu with buttons"""
        supabase_service.update_user_mode(user_id, "menu")
        
        await platform.send_menu_buttons(
            user_id,
            "Namaskara! 🙏 Welcome to Chatlingo. How would you like to learn Kannada today?",
            MENU_BUTTONS
        )

    @staticmethod
    async def _handle_practice_scenario_flow(user: Any, text: str, platform: Any):
        """Handle conversation in practice scenario mode"""
        user_id = user.phone_number
        
        # Check for exit commands
        if text.lower().strip() in ["exit", "quit", "stop", "menu", "end"]:
            await platform.send_text(user_id, "Ending practice session. Great job!")
            await MessageProcessor._send_main_menu(user_id, platform)
            return

        scenario_id = user.current_scenario_id
        session_id = getattr(user, 'current_session_id', None)
        
        scenario = supabase_service.get_scenario_by_id(scenario_id)
        if not scenario:
            await MessageProcessor._send_main_menu(user_id, platform)
            return

        # Get conversation history and generate response
        history_objs = supabase_service.get_recent_messages(user_id, limit=50, session_id=session_id)
        history = [{"role": msg.role, "content": msg.content} for msg in history_objs]
        
        response_text = await llm_service.get_practice_scenario_response(history, scenario.model_dump())
        
        # Save and send response
        supabase_service.add_message(user_id, "assistant", response_text, mode="practice_scenario",
                                    session_id=session_id, scenario_id=scenario_id)
        await platform.send_text(user_id, response_text)

    @staticmethod
    async def _handle_chat_flow(user: Any, text: str, platform: Any):
        """Handle conversation in random chat mode"""
        user_id = user.phone_number
        
        # Get history and generate response
        history_objs = supabase_service.get_recent_messages(user_id, limit=50)
        history = [{"role": msg.role, "content": msg.content} for msg in history_objs]
        
        response_text = await llm_service.get_chat_response(history)
        
        # Send and save
        await platform.send_text(user_id, response_text)
        supabase_service.add_message(user_id, "assistant", response_text, mode="random_chat")

# Global instance
message_processor = MessageProcessor()
