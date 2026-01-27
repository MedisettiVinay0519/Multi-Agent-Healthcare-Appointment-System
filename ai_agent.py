import re
import os
import json
from dotenv import load_dotenv
from typing import Literal, Any, List
from typing_extensions import TypedDict, Annotated

from langgraph.types import Command
from langgraph.graph import START, END, StateGraph
from langgraph.graph.message import add_messages

from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq

from tools import (
    check_availability_by_doctor,
    check_availability_by_specialization,
    set_appointment,
    cancel_appointment,
    reschedule_appointment,
)

# -------------------------------------------------
# ENV & MODEL
# -------------------------------------------------
load_dotenv()

llm_model = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY"),
)

# -------------------------------------------------
# SUPERVISOR PROMPT
# -------------------------------------------------
system_prompt = """
You are a supervisor managing hospital appointment agents.

RULES:
- Decide which worker should handle the request
- DO NOT call tools
- DO NOT browse or search
- Respond ONLY in valid JSON

JSON FORMAT:
{
  "next": "information_node" | "booking_node" | "FINISH",
  "reasoning": "short reason"
}
"""

# -------------------------------------------------
# STATE
# -------------------------------------------------
class AgentState(TypedDict):
    messages: Annotated[List[Any], add_messages]
    id_number: int
    query: str
    current_reasoning: str

# -------------------------------------------------
# AGENT
# -------------------------------------------------
class DoctorAppointmentAgent:

    # ---------------- SUPERVISOR ----------------
    def supervisor_node(
        self, state: AgentState
    ) -> Command[Literal["information_node", "booking_node", "__end__"]]:

        # Stop loop if last message already AI
        if state["messages"] and isinstance(state["messages"][-1], AIMessage):
            return Command(goto=END)

        user_msg = state["messages"][-1].content.lower()

        if any(w in user_msg for w in ["available", "availability"]):
            goto = "information_node"
        else:
            goto = "booking_node"

        return Command(
            goto=goto,
            update={"query": state["messages"][-1].content},
        )

    # ---------------- INFORMATION NODE ----------------
    def information_node(
        self, state: AgentState
    ) -> Command[Literal["supervisor"]]:

        query = state["messages"][-1].content.lower()

        extract_prompt = f"""
Extract intent and return ONLY JSON.

Schema:
{{
  "type": "doctor" | "specialization",
  "doctor_name": string | null,
  "specialization": string | null,
  "date": "DD-MM-YYYY"
}}

Query: "{query}"
"""

        raw = llm_model.invoke(extract_prompt).content

        try:
            intent = json.loads(raw)
        except Exception:
            intent = {}

        try:
            if intent.get("type") == "doctor":
                result = check_availability_by_doctor.invoke(intent)
            elif intent.get("type") == "specialization":
                result = check_availability_by_specialization.invoke(intent)
            else:
                result = "No availability found."
        except Exception:
            result = "No availability found in hospital records."

        return Command(
            goto="supervisor",
            update={
                "messages": state["messages"]
                + [AIMessage(content=result, name="information_node")]
            },
        )

    # ---------------- BOOKING NODE ----------------
    def booking_node(
        self, state: AgentState
    ) -> Command[Literal["supervisor"]]:

        # Keep context small
        state["messages"] = state["messages"][-4:]

        # Extract last human message safely
        last_user_msg = ""
        for msg in reversed(state["messages"]):
            if isinstance(msg, HumanMessage):
                last_user_msg = msg.content
                break

        # Guard: date + time required
        if not re.search(r"\d{2}-\d{2}-\d{4}\s+\d{2}:\d{2}", last_user_msg):
            return Command(
                goto="supervisor",
                update={
                    "messages": state["messages"]
                    + [
                        AIMessage(
                            content=(
                                "Please provide the appointment date and time "
                                "in **DD-MM-YYYY HH:MM** format."
                            ),
                            name="booking_node",
                        )
                    ]
                },
            )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    f"""
You are a booking agent.

RULES:
- User ID is FIXED: {state["id_number"]}
- Use ONLY provided tools
- NEVER invent values
- desired_date MUST be DD-MM-YYYY HH:MM
"""
                ),
                ("placeholder", "{messages}"),
            ]
        )

        agent = create_react_agent(
            model=llm_model,
            tools=[set_appointment, cancel_appointment, reschedule_appointment],
            prompt=prompt,
        )

        result = agent.invoke(state)

        return Command(
            goto="supervisor",
            update={
                "messages": state["messages"]
                + [
                    AIMessage(
                        content=result["messages"][-1].content,
                        name="booking_node",
                    )
                ]
            },
        )

    # ---------------- WORKFLOW ----------------
    def workflow(self):
        graph = StateGraph(AgentState)

        graph.add_node("supervisor", self.supervisor_node)
        graph.add_node("information_node", self.information_node)
        graph.add_node("booking_node", self.booking_node)

        graph.add_edge(START, "supervisor")
        graph.add_edge("information_node", "supervisor")
        graph.add_edge("booking_node", "supervisor")

        return graph.compile()
