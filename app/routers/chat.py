from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from typing import List
import json
import time
from ..models.chat import ChatMessageCreate, ChatMessageResponse, ChatMessage
from ..models.user import UserResponse
from ..dependencies import get_current_user
from ..database import get_database
from bson import ObjectId
from datetime import datetime
import os
from ..config import settings

from openai import OpenAI
client = OpenAI(api_key=settings.openai_api_key)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/send", response_model=ChatMessageResponse)
async def send_message(
    message_data: ChatMessageCreate,
    current_user: UserResponse = Depends(get_current_user),
    db = Depends(get_database)
):
    """Send a chat message and get AI response"""
    
    # Create user message
    user_message = {
        "user_id": current_user.id,
        "message": message_data.message,
        "is_user_message": True,
        "created_at": datetime.utcnow()
    }
    
    # Insert user message
    result = await db.chat_messages.insert_one(user_message)
    user_message["_id"] = str(result.inserted_id)
    
    # Fetch last 10 messages for context
    cursor = db.chat_messages.find(
        {"user_id": current_user.id}
    ).sort("created_at", -1).limit(10)
    
    chat_history = await cursor.to_list(length=10)
    
    # Generate AI response with chat history
    ai_response = generate_ai_response(message_data.message, current_user, chat_history)
    
    # Create AI message
    ai_message = {
        "user_id": current_user.id,
        "message": ai_response,
        "is_user_message": False,
        "created_at": datetime.utcnow()
    }
    
    # Insert AI message
    await db.chat_messages.update_one(
        {"_id": ObjectId(user_message["_id"])},
        {"$set": {"response": ai_response}}
    )
    
    return ChatMessageResponse(
        id=str(user_message["_id"]),
        message=ai_response,
        response=ai_response,
        is_user_message=False,
        created_at=ai_message["created_at"]
    )


@router.post("/send-stream")
async def send_message_stream(
    message_data: ChatMessageCreate,
    current_user: UserResponse = Depends(get_current_user),
    db = Depends(get_database)
):
    """Send a chat message and get AI response via streaming"""
    
    # Create user message
    user_message = {
        "user_id": current_user.id,
        "message": message_data.message,
        "is_user_message": True,
        "created_at": datetime.utcnow()
    }
    
    # Insert user message
    result = await db.chat_messages.insert_one(user_message)
    user_message["_id"] = str(result.inserted_id)
    
    # Fetch last 10 messages for context
    cursor = db.chat_messages.find(
        {"user_id": current_user.id, "response": {"$exists": True}}
    ).sort("created_at", -1).limit(10)
    
    chat_history = await cursor.to_list(length=10)
    
    async def generate_stream():
        """Generate streaming response"""
        try:
            # Generate streaming AI response
            full_response = ""
            async for chunk in generate_ai_response_stream(message_data.message, current_user, chat_history):
                full_response += chunk
                # time.sleep(1)
                yield f"data: {json.dumps({'chunk': chunk, 'message_id': str(user_message['_id'])})}\n\n"
            
            # Save the complete response to database
            await db.chat_messages.update_one(
                {"_id": ObjectId(user_message["_id"])},
                {"$set": {"response": full_response}}
            )
            
            # Send end signal
            yield f"data: {json.dumps({'done': True, 'message_id': str(user_message['_id'])})}\n\n"
            
        except Exception as e:
            error_data = {"error": str(e), "message_id": str(user_message["_id"])}
            yield f"data: {json.dumps(error_data)}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
        }
    )


@router.get("/messages", response_model=List[ChatMessageResponse])
async def get_chat_history(
    current_user: UserResponse = Depends(get_current_user),
    limit: int = 50,
    db = Depends(get_database)
):
    """Get chat history for the current user"""
    
    cursor = db.chat_messages.find(
        {"user_id": current_user.id, "response": {"$exists": True}}
    ).sort("created_at", -1).limit(limit)
    
    messages = await cursor.to_list(length=limit)
    
    # Convert ObjectId to string and reverse to show oldest first
    chat_messages = []
    for msg in reversed(messages):
        chat_messages.append(ChatMessageResponse(
            id=str(msg["_id"]),
            response=msg["response"],
            message=msg["message"],
            is_user_message=msg["is_user_message"],
            created_at=msg["created_at"]
        ))
    
    return chat_messages


def generate_ai_response(user_message: str, user: UserResponse, chat_history: list = None) -> str:
    """Generate AI response based on user message, user profile, and chat history"""
    
    # Format birth information as strings
    name = user.name
    birthdate_str = user.birthdate.strftime("%B %d, %Y") if user.birthdate else "Not provided"
    birthtime_str = user.birthtime if user.birthtime else "Not provided"
    birth_location_str = user.birth_location if user.birth_location else "Not provided"

    # Format chat history for context
    chat_context = ""
    if chat_history:
        # Reverse to show oldest first, then take last 10
        reversed_history = list(reversed(chat_history))[-10:]
        chat_context = "\n\n### Previous Conversation Context:\n"
        for msg in reversed_history:
            role = "User" if msg["is_user_message"] else "Astrologer"
            chat_context += f"{role}: {msg['message']}\n"

    prompt = f"""
        You are an expert astrologer with deep knowledge of Vedic and Western astrology. Your role is to interact with the user and provide accurate astrological insights.

        ### Workflow:

        1. **Greeting Messages**

        * If the user sends a simple greeting (e.g., "Hi", "Hello", "Good morning"), reply politely with a short warm greeting.
        * Do not ask follow-up questions in this case.

        2. **Horoscope Requests (Daily/Weekly/Monthly/Yearly)**

        * If the user asks for horoscope, daily horoscope, weekly horoscope, monthly horoscope, or yearly horoscope, provide a structured response in the following format:

        ```
        🌟 [ZODIAC_SIGN] HOROSCOPE - [PERIOD]

         Prediction Period: [Start Date] - [End Date] [Year]

        ⭐ RATINGS:
        • Health: [X]/5 ⭐
        • Travel: [X]/5 ⭐
        • Work: [X]/5 ⭐
        • Luck: [X]/5 ⭐
        • Relationship: [X]/5 ⭐
        • Finance: [X]/5 ⭐
        • Study: [X]/5 ⭐

        🍀 LUCKY ELEMENTS:
        • Lucky Number: [Number]
        • Lucky Color: [Color]

        📖 PREDICTION:
        [Detailed astrological prediction based on current planetary positions and user's birth chart]

        💡 RECOMMENDATIONS:
        [Specific recommendations based on astrological analysis]
        ```

        * Calculate the zodiac sign based on the user's birth date
        * Provide realistic ratings (1-5 stars) based on planetary positions
        * Include specific lucky numbers and colors based on astrological calculations
        * Give detailed predictions and practical recommendations

        3. **Understand the User Input**

        * If the user's message is an astrology-related query, analyze it carefully.
        * If **birth date, birth time, and birth location are provided**, immediately proceed with a detailed astrological interpretation.
        * If any of these three details are missing, ask clear and precise follow-up questions to collect the missing information.
        * If the user's question is very broad (e.g., "tell me about my future"), politely ask them to clarify the specific concern (career, marriage, relationships, finances, etc.).

        4. **Decision Logic**

        * If complete birth details and context are available, generate a **focused and accurate astrological interpretation**.
        * If essential details are missing, do **not** attempt a partial answer — ask for the exact missing details only.
        * Do not ask redundant or unnecessary clarifications once all three essentials (birth date, birth time, birth location) are provided.

        5. **Scope Limitation**

        * Stay strictly within the domain of astrology.
        * ❌ Do not provide medical, legal, psychological, or other non-astrological advice.
        * ❌ Do not disclose, repeat, or echo the user's personal information (birth details) in the response.

         **Goal:** Help the user gain clarity about their situation using expert astrological analysis based on their provided birth and situational data.

        ---

        **Critical Rules**

        * ❌ Do not answer questions outside astrology.
        * ❌ Do not provide medical, legal, psychological, or unrelated advice.
        * ❌ Do not disclose or repeat the user's personal information (birth date, time, or location) in the final response.
        * ✅ Always keep responses respectful, precise, and astrologically insightful.
        * ✅ For horoscope requests, always use the structured format above.

        ---

        **User Input Variables:**

        * User Message: {user_message}
        * User Name: {name}
        * User Birth Date: {birthdate_str}
        * User Birth Time: {birthtime_str}
        * User Birth Location: {birth_location_str}

        {chat_context}
    """

    response = client.responses.create(
        model="gpt-5",
        input=prompt
    )

    return response.output_text


async def generate_ai_response_stream(user_message: str, user: UserResponse, chat_history: list = None):
    """Generate streaming AI response based on user message, user profile, and chat history"""
    
    # Format birth information as strings
    name = user.name
    birthdate_str = user.birthdate.strftime("%B %d, %Y") if user.birthdate else "Not provided"
    birthtime_str = user.birthtime if user.birthtime else "Not provided"
    birth_location_str = user.birth_location if user.birth_location else "Not provided"

    # Format chat history for context
    chat_context = ""
    if chat_history:
        # Reverse to show oldest first, then take last 10
        reversed_history = list(reversed(chat_history))[-10:]
        chat_context = "\n\n### Previous Conversation Context:\n"
        for msg in reversed_history:
            role = "User" if msg["is_user_message"] else "Astrologer"
            chat_context += f"{role}: {msg['message']}\n"

    prompt = f"""
        You are an expert astrologer with deep knowledge of Vedic and Western astrology. Your role is to interact with the user and provide accurate astrological insights.

        ### Workflow:

        1. **Greeting Messages**

        * If the user sends a simple greeting (e.g., "Hi", "Hello", "Good morning"), reply politely with a short warm greeting.
        * Do not ask follow-up questions in this case.

        2. **Horoscope Requests (Daily/Weekly/Monthly/Yearly)**

        * If the user asks for horoscope, daily horoscope, weekly horoscope, monthly horoscope, or yearly horoscope, provide a structured response in the following format:

        ```
        🌟 [ZODIAC_SIGN] HOROSCOPE - [PERIOD]

         Prediction Period: [Start Date] - [End Date] [Year]

        ⭐ RATINGS:
        • Health: [X]/5 ⭐
        • Travel: [X]/5 ⭐
        • Work: [X]/5 ⭐
        • Luck: [X]/5 ⭐
        • Relationship: [X]/5 ⭐
        • Finance: [X]/5 ⭐
        • Study: [X]/5 ⭐

        🍀 LUCKY ELEMENTS:
        • Lucky Number: [Number]
        • Lucky Color: [Color]

        📖 PREDICTION:
        [Detailed astrological prediction based on current planetary positions and user's birth chart]

        💡 RECOMMENDATIONS:
        [Specific recommendations based on astrological analysis]
        ```

        * Calculate the zodiac sign based on the user's birth date
        * Provide realistic ratings (1-5 stars) based on planetary positions
        * Include specific lucky numbers and colors based on astrological calculations
        * Give detailed predictions and practical recommendations

        3. **Understand the User Input**

        * If the user's message is an astrology-related query, analyze it carefully.
        * If **birth date, birth time, and birth location are provided**, immediately proceed with a detailed astrological interpretation.
        * If any of these three details are missing, ask clear and precise follow-up questions to collect the missing information.
        * If the user's question is very broad (e.g., "tell me about my future"), politely ask them to clarify the specific concern (career, marriage, relationships, finances, etc.).

        4. **Decision Logic**

        * If complete birth details and context are available, generate a **focused and accurate astrological interpretation**.
        * If essential details are missing, do **not** attempt a partial answer — ask for the exact missing details only.
        * Do not ask redundant or unnecessary clarifications once all three essentials (birth date, birth time, birth location) are provided.

        5. **Scope Limitation**

        * Stay strictly within the domain of astrology.
        * ❌ Do not provide medical, legal, psychological, or other non-astrological advice.
        * ❌ Do not disclose, repeat, or echo the user's personal information (birth details) in the response.

         **Goal:** Help the user gain clarity about their situation using expert astrological analysis based on their provided birth and situational data.

        ---

        **Critical Rules**

        * ❌ Do not answer questions outside astrology.
        * ❌ Do not provide medical, legal, psychological, or unrelated advice.
        * ❌ Do not disclose or repeat the user's personal information (birth date, time, or location) in the final response.
        * ✅ Always keep responses respectful, precise, and astrologically insightful.
        * ✅ For horoscope requests, always use the structured format above.
        * ✅ Do not use user details if user is asking about general astrology.

        ---

        **User Input Variables:**

        * User Name: {name}
        * User Birth Date: {birthdate_str}
        * User Birth Time: {birthtime_str}
        * User Birth Location: {birth_location_str}
        * Today's Date: {datetime.now().strftime("%B %d, %Y")}
    """
    
    messages = [{"role": "system", "content": prompt}]
    if chat_history:
        # Reverse to show oldest first, then take last 10
        reversed_history = list(reversed(chat_history))[-5:]
        for msg in reversed_history:
            messages.append({"role": "user", "content": msg['message']})
            messages.append({"role": "assistant", "content": msg['response']})
    messages.append({"role": "user", "content": user_message})
    try:
        stream = client.chat.completions.create(
            model="gpt-4.1",
            messages=messages,
            stream=True,
            temperature=0.1,
            max_tokens=1000,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None,
            n=1,
        )
        
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content
                
    except Exception as e:
        print(f"Error in streaming response: {e}")
        yield f"Sorry, I encountered an error: {str(e)}"
