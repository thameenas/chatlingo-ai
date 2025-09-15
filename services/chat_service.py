import json
from repositories.chat_repository import ChatRepository
from repositories.user_repository import UserRepository
from services.llm_service import LLMService


class ChatService:
    def __init__(self):
        """Initialize chat service with dependencies"""
        self.user_repository = UserRepository()
        self.chat_repository = ChatRepository()
        self.llm_service = LLMService()
        # Load scenarios
        with open("scenarios.json", "r", encoding="utf-8") as f:
            self.scenarios = json.load(f)

    def process_message(self, phone: str, message: str):

        # Check if user exists, create if not
        user = self.user_repository.get_user_by_phone(phone)
        if not user:
            user = self.user_repository.create_user(phone)

        # Check if message is a command (starts with /)
        if message.startswith('/'):
            return self._handle_command(phone, message, int(user.current_scenario_id))

        # If not a command, process as normal message
        # Store user message in chat history
        chat_history_messages = self.chat_repository.add_message(phone, "user", message)

        # Get formatted chat history
        history_messages = self._get_formatted_chat_history(chat_history_messages)

        # Generate response from LLM
        response = self.llm_service.generate_response(message, history=history_messages)

        # Store LLM response in chat history
        self.chat_repository.add_message(phone, "model", response)
        if user.current_scenario_id == 1:
            return ("Welcome to your Kannada Learning Journey! Please use the /menu command to see all available "
                    "commands.") + response
        return response

    def _handle_command(self, phone: str, command: str, current_scenario_id: int):
        """
        Handle WhatsApp commands
        
        Args:
            phone (str): The user's phone number
            command (str): The command message
            current_scenario_id (int): The user's current scenario ID
            
        Returns:
            str: The response to the command
        """
        # Command: /menu - Show available commands
        if command.lower() == '/menu':
            response = "Available commands:\n\n" + \
                       "/next - Move to next lesson/scenario\n" + \
                       "/day-N - Jump to a specific day/lesson (e.g., /day-5)"
            return response

        # Command: /next - Move to next lesson/scenario
        elif command.lower() == '/next':
            next_scenario_id = min(current_scenario_id + 1, len(self.scenarios))

            # Update user's current scenario
            self.user_repository.update_user_scenario(phone, next_scenario_id)

            # Get scenario introduction from LLM
            scenario_name = self.scenarios[next_scenario_id - 1]
            confirmation = f"Moving to Day {next_scenario_id}: {scenario_name}"

            # Generate LLM response for the new scenario
            llm_response = self._generate_scenario_introduction(phone, next_scenario_id, scenario_name)

            # Return both confirmation and LLM response
            response = f"{confirmation}\n\n{llm_response}"
            return response

        # Command: /day-N - Jump to a specific day/lesson
        elif command.lower().startswith('/day-'):
            try:
                # Extract day number from command
                day_num = int(command[5:])

                # Validate day number
                if 1 <= day_num <= len(self.scenarios):
                    # Update user's current scenario
                    self.user_repository.update_user_scenario(phone, day_num)

                    # Get scenario introduction from LLM
                    scenario_name = self.scenarios[day_num - 1]
                    confirmation = f"Jumping to Day {day_num}: {scenario_name}"

                    # Generate LLM response for the new scenario
                    llm_response = self._generate_scenario_introduction(phone, day_num, scenario_name)

                    # Return both confirmation and LLM response
                    response = f"{confirmation}\n\n{llm_response}"
                else:
                    response = f"Invalid day number. Please choose a day between 1 and {len(self.scenarios)}."
            except ValueError:
                response = "Invalid command format. Use /day-N where N is a day number."

            return response

        # Unknown command
        else:
            response = "Unknown command. Use /menu to see available commands."
            return response

    def _get_formatted_chat_history(self, chat_history_messages, limit: int = 10):
        history_messages = []

        if chat_history_messages:
            # Convert chat history to format expected by LLM service
            for msg in chat_history_messages[-limit:]:
                history_messages.append({
                    "role": msg["role"],
                    "parts": [msg["content"]]
                })

        return history_messages

    def _generate_scenario_introduction(self, phone: str, scenario_id: int, scenario_name: str):
        # Get formatted chat history
        chat_history = self.chat_repository.get_chat_history(phone)
        history_messages = self._get_formatted_chat_history(chat_history, limit=5)

        # Add a system message about the scenario
        system_message = {
            "role": "system",
            "parts": [
                f"The user has moved to Day {scenario_id}: {scenario_name}. Please provide an introduction to this scenario."]
        }
        history_messages.append(system_message)

        # Generate response from LLM with an empty user message
        # This way the LLM responds to the system message, not a user message
        llm_response = self.llm_service.generate_response("", history=history_messages)

        # Store the LLM response in chat history
        self.chat_repository.add_message(phone, "model", llm_response)

        return llm_response
