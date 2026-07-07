from state.rag_state import RAGState


def rag_output_node(state: RAGState):

    return {
        "response": state["answer"],

        "rag_metadata": {

            "decision": state["evaluation"]["decision"],

            "reason": state["evaluation"]["reason"],

            "retry_count": state.get("retry_count", 0)

        },

        # This is what actually reaches the parent FinancialState.
        # "response"/"rag_metadata" above aren't part of the FinancialState
        # schema, so they never propagated past this subgraph. agent_outputs
        # is part of both RAGState and FinancialState (same key, same
        # operator.or_ reducer), so this update merges correctly into the
        # parent graph's agent_outputs as soon as the subgraph finishes.
        "agent_outputs": {
            "rag": {
                "analysis": state["answer"]
            }
        }
    }
