from state.financial_state import FinancialState


def guard_router(state: FinancialState):

    if state["blocked"]:

        return "blocked"

    return "supervisor"
