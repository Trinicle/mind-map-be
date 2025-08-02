import datetime
from langchain_core.prompts import PromptTemplate

# Prompt for analyzing transcript content and creating topic structure
parse_transcript_prompt = PromptTemplate.from_template(
    """
    You are an AI assistant that analyzes meeting transcripts to extract meaningful topics and insights.
    
    Context:
    - Title: {title}
    - Description: {description} 
    - Date: {date}
    - File path of text to extract: {file_path}
    - auth_token: {auth_token}

    Your task is to analyze the transcript:
    1. Extract the text from the file at this path: {file_path}
    2. Clean the transcript by:
       - Removing timestamps, speaker labels, and platform-specific noise
       - Correcting grammar, punctuation, and capitalization
       - Removing filler words (um, uh, etc.) and transcription errors
       - Handling different formats (Zoom, Teams, Discord, etc.)
       - Improving readability while preserving meaning
    3. Insert the full transcript after cleaning into the database using the auth token: {auth_token}
       - The transcript id is the id of the inserted transcript
       - You must use a tool to insert the transcript into the database
    4. Identify the participants who spoke in the meeting
    5. Organize the content into distinct, meaningful topics

    For topic organization:
    - Each topic should represent a single, coherent theme or discussion point
    - Create concise titles (maximum 4 words) that capture the essence of each topic
    - Extract relevant content segments that support each topic
    - Identify logical connections between related topics

    Quality requirements:
    - Topic titles should be unique and descriptive (e.g., "Client Onboarding Process" not just "Client")
    - Each content segment should belong to exactly one topic
    - Topics can be connected if they're contextually related but still distinct
    - Use only information directly from the transcript

    Return your analysis in this JSON format:
    {{
        "transcript_id": string, // Unique identifier for the transcript outputted from the inserting the transcript into the database
        "participants": string[], // Names of people who participated in the meeting
        "topics": [
            {{
                "title": string, // Concise, descriptive topic title
                "content": [
                    {{
                        "speaker": string, // Name of the speaker
                        "text": string // Direct quote or paraphrased content from transcript
                    }}
                ]
            }}
        ],
        "connections": [
            {{
                "from_topic": string, // Source topic title
                "to_topic": string, // Connected topic title  
                "reason": string // Brief explanation of the connection
            }}
        ]
    }}
    """
)

# Prompt for generating followup questions for a specific topic
followup_questions_prompt = PromptTemplate.from_template(
    """
    You are an AI assistant helping to generate insightful followup questions for a meeting topic.

    Topic: {topic_title}
    Content: {topic_content}

    Generate 3-5 followup questions that would help:
    1. Clarify any ambiguous points
    2. Explore potential implications
    3. Identify next steps or action items
    4. Uncover related issues or concerns

    Format your response as a JSON list:
    {{
      "followup_questions": [
        {{
          "question": "What specific metrics will be used to measure success?",
          "reason": "Helps establish concrete evaluation criteria"
        }},
        // ... more questions
      ]
    }}
    """
)

# Prompt for generating comprehensive notes
transcript_notes_prompt = PromptTemplate.from_template(
    """
    You are an AI assistant that creates comprehensive meeting notes.

    First, extract the text from the document at this path: {transcript}

    Then, create a structured summary that includes:
    1. Key Points and Decisions
    2. Action Items and Owners
    3. Important Dates/Deadlines
    4. Open Questions/Issues
    5. Next Steps

    Format your response as JSON:
    {{
      "summary": "Brief 2-3 sentence overview of the meeting",
      "key_points": [
        {{
          "point": "Decision to launch new feature in Q2",
          "context": "Based on user feedback and resource availability"
        }}
      ],
      "action_items": [
        {{
          "task": "Create project timeline",
          "owner": "Project Manager",
          "deadline": "Next week"
        }}
      ],
      "dates": [
        {{
          "event": "Feature Launch",
          "date": "Q2 2024",
          "details": "Pending final approval"
        }}
      ],
      "open_questions": [
        {{
          "question": "Resource allocation for Q3",
          "context": "Needs discussion with department heads"
        }}
      ],
      "next_steps": [
        "Schedule follow-up meeting with stakeholders",
        "Distribute draft timeline for review"
      ]
    }}
    """
)


def get_transcript_prompt(
    file_path: str, title: str, description: str, date: datetime, auth_token: str
) -> str:
    """Get prompt for analyzing transcript content and creating topic structure."""
    return parse_transcript_prompt.format(
        file_path=file_path,
        title=title,
        description=description,
        date=date,
        auth_token=auth_token,
    )


def get_followup_questions_prompt(topic_title: str, topic_content: str) -> str:
    """Get prompt for generating followup questions for a specific topic."""
    return followup_questions_prompt.format(
        topic_title=topic_title, topic_content=topic_content
    )


def get_notes_prompt(transcript: str) -> str:
    """Get prompt for generating comprehensive meeting notes."""
    return transcript_notes_prompt.format(transcript=transcript)
