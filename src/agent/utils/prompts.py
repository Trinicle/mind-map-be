from langchain_core.prompts import PromptTemplate


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
    You are a helpful assistant that can answer relevant questions about a transcript.
    """

    @staticmethod
    def chatbot_prompt(context: str, query: str):
        if context:
            return f"""
			Here is the relevant transcript id to query off of {context}.
            Given this query {query} and the relevant transcript id, use any of the necessary tools supplied to answer the query.
            Prefer to use the query_transcript tool as it is more likely to be relevant to the query.
            """
        return f"""
		Here is the query: {query}
		Use any of the necessary tools supplied to answer the query. 
        """
