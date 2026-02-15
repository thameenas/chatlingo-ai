"""
Message Processor for Chatlingo AI

WhatsApp transport layer - handles webhook processing and message routing.
Uses ConversationEngine for core conversation logic.
"""

import logging
import traceback
from typing import Any
from app.schemas.whatsapp import WhatsAppWebhook
from app.services.whatsapp_service import whatsapp_service
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
    """Core logic for processing incoming WhatsApp messages"""
    
    async def process_webhook(self, payload: WhatsAppWebhook):
        """
        Entry point for processing a webhook payload.
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
            
            # 3. Handle different message types
            if message.type == "text":
                logger.info(f"[PROCESSOR] ➡️ Routing to _handle_text_message")
                await self._handle_text_message(user, message.text.body)
            elif message.type == "interactive":
                logger.info(f"[PROCESSOR] ➡️ Routing to _handle_interactive_message")
                await self._handle_interactive_message(user, message.interactive)
            else:
                logger.warning(f"[PROCESSOR] ⚠️ Unhandled message type: {message.type}")
                
        except Exception as e:
            logger.error(f"[PROCESSOR] ❌ Error processing webhook: {str(e)}")
            logger.error(f"[PROCESSOR] ❌ Traceback:\n{traceback.format_exc()}")

    async def _handle_text_message(self, user: Any, text: str):
        """Handle incoming text messages based on user state"""
        phone = user.phone_number
        mode = user.current_mode
        logger.info(f"[PROCESSOR] _handle_text_message: phone={phone}, mode={mode}, text='{text}'")
        
        # Save user message to history
        session_id = getattr(user, 'current_session_id', None)
        scenario_id = getattr(user, 'current_scenario_id', None)
        logger.info(f"[PROCESSOR] Saving user message: session_id={session_id}, scenario_id={scenario_id}")
        supabase_service.add_message(phone, "user", text, mode=mode, session_id=session_id, scenario_id=scenario_id)
        
        # Global commands
        if text.lower() in ["menu", "hi", "hello", "start", "restart"]:
            logger.info(f"[PROCESSOR] Global command detected: '{text.lower()}' → sending main menu")
            await self._send_main_menu(phone)
            return

        # Handle based on current mode
        if mode == "menu":
            logger.info(f"[PROCESSOR] Mode is 'menu' → sending main menu")
            await self._send_main_menu(phone)
            
        elif mode == "practice_scenario":
            logger.info(f"[PROCESSOR] Mode is 'practice_scenario' → routing to scenario flow")
            await self._handle_practice_scenario_flow(user, text)
            
        elif mode == "random_chat":
            logger.info(f"[PROCESSOR] Mode is 'random_chat' → routing to chat flow")
            await self._handle_chat_flow(user, text)
            
        else:
            logger.warning(f"[PROCESSOR] ⚠️ Unknown mode '{mode}' → fallback to main menu")
            await self._send_main_menu(phone)

    async def _handle_interactive_message(self, user: Any, interactive: Any):
        """Handle button clicks and list selections"""
        phone = user.phone_number
        logger.info(f"[PROCESSOR] _handle_interactive_message: phone={phone}, interactive_type={interactive.type}")
        
        # Handle Button Replies
        if interactive.type == "button_reply":
            button_id = interactive.button_reply.id
            logger.info(f"[PROCESSOR] Button reply: id='{button_id}', title='{interactive.button_reply.title}'")
            
            if button_id == "practice_scenario_start":
                # Fetch all scenarios
                scenarios = supabase_service.get_all_scenarios()
                
                logger.info(f"[PROCESSOR] Fetched {len(scenarios)} scenarios")
                if not scenarios:
                    logger.warning("[PROCESSOR] ⚠️ No scenarios found in DB")
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
                logger.info("[PROCESSOR] Starting random chat")
                await self._handle_random_chat_start(phone)
                
            elif button_id == "sos_helper":
                logger.info("[PROCESSOR] SOS Helper selected (not implemented)")
                await whatsapp_service.send_text_message(phone, "🚑 SOS Helper coming soon! (This feature is under construction)")
                await self._send_main_menu(phone)
            else:
                logger.warning(f"[PROCESSOR] ⚠️ Unknown button_id: '{button_id}'")

        # Handle List Replies
        elif interactive.type == "list_reply":
            selection_id = interactive.list_reply.id
            logger.info(f"[PROCESSOR] List reply: id='{selection_id}', title='{interactive.list_reply.title}'")
            
            if selection_id.startswith("scenario_"):
                try:
                    scenario_id = int(selection_id.split("_")[1])
                    logger.info(f"[PROCESSOR] Starting scenario {scenario_id}")
                    await self._start_scenario(phone, scenario_id)
                except ValueError:
                    logger.error(f"[PROCESSOR] ❌ Invalid scenario ID format: {selection_id}")
                    await self._send_main_menu(phone)
            else:
                logger.warning(f"[PROCESSOR] ⚠️ Unknown list selection: '{selection_id}'")
        else:
            logger.warning(f"[PROCESSOR] ⚠️ Unknown interactive type: '{interactive.type}'")

    async def _handle_random_chat_start(self, phone: str):
        """Start random chat mode"""
        logger.info(f"[PROCESSOR] _handle_random_chat_start: phone={phone}")
        supabase_service.update_user_mode(phone, "random_chat")
        
        # Generate dynamic opening using LLM instead of static text
        history = [] # Empty history for start
        logger.info("[PROCESSOR] Calling LLM for random chat opening...")
        response_text = await llm_service.get_chat_response(history)
        logger.info(f"[PROCESSOR] LLM response (first 100): '{response_text[:100]}...'")
        
        await whatsapp_service.send_text_message(phone, response_text)
        supabase_service.add_message(phone, "assistant", response_text, mode="random_chat")

    async def _start_scenario(self, phone: str, scenario_id: int):
        """Start a specific practice scenario"""
        logger.info(f"[PROCESSOR] _start_scenario: phone={phone}, scenario_id={scenario_id}")
        scenario = conversation_engine.get_scenario(scenario_id)
        if scenario:
            logger.info(f"[PROCESSOR] Scenario found: '{scenario.title}'")
            # Start scenario session via engine
            session_id = conversation_engine.start_scenario(phone, scenario_id)
            logger.info(f"[PROCESSOR] Session created: {session_id}")
            
            # Generate opening via engine
            logger.info("[PROCESSOR] Generating scenario opening via LLM...")
            response_text = await conversation_engine.generate_opening(phone, scenario, session_id)
            logger.info(f"[PROCESSOR] Opening response (first 100): '{response_text[:100]}...'")
            
            # Send opening line (WhatsApp-specific)
            await whatsapp_service.send_text_message(phone, f"*{scenario.title}*\n\n{response_text}")
        else:
            logger.warning(f"[PROCESSOR] ⚠️ Scenario {scenario_id} not found")
            await whatsapp_service.send_text_message(phone, "Scenario not found.")
            await self._send_main_menu(phone)

    async def _send_main_menu(self, phone: str):
        """Send the main menu with buttons"""
        logger.info(f"[PROCESSOR] _send_main_menu: phone={phone}")
        supabase_service.update_user_mode(phone, "menu")
        
        result = await whatsapp_service.send_interactive_buttons(
            phone,
            "Namaskara! 🙏 Welcome to Chatlingo. How would you like to learn Kannada today?",
            MENU_BUTTONS
        )
        logger.info(f"[PROCESSOR] Main menu sent: success={result}")

    async def _handle_practice_scenario_flow(self, user: Any, text: str):
        """Handle conversation in practice scenario mode"""
        phone = user.phone_number
        logger.info(f"[PROCESSOR] _handle_practice_scenario_flow: phone={phone}, text='{text}'")
        
        # Check for exit commands
        if text.lower().strip() in ["exit", "quit", "stop", "menu", "end"]:
            logger.info(f"[PROCESSOR] Exit command detected: '{text}'")
            await whatsapp_service.send_text_message(phone, "Ending practice session. Great job!")
            await self._send_main_menu(phone)
            return

        scenario_id = user.current_scenario_id
        session_id = getattr(user, 'current_session_id', None)
        logger.info(f"[PROCESSOR] Scenario flow: scenario_id={scenario_id}, session_id={session_id}")
        
        scenario = conversation_engine.get_scenario(scenario_id)
        if not scenario:
            logger.warning(f"[PROCESSOR] ⚠️ Scenario {scenario_id} not found, sending main menu")
            await self._send_main_menu(phone)
            return

        # User message already saved in _handle_text_message
        # Generate response via engine
        logger.info("[PROCESSOR] Generating scenario response via LLM...")
        response_text = await conversation_engine.process_message(
            phone, scenario, session_id
        )
        logger.info(f"[PROCESSOR] Scenario response (first 100): '{response_text[:100]}...'")
        
        # Send response (WhatsApp-specific)
        await whatsapp_service.send_text_message(phone, response_text)

    async def _handle_chat_flow(self, user: Any, text: str):
        """Handle conversation in random chat mode"""
        phone = user.phone_number
        logger.info(f"[PROCESSOR] _handle_chat_flow: phone={phone}, text='{text}'")
        
        # Get history
        history_objs = supabase_service.get_recent_messages(phone, limit=50)
        history = [{"role": msg.role, "content": msg.content} for msg in history_objs]
        logger.info(f"[PROCESSOR] Chat history: {len(history)} messages loaded")
        
        # Generate response
        logger.info("[PROCESSOR] Calling LLM for chat response...")
        response_text = await llm_service.get_chat_response(history)
        logger.info(f"[PROCESSOR] Chat response (first 100): '{response_text[:100]}...'")
        
        # Send and save
        await whatsapp_service.send_text_message(phone, response_text)
        supabase_service.add_message(phone, "assistant", response_text, mode="random_chat")
        logger.info("[PROCESSOR] Chat response sent and saved")

# Global instance
message_processor = MessageProcessor()