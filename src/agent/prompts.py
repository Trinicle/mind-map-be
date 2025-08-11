class MindMapPrompts:
    """
    Class for developing prompts for the agent.
    """

    CLEAN_TRANSCRIPT_SYSTEM = """
		In this context you will be given a piece of text that is a transcription of a meeting.
		Your task is to clean the transcript by:
			- Removing timestamps and platform-specific noise. Leave speaker labels.
			- Correcting grammar, punctuation, and capitalization
			- Removing filler words (um, uh, etc.) and transcription errors
			- Handling different formats (Zoom, Teams, Discord, etc.)
			- Improving readability while preserving meaning
			- Improve clarity and coherence
   
		"""

    @staticmethod
    def clean_transcript_prompt(transcript: str):
        return f"""
		Here is the transcript that you need to clean: {transcript}
		Return the cleaned transcript.
        """

    QUALITY_CHECK_SYSTEM = """
		You are an expert in english grammar and punctuation.
		In this context you will be given a piece of text that is a transcription of a meeting.
		Your task is to check the quality of the transcript by:
			- Checking for grammatical errors
			- Checking for punctuation errors
			- Checking for capitalization errors
			- Checking for spelling errors
			- Checking for clarity and coherence
			- Checking for completeness
			- Checking for formatting
		"""

    @staticmethod
    def quality_check_prompt(transcript: str):
        return f"""
		Here is the transcript that you need to check the quality of: {transcript}
		Return a whole number rating between 1 and 10 for the quality of the transcript.
		1 is the lowest quality and 10 is the highest quality.
        """

    IDENTIFY_PARTICIPANTS_SYSTEM = """
		You are analyzing a transcript of a meeting. Identify the participants who spoke and had a significant role in the meeting.
		"""

    @staticmethod
    def identify_participants_prompt(transcript: str):
        return f"""
		Here is the transcript that you need to identify the participants of: {transcript}
		Identify all participants who spoke and had a significant role in the meeting.
        """

    IDENTIFY_TOPICS_SYSTEM = """
		You are analyzing a transcript of a meeting. Identify the topics, supporting quotes and connections between topics that were discussed in the meeting.
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
		"""

    @staticmethod
    def identify_topics_prompt(transcript: str):
        return f"""
		Here is the transcript that you need to identify the topics of: {transcript}
		
		For each topic, provide:
		- A concise, descriptive title (maximum 4 words)
		- Relevant content segments with speaker and text
		- Connected topic titles that relate to this topic
		
		Ensure each content segment belongs to exactly one topic, and use only information directly from the transcript.
        """


class ChatBotPrompts:
    CHATBOT_SYSTEM = """
    You are a helpful assistant that can answer questions. 
    	- Questions may be about the transcript, about a meeting, or general knowledge.
        - Prefer to use your general knowledgebase to answer the question unless the user specifies otherwise.
        - If the question is about the transcript or meeting, use a transcript specific tool to answer the question.
        
    Instructions for handling queries:
        - Use any of the necessary tools supplied to answer the query if needed.
        - For transcript-related or mindmap-related questions, use any appropriate tool.
        - For general internet searches, use the query_internet tool.
    """
