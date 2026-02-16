"""
Message Processor for Chatlingo AI

Multi-platform transport layer - handles webhook processing and message routing
for both WhatsApp and Telegram. Uses ConversationEngine for core conversation logic.
"""

import logging
import traceback
from typing import Any
from app.schemas.whatsapp import WhatsAppWebhook
from app.schemas.telegram import TelegramUpdate
from app.services.whatsapp_service import whatsapp_service
from app.services.telegram_service import telegram_service
from app.services.platform_adapter import get_platform_adapter, MessagingPlatform
from app.services.llm_service import llm_service
from app.services import supabase_service
from app.services.conversation_engine import conversation_engine

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
        """
        Process incoming Telegram update.
        
        Args:
            update: TelegramUpdate object from webhook
        """
        logger.info(f"[PROCESSOR] 🔄 process_telegram_update called: update_id={update.update_id}")
        try:
            # Handle regular message
            if update.message:
                message = update.message
                user_id = str(message.chat.id)
                logger.info(f"[PROCESSOR] 📨 Telegram message: chat_id={user_id}, text={message.text}")
                
                # Get or create user (Telegram chat_id stored as phone_number)
                user = supabase_service.get_or_create_user(user_id)
                logger.info(f"[PROCESSOR] 👤 User state: mode={user.current_mode}")
                
                # Get platform adapter
                platform = get_platform_adapter("telegram", telegram_service)
                
                # Handle text message
                if message.text:
                    await MessageProcessor._handle_text_message_generic(
                        user, message.text, platform
                    )
                    
            # Handle callback query (button press)
            elif update.callback_query:
                callback = update.callback_query
                user_id = str(callback.message.chat.id) if callback.message else str(callback.from_.id)
                logger.info(f"[PROCESSOR] 🔘 Telegram callback: data={callback.data}")
                
                # Answer callback query immediately
                await telegram_service.answer_callback_query(callback.id)
                
                # Get user and platform
                user = supabase_service.get_or_create_user(user_id)
                platform = get_platform_adapter("telegram", telegram_service)
                
                # Handle callback as button press
                await MessageProcessor._handle_button_callback_generic(
                    user, callback.data, platform
                )
        
        except Exception as e:
            logger.error(f"[PROCESSOR] ❌ Error processing Telegram update: {str(e)}")
            logger.error(f"[PROCESSOR] ❌ Traceback:\n{traceback.format_exc()}")
    
    async def process_webhook(self, payload: WhatsAppWebhook):
        """
        Entry point for processing a WhatsApp webhook payload.
        """
        logger.info("[PROCESSOR] 🔄 process_webhook called")
        try:
            # Extract the first entry and change
            if not payload.entry or not payload.entry[0].changes:
                logger.info("[PROCESSOR] ⏭️ No entry or changes in payload, skipping")
                return
                
            change = payload.entry[0].changes[0]
            value = change.value
            
            # Check if it's a message
            if not value.messages or not value.messages[0]:
                logger.info("[PROCESSOR] ⏭️ No messages in payload (likely a status update), skipping")
                return
                
            message = value.messages[0]
            phone_number = message.from_
            logger.info(f"[PROCESSOR] 📨 Message received: type={message.type}, from={phone_number}, id={message.id}")
            
            if message.type == "text" and message.text:
                logger.info(f"[PROCESSOR] 📝 Text content: '{message.text.body}'")
            elif message.type == "interactive" and message.interactive:
                logger.info(f"[PROCESSOR] 🔘 Interactive type: {message.interactive.type}")
            
            # 1. Mark message as read immediately (UX)
            logger.info(f"[PROCESSOR] 👁️ Marking message {message.id} as read")
            await whatsapp_service.mark_message_as_read(message.id)
            
            # 2. Get or create user in DB
            logger.info(f"[PROCESSOR] 👤 Getting/creating user for {phone_number}")
            user = supabase_service.get_or_create_user(phone_number)
            logger.info(f"[PROCESSOR] 👤 User state: mode={user.current_mode}, scenario_id={user.current_scenario_id}, session_id={user.current_session_id}")
            
            # Get platform adapter
            platform = get_platform_adapter("whatsapp", whatsapp_service)
            
            # 3. Handle different message types
            if message.type == "text":
                logger.info(f"[PROCESSOR] ➡️ Routing to _handle_text_message_generic")
                await self._handle_text_message_generic(user, message.text.body, platform)
            elif message.type == "interactive":
                logger.info(f"[PROCESSOR] ➡️ Routing to _handle_interactive_message")
                await self._handle_interactive_message(user, message.interactive, platform)
            else:
                logger.warning(f"[PROCESSOR] ⚠️ Unhandled message type: {message.type}")
                
        except Exception as e:
            logger.error(f"[PROCESSOR] ❌ Error processing webhook: {str(e)}")
            logger.error(f"[PROCESSOR] ❌ Traceback:\n{traceback.format_exc()}")

    @staticmethod
    async def _handle_text_message_generic(user: Any, text: str, platform: MessagingPlatform):
        """Handle incoming text messages based on user state (platform-agnostic)"""
        user_id = user.phone_number
        mode = user.current_mode
        logger.info(f"[PROCESSOR] _handle_text_message_generic: user_id={user_id}, mode={mode}, text='{text}'")
        
        # Save user message to history
        session_id = getattr(user, 'current_session_id', None)
        scenario_id = getattr(user, 'current_scenario_id', None)
        logger.info(f"[PROCESSOR] Saving user message: session_id={session_id}, scenario_id={scenario_id}")
        supabase_service.add_message(user_id, "user", text, mode=mode, session_id=session_id, scenario_id=scenario_id)
        
        # Global commands (including /start for Telegram)
        if text.lower() in ["menu", "hi", "hello", "start", "restart", "/start"]:
            logger.info(f"[PROCESSOR] Global command detected: '{text.lower()}' → sending main menu")
            await MessageProcessor._send_main_menu_generic(user_id, platform)
            return

        # Handle based on current mode
        if mode == "menu":
            logger.info(f"[PROCESSOR] Mode is 'menu' → sending main menu")
            await MessageProcessor._send_main_menu_generic(user_id, platform)
            
        elif mode == "practice_scenario":
            logger.info(f"[PROCESSOR] Mode is 'practice_scenario' → routing to scenario flow")
            await MessageProcessor._handle_practice_scenario_flow_generic(user, text, platform)
            
        elif mode == "random_chat":
            logger.info(f"[PROCESSOR] Mode is 'random_chat' → routing to chat flow")
            await MessageProcessor._handle_chat_flow_generic(user, text, platform)
            
        else:
            logger.warning(f"[PROCESSOR] ⚠️ Unknown mode '{mode}' → fallback to main menu")
            await MessageProcessor._send_main_menu_generic(user_id, platform)

    async def _handle_interactive_message(self, user: Any, interactive: Any, platform: MessagingPlatform):
        """Handle WhatsApp button clicks and list selections"""
        user_id = user.phone_number
        logger.info(f"[PROCESSOR] _handle_interactive_message: user_id={user_id}, interactive_type={interactive.type}")
        
        # Handle Button Replies
        if interactive.type == "button_reply":
            button_id = interactive.button_reply.id
            logger.info(f"[PROCESSOR] Button reply: id='{button_id}', title='{interactive.button_reply.title}'")
            await self._handle_button_callback_generic(user, button_id, platform)

        # Handle List Replies
        elif interactive.type == "list_reply":
            selection_id = interactive.list_reply.id
            logger.info(f"[PROCESSOR] List reply: id='{selection_id}', title='{interactive.list_reply.title}'")
            await self._handle_button_callback_generic(user, selection_id, platform)
        else:
            logger.warning(f"[PROCESSOR] ⚠️ Unknown interactive type: '{interactive.type}'")

    @staticmethod
    async def _handle_button_callback_generic(user: Any, button_id: str, platform: MessagingPlatform):
        """Handle button/callback actions (platform-agnostic)"""
        user_id = user.phone_number
        logger.info(f"[PROCESSOR] _handle_button_callback_generic: button_id={button_id}")
        
        if button_id == "practice_scenario_start":
            # Fetch all scenarios
            scenarios = supabase_service.get_all_scenarios()
            
            logger.info(f"[PROCESSOR] Fetched {len(scenarios)} scenarios")
            if not scenarios:
                logger.warning("[PROCESSOR] ⚠️ No scenarios found in DB")
                await platform.send_text(user_id, "No scenarios found. Please contact admin.")
                return

            # Create list items
            items = []
            for scenario in scenarios:
                items.append({
                    "id": f"scenario_{scenario.id}",
                    "title": scenario.title[:24],  # Limit for WhatsApp compatibility
                    "description": scenario.bot_persona[:72] if len(scenario.bot_persona) <= 72 else scenario.bot_persona[:69] + "..."
                })
            
            await platform.send_menu_list(
                user_id,
                "Choose a scenario to practice:",
                "Select Scenario",
                items
            )
            
        elif button_id == "random_chat":
            logger.info("[PROCESSOR] Starting random chat")
            await MessageProcessor._handle_random_chat_start_generic(user_id, platform)
            
        elif button_id == "sos_helper":
            logger.info("[PROCESSOR] SOS Helper selected (not implemented)")
            await platform.send_text(user_id, "🚑 SOS Helper coming soon! (This feature is under construction)")
            await MessageProcessor._send_main_menu_generic(user_id, platform)
            
        elif button_id.startswith("scenario_"):
            try:
                scenario_id = int(button_id.split("_")[1])
                logger.info(f"[PROCESSOR] Starting scenario {scenario_id}")
                await MessageProcessor._start_scenario_generic(user_id, scenario_id, platform)
            except ValueError:
                logger.error(f"[PROCESSOR] ❌ Invalid scenario ID format: {button_id}")
                await MessageProcessor._send_main_menu_generic(user_id, platform)
        else:
            logger.warning(f"[PROCESSOR] ⚠️ Unknown button_id: '{button_id}'")

    @staticmethod
    async def _handle_random_chat_start_generic(user_id: str, platform: MessagingPlatform):
        """Start random chat mode (platform-agnostic)"""
        logger.info(f"[PROCESSOR] _handle_random_chat_start_generic: user_id={user_id}")
        supabase_service.update_user_mode(user_id, "random_chat")
        
        # Generate dynamic opening using LLM instead of static text
        history = []  # Empty history for start
        logger.info("[PROCESSOR] Calling LLM for random chat opening...")
        response_text = await llm_service.get_chat_response(history)
        logger.info(f"[PROCESSOR] LLM response (first 100): '{response_text[:100]}...'")
        
        await platform.send_text(user_id, response_text)
        supabase_service.add_message(user_id, "assistant", response_text, mode="random_chat")

    @staticmethod
    async def _start_scenario_generic(user_id: str, scenario_id: int, platform: MessagingPlatform):
        """Start a specific practice scenario (platform-agnostic)"""
        logger.info(f"[PROCESSOR] _start_scenario_generic: user_id={user_id}, scenario_id={scenario_id}")
        scenario = conversation_engine.get_scenario(scenario_id)
        if scenario:
            logger.info(f"[PROCESSOR] Scenario found: '{scenario.title}'")
            # Start scenario session via engine
            session_id = conversation_engine.start_scenario(user_id, scenario_id)
            logger.info(f"[PROCESSOR] Session created: {session_id}")
            
            # Generate opening via engine
            logger.info("[PROCESSOR] Generating scenario opening via LLM...")
            response_text = await conversation_engine.generate_opening(user_id, scenario, session_id)
            logger.info(f"[PROCESSOR] Opening response (first 100): '{response_text[:100]}...'")
            
            # Send opening line with scenario title
            await platform.send_text(user_id, f"*{scenario.title}*\n\n{response_text}")
        else:
            logger.warning(f"[PROCESSOR] ⚠️ Scenario {scenario_id} not found")
            await platform.send_text(user_id, "Scenario not found.")
            await MessageProcessor._send_main_menu_generic(user_id, platform)

    @staticmethod
    async def _send_main_menu_generic(user_id: str, platform: MessagingPlatform):
        """Send the main menu with buttons (platform-agnostic)"""
        logger.info(f"[PROCESSOR] _send_main_menu_generic: user_id={user_id}")
        supabase_service.update_user_mode(user_id, "menu")
        
        await platform.send_menu_buttons(
            user_id,
            "Namaskara! 🙏 Welcome to Chatlingo. How would you like to learn Kannada today?",
            MENU_BUTTONS
        )
        logger.info(f"[PROCESSOR] Main menu sent to user {user_id}")

    @staticmethod
    async def _handle_practice_scenario_flow_generic(user: Any, text: str, platform: MessagingPlatform):
        """Handle conversation in practice scenario mode (platform-agnostic)"""
        user_id = user.phone_number
        logger.info(f"[PROCESSOR] _handle_practice_scenario_flow_generic: user_id={user_id}, text='{text}'")
        
        # Check for exit commands
        if text.lower().strip() in ["exit", "quit", "stop", "menu", "end"]:
            logger.info(f"[PROCESSOR] Exit command detected: '{text}'")
            await platform.send_text(user_id, "Ending practice session. Great job!")
            await MessageProcessor._send_main_menu_generic(user_id, platform)
            return

        scenario_id = user.current_scenario_id
        session_id = getattr(user, 'current_session_id', None)
        logger.info(f"[PROCESSOR] Scenario flow: scenario_id={scenario_id}, session_id={session_id}")
        
        scenario = conversation_engine.get_scenario(scenario_id)
        if not scenario:
            logger.warning(f"[PROCESSOR] ⚠️ Scenario {scenario_id} not found, sending main menu")
            await MessageProcessor._send_main_menu_generic(user_id, platform)
            return

        # User message already saved in _handle_text_message_generic
        # Generate response via engine
        logger.info("[PROCESSOR] Generating scenario response via LLM...")
        response_text = await conversation_engine.process_message(
            user_id, scenario, session_id
        )
        logger.info(f"[PROCESSOR] Scenario response (first 100): '{response_text[:100]}...'")
        
        # Send response
        await platform.send_text(user_id, response_text)

    @staticmethod
    async def _handle_chat_flow_generic(user: Any, text: str, platform: MessagingPlatform):
        """Handle conversation in random chat mode (platform-agnostic)"""
        user_id = user.phone_number
        logger.info(f"[PROCESSOR] _handle_chat_flow_generic: user_id={user_id}, text='{text}'")
        
        # Get history
        history_objs = supabase_service.get_recent_messages(user_id, limit=50)
        history = [{"role": msg.role, "content": msg.content} for msg in history_objs]
        logger.info(f"[PROCESSOR] Chat history: {len(history)} messages loaded")
        
        # Generate response
        logger.info("[PROCESSOR] Calling LLM for chat response...")
        response_text = await llm_service.get_chat_response(history)
        logger.info(f"[PROCESSOR] Chat response (first 100): '{response_text[:100]}...'")
        
        # Send and save
        await platform.send_text(user_id, response_text)
        supabase_service.add_message(user_id, "assistant", response_text, mode="random_chat")
        logger.info("[PROCESSOR] Chat response sent and saved")

# Global instance
message_processor = MessageProcessor()
