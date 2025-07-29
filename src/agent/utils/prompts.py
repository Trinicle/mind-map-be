from langchain_core.prompts import PromptTemplate

# Prompt for parsing transcript into topics
parse_transcript_prompt = PromptTemplate.from_template(
    """
    You are an AI assistant that organizes meeting transcripts into structured topic clusters.

    First, extract the text from the document at this path: {file_path}

    Then, analyze the extracted text with these goals:
    1. Clear out any noise from the transcript, make it more readable by correcting grammar and punctuation, and removing any non-essential information.
    2. Break the transcript into distinct topics.
    3. Assign each segment of conversation to exactly one topic, only use information from the transcript to assign the conversation to a topic.
    4. Generate a short, descriptive title (maximum 4 words) for each topic.
    5. Identify and describe connections between related topics.

    Requirements:
    - A topic must represent a single idea or theme.
    - A topics title should be unique.
    - A topic title must generalize the content (e.g., "Client Onboarding" not "Client").
    - A conversation cannot belong to multiple topics.
    - Multiple conversations may belong to the same topic.
    - Topics can be connected if they are contextually or logically related, but still distinct.

    RESPONSE FORMAT INSTRUCTIONS:

    When responding, use the following format
    
    {{
        "participants": string[], // A list of the names of the participants that had an impact on the transcript
        "topics": [
            {{
                "title": string, // The title of the topic
                "content": [
                  {{
                    "text": string // The text of the content
                  }},
                  // A list of direct quotes from the transcript supporting the topic
                ]
            }},
        ],
        "connections": [
            {{
                "from_topic": string, // The title of the topic that is connected to the current topic
                "to_topic": string, // The title of the topic that is connected from the current topic
                "reason": string, // A short description of why the two topics are connected
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


def get_transcript_prompt(file_path: str) -> str:
    """Get prompt for parsing transcript into topics."""
    return parse_transcript_prompt.format(file_path=file_path)


def get_followup_questions_prompt(topic_title: str, topic_content: str) -> str:
    """Get prompt for generating followup questions for a specific topic."""
    return followup_questions_prompt.format(
        topic_title=topic_title, topic_content=topic_content
    )


def get_notes_prompt(transcript: str) -> str:
    """Get prompt for generating comprehensive meeting notes."""
    return transcript_notes_prompt.format(transcript=transcript)
