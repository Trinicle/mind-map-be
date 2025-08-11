from langgraph.graph import StateGraph, START, END

from src.agent.nodes import (
    load_transcript_node,
    clean_transcript_node,
    quality_score_condition_node,
    quality_check_node,
    identify_participants_node,
    identify_topics_node,
    split_transcript_node,
)
from src.agent.state import TranscriptState


transcript_builder = StateGraph(TranscriptState)

transcript_builder.add_node("load_transcript", load_transcript_node)
transcript_builder.add_node("clean_transcript", clean_transcript_node)
transcript_builder.add_node("quality_check", quality_check_node)
transcript_builder.add_node("split_transcript", split_transcript_node)
transcript_builder.add_node("identify_participants", identify_participants_node)
transcript_builder.add_node("identify_topics", identify_topics_node)

transcript_builder.add_edge(START, "load_transcript")
transcript_builder.add_edge("load_transcript", "clean_transcript")
transcript_builder.add_edge("clean_transcript", "quality_check")
transcript_builder.add_edge("split_transcript", "identify_participants")
transcript_builder.add_edge("split_transcript", "identify_topics")

transcript_builder.add_edge("identify_participants", END)
transcript_builder.add_edge("identify_topics", END)

transcript_builder.add_conditional_edges(
    "quality_check",
    quality_score_condition_node,
    {
        "reclean": "clean_transcript",
        "pass": "split_transcript",
    },
)

transcript_graph = transcript_builder.compile()
