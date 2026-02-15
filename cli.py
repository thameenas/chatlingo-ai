#!/usr/bin/env python3
"""
CLI Interface for Chatlingo AI - Practice Scenarios

Reuses ConversationEngine for core logic. Input/output via terminal.

Usage:
    Interactive mode:
        python cli.py
    
    Non-interactive mode (for LLM testing):
        python cli.py --list                      # List scenarios
        python cli.py --start 1                   # Start scenario 1, returns session_id
        python cli.py --session <id> --message "hello"  # Send message
        python cli.py --session <id> --exit       # End session
"""

import asyncio
import argparse
import json
import os

from app.services.conversation_engine import conversation_engine
from app.services import supabase_service

# File to persist session info for non-interactive mode
SESSION_FILE = "/tmp/chatlingo_session.json"


def save_session(data: dict):
    """Save session data to temp file"""
    with open(SESSION_FILE, "w") as f:
        json.dump(data, f)


def load_session() -> dict:
    """Load session data from temp file"""
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "r") as f:
            return json.load(f)
    return {}


def clear_session():
    """Clear session file"""
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)


async def list_scenarios():
    """List available scenarios"""
    scenarios = conversation_engine.get_all_scenarios()
    if not scenarios:
        print("No scenarios found.")
        return
    
    print("\n📋 Available Scenarios:")
    for s in scenarios:
        print(f"  {s.id}. {s.title} - {s.situation_seed}")
    print("\nUse --start <id> to begin a scenario")


async def start_scenario(scenario_id: int, phone: str):
    """Start a new scenario session"""
    scenario = conversation_engine.get_scenario(scenario_id)
    if not scenario:
        print(f"❌ Scenario {scenario_id} not found")
        return
    
    # Ensure user exists
    supabase_service.get_or_create_user(phone)
    
    # Start session
    session_id = conversation_engine.start_scenario(phone, scenario.id)
    
    # Generate opening
    opening = await conversation_engine.generate_opening(phone, scenario, session_id)
    
    # Save session info
    save_session({
        "session_id": session_id,
        "scenario_id": scenario.id,
        "scenario_title": scenario.title,
        "bot_persona": scenario.bot_persona,
        "phone": phone
    })
    
    print(f"\n🎪 Starting: {scenario.title}")
    print(f"📍 {scenario.situation_seed}")
    print("-" * 40)
    print(f"\n🤖 {scenario.bot_persona}:\n{opening}")
    print("\n" + "-" * 40)
    print("💡 Reply with: --message \"your message\"")
    print("🚪 Exit with: --exit")


async def send_message(message: str, phone: str):
    """Send a message in current session"""
    session = load_session()
    if not session:
        print("❌ No active session. Use --start <scenario_id> first.")
        return
    
    scenario = conversation_engine.get_scenario(session["scenario_id"])
    if not scenario:
        print("❌ Scenario not found")
        return
    
    session_id = session["session_id"]
    
    # Save user message
    conversation_engine.save_user_message(phone, message, scenario.id, session_id)
    
    # Generate response
    response = await conversation_engine.process_message(phone, scenario, session_id)
    
    print(f"\n👤 You: {message}")
    print("-" * 40)
    print(f"\n🤖 {scenario.bot_persona}:\n{response}")
    print("\n" + "-" * 40)


async def end_session():
    """End current session"""
    session = load_session()
    if session:
        print(f"\n👋 Ending session for: {session.get('scenario_title', 'Unknown')}")
        clear_session()
        print("✅ Session ended. Hogibarti!")
    else:
        print("No active session to end.")


async def interactive_mode(phone: str):
    """Original interactive mode"""
    print("\n🎭 CHATLINGO - Practice Scenario CLI")
    print("-" * 40)
    
    # Fetch scenarios from database
    scenarios = conversation_engine.get_all_scenarios()
    if not scenarios:
        print("No scenarios found in database.")
        return
    
    # Display scenarios
    print("\nAvailable Scenarios:")
    for s in scenarios:
        print(f"  {s.id}. {s.title}")
    
    # Select scenario
    try:
        choice = int(input("\nEnter scenario number: "))
        scenario = conversation_engine.get_scenario(choice)
        if not scenario:
            print("Invalid scenario")
            return
    except ValueError:
        print("Invalid input")
        return
    
    print(f"\n🎪 Starting: {scenario.title}")
    print(f"📍 {scenario.situation_seed}")
    print("-" * 40)
    print("Type 'exit' to quit\n")
    
    # Ensure user exists in DB (same as WhatsApp flow)
    supabase_service.get_or_create_user(phone)
    
    # Start scenario session
    session_id = conversation_engine.start_scenario(phone, scenario.id)
    
    # Generate opening
    opening = await conversation_engine.generate_opening(phone, scenario, session_id)
    print(f"🤖 {scenario.bot_persona}: {opening}\n")
    
    # Conversation loop
    while True:
        user_input = input("👤 You: ").strip()
        if not user_input or user_input.lower() == "exit":
            print("\n👋 Hogibarti!")
            break
        
        # Save user message first
        conversation_engine.save_user_message(phone, user_input, scenario.id, session_id)
        
        # Generate response
        response = await conversation_engine.process_message(
            phone, scenario, session_id
        )
        print(f"\n🤖 {scenario.bot_persona}: {response}\n")


async def main():
    parser = argparse.ArgumentParser(description="Chatlingo CLI")
    parser.add_argument(
        "--phone",
        default="cli_test_user",
        help="Phone number/identifier for DB tracking"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available scenarios"
    )
    parser.add_argument(
        "--start",
        type=int,
        metavar="SCENARIO_ID",
        help="Start a scenario by ID"
    )
    parser.add_argument(
        "--message",
        type=str,
        metavar="TEXT",
        help="Send a message in current session"
    )
    parser.add_argument(
        "--exit",
        action="store_true",
        dest="end_session",
        help="End current session"
    )
    
    args = parser.parse_args()
    
    # Use saved phone from session if exists
    session = load_session()
    phone = session.get("phone", args.phone)
    
    # Non-interactive commands
    if args.list:
        await list_scenarios()
    elif args.start:
        await start_scenario(args.start, args.phone)
    elif args.message:
        await send_message(args.message, phone)
    elif args.end_session:
        await end_session()
    else:
        # Default: interactive mode
        await interactive_mode(args.phone)


if __name__ == "__main__":
    asyncio.run(main())
